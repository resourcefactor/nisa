import frappe
from frappe import _
from frappe.utils import getdate, add_days, today


@frappe.whitelist()
def get_events(start, end, filters=None):
	import json
	from frappe.desk.calendar import get_event_conditions

	# Normalise filters: JSON string → Python list
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except (ValueError, TypeError):
			filters = []
	filters = filters or []

	# Intersect the delivery_date "Between" filter range with the passed start/end
	# so the SQL is scoped to exactly what was requested (calendar view or print range).
	for f in filters:
		if len(f) >= 4:
			_doctype, field, op, val = f[0], f[1], f[2], f[3]
		elif len(f) == 3:
			field, op, val = f[0], f[1], f[2]
		else:
			continue
		if field == "delivery_date" and op.lower() == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
			filter_start = getdate(val[0])
			filter_end = getdate(val[1])
			view_start = getdate(start)
			view_end = getdate(end)
			effective_start = max(filter_start, view_start)
			effective_end = min(filter_end, view_end)
			if effective_start <= effective_end:
				start, end = str(effective_start), str(effective_end)
			break

	conditions = get_event_conditions("Sales Order", filters)

	data = frappe.db.sql(
		f"""
		select
			distinct `tabSales Order`.name, `tabSales Order`.customer_name, `tabSales Order`.status,
			`tabSales Order`.delivery_status, `tabSales Order`.billing_status,
			`tabSales Order Item`.delivery_date
		from
			`tabSales Order`, `tabSales Order Item`
		where `tabSales Order`.name = `tabSales Order Item`.parent
			and `tabSales Order`.skip_delivery_note = 0
			and (ifnull(`tabSales Order Item`.delivery_date, '0000-00-00') != '0000-00-00')
			and (`tabSales Order Item`.delivery_date between %(start)s and %(end)s)
			and `tabSales Order`.docstatus < 2
			{conditions}
		""",
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0, "convertToUserTz": 0},
	)

	for d in data:
		d["custom_calendar_title"] = f"{d.name} - {d.customer_name}"
	return data


def validate(doc, method=None):
	_validate_delivery_date(doc)
	_validate_max_deliveries_per_date(doc)
	_link_inhouse_production_items(doc)


def _validate_delivery_date(doc):
	if not doc.delivery_date:
		return

	if doc.get("custom_urgent"):
		return

	min_date = add_days(today(), 5)
	if getdate(doc.delivery_date) < getdate(min_date):
		frappe.throw(
			_("Delivery Date must be at least 5 days from today ({0}). "
			  "Enable <b>Urgent Order</b> to allow an earlier date.").format(min_date)
		)


def _validate_max_deliveries_per_date(doc):
	if not doc.delivery_date:
		return

	# Ready-to-dispatch orders bypass the 5-per-day limit
	if doc.get("custom_ready_to_dispatch"):
		return

	count = frappe.db.count(
		"Sales Order",
		filters={
			"delivery_date": doc.delivery_date,
			"name": ("!=", doc.name or ""),
			"docstatus": ("!=", 2),
		},
	)

	if count >= 5:
		frappe.throw(
			_("Cannot schedule delivery on {0}. "
			  "5 Sales Orders are already scheduled for that date.").format(
				frappe.format(doc.delivery_date, {"fieldtype": "Date"})
			)
		)


def _link_inhouse_production_items(doc):
	"""When a SO is saved, find in-house PIT records with matching item codes
	that have no sales order yet, and link them to this SO."""
	item_codes = list({row.item_code for row in doc.items if row.item_code})
	if not item_codes:
		return

	for item_code in item_codes:
		pit_records = frappe.get_all(
			"Production Item Tracking",
			filters={
				"in_house": 1,
				"item_code": item_code,
				"sales_order": ["is", "not set"],
			},
			fields=["name"],
			limit=1,
		)
		for pit in pit_records:
			frappe.db.set_value("Production Item Tracking", pit.name, "sales_order", doc.name, update_modified=False)
