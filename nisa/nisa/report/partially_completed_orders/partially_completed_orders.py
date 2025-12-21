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
			"fieldname": "received_date",
			"label": _("Received Date"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "days_pending",
			"label": _("Days Pending"),
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

	# Fetch data - items where received_date exists but actual_completion_date is missing
	data = frappe.db.sql("""
		SELECT
			name,
			sales_order,
			customer,
			customer_name,
			item_code,
			item_name,
			current_process,
			current_assignee,
			assignee_name,
			assigned_date,
			received_date,
			sales_order_delivery_date
		FROM
			`tabProduction Item Tracking`
		WHERE
			actual_completion_date IS NULL
			AND received_date IS NOT NULL
			{conditions}
		ORDER BY
			received_date ASC
	""".format(conditions=conditions), filters, as_dict=1)

	# Calculate days_pending dynamically for each row
	today = getdate()

	for row in data:
		if row.received_date:
			received_date = getdate(row.received_date)
			row['days_pending'] = date_diff(today, received_date)

	# Sort by days_pending descending, then by SO delivery date
	data.sort(key=lambda x: (-x.get('days_pending', 0), x.get('sales_order_delivery_date') or '9999-12-31'))

	return data


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
		conditions.append("AND received_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND received_date <= %(to_date)s")

	if filters.get("urgent"):
		conditions.append("AND urgent = 1")

	return " ".join(conditions)
