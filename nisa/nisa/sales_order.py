import frappe
from frappe import _
from frappe.utils import getdate, add_days, today


def validate(doc, method=None):
	_validate_delivery_date(doc)
	_validate_max_deliveries_per_date(doc)


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
