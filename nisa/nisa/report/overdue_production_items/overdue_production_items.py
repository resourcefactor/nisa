# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "image",
			"label": _("Image"),
			"fieldtype": "Image",
			"width": 80,
		},
		{
			"fieldname": "name",
			"label": _("ID"),
			"fieldtype": "Link",
			"options": "Production Item Tracking",
			"width": 120
		},
		{
			"fieldname": "sales_order",
			"label": _("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 130
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 120
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"width": 150
		},
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 120
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "current_process",
			"label": _("Current Process"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "current_assignee",
			"label": _("Current Assignee"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 120
		},
		{
			"fieldname": "assignee_name",
			"label": _("Assignee Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "assigned_date",
			"label": _("Assigned Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "expected_completion_date",
			"label": _("Expected Date"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "days_overdue",
			"label": _("Days Overdue"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "sales_order_delivery_date",
			"label": _("SO Delivery Date"),
			"fieldtype": "Date",
			"width": 120
		}
	]


def get_data(filters):
	from frappe.utils import getdate, date_diff
	
	conditions = get_conditions(filters)

	# Fetch data - note we're still selecting days_overdue for filtering, but will recalculate
	data = frappe.db.sql("""
		SELECT
			pit.name,
			pit.sales_order,
			pit.customer,
			pit.customer_name,
			(SELECT st.sales_person
			 FROM `tabSales Team` st
			 WHERE st.parent = pit.sales_order
			 AND st.parenttype = 'Sales Order'
			 LIMIT 1) as sales_person,
			pit.item_code,
			pit.item_name,
			pit.current_process,
			pit.current_assignee,
			pit.assignee_name,
			pit.assigned_date,
			pit.expected_completion_date,
			pit.received_date,
			pit.sales_order_delivery_date,
			COALESCE(
				(SELECT soi.custom_top_article_image
				 FROM `tabSales Order Item` soi
				 WHERE soi.parent = pit.sales_order AND soi.item_code = pit.item_code
				 LIMIT 1),
				(SELECT soi.custom_bottom_article_image
				 FROM `tabSales Order Item` soi
				 WHERE soi.parent = pit.sales_order AND soi.item_code = pit.item_code
				 LIMIT 1),
				(SELECT i.image FROM `tabItem` i WHERE i.name = pit.item_code)
			) as image
		FROM
			`tabProduction Item Tracking` pit
		WHERE
			pit.actual_completion_date IS NULL
			AND pit.expected_completion_date IS NOT NULL
			{conditions}
		ORDER BY
			pit.expected_completion_date ASC
	""".format(conditions=conditions), filters, as_dict=1)
	
	# Calculate days_overdue dynamically for each row
	today = getdate()
	overdue_items = []
	
	for row in data:
		# Skip records where received_date is available
		if row.received_date:
			continue

		if row.expected_completion_date:
			expected_date = getdate(row.expected_completion_date)
			# Only include items that are actually overdue
			if today > expected_date:
				row['days_overdue'] = date_diff(today, expected_date)
				overdue_items.append(row)
	
	# Sort by days_overdue descending, then by SO delivery date
	overdue_items.sort(key=lambda x: (-x['days_overdue'], x.get('sales_order_delivery_date') or '9999-12-31'))
	
	return overdue_items


def get_conditions(filters):
	conditions = []

	if filters.get("customer"):
		conditions.append("AND customer = %(customer)s")

	if filters.get("sales_order"):
		conditions.append("AND sales_order = %(sales_order)s")

	if filters.get("current_process"):
		conditions.append("AND current_process = %(current_process)s")

	if filters.get("current_assignee"):
		conditions.append("AND current_assignee = %(current_assignee)s")

	if filters.get("from_date"):
		conditions.append("AND assigned_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND assigned_date <= %(to_date)s")

	if filters.get("urgent"):
		conditions.append("AND urgent = 1")

	if filters.get("sales_person"):
		conditions.append("""
			AND sales_order IN (
				SELECT parent FROM `tabSales Team`
				WHERE parenttype = 'Sales Order'
				AND sales_person = %(sales_person)s
			)
		""")

	return " ".join(conditions)
