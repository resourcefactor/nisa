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
			"width": 150
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
	conditions = get_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			name,
			sales_order,
			customer,
			item_code,
			item_name,
			current_process,
			current_assignee,
			assigned_date,
			expected_completion_date,
			days_overdue,
			sales_order_delivery_date
		FROM
			`tabProduction Item Tracking`
		WHERE
			is_overdue = 1
			AND actual_completion_date IS NULL
			{conditions}
		ORDER BY
			days_overdue DESC,
			sales_order_delivery_date ASC
	""".format(conditions=conditions), filters, as_dict=1)

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
		conditions.append("AND assigned_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND assigned_date <= %(to_date)s")

	return " ".join(conditions)
