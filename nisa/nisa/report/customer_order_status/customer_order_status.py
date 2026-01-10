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
			"fieldname": "sales_order",
			"label": _("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 100
		},
  {
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"width": 150
		},
		{
			"fieldname": "delivery_date",
			"label": _("Delivery Date"),
			"fieldtype": "Date",
			"width": 110
		},
		{
			"fieldname": "total_items",
			"label": _("Total Items"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "completed_items",
			"label": _("Completed"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "in_progress_items",
			"label": _("In Progress"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "not_started_items",
			"label": _("Not Started"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "overdue_items",
			"label": _("Overdue"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "completion_percentage",
			"label": _("Completion %"),
			"fieldtype": "Percent",
			"width": 110
		},
		{
			"fieldname": "order_status",
			"label": _("Order Status"),
			"fieldtype": "Data",
			"width": 120
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			pit.sales_order,
			pit.customer,
			pit.customer_name,
			pit.sales_order_delivery_date as delivery_date,
			(SELECT st.sales_person
			 FROM `tabSales Team` st
			 WHERE st.parent = pit.sales_order
			 AND st.parenttype = 'Sales Order'
			 LIMIT 1) as sales_person,
			COUNT(*) as total_items,
			SUM(CASE WHEN pit.overall_status = 'Completed' THEN 1 ELSE 0 END) as completed_items,
			SUM(CASE WHEN pit.overall_status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_items,
			SUM(CASE WHEN pit.overall_status = 'Not Started' THEN 1 ELSE 0 END) as not_started_items,
			SUM(CASE WHEN pit.is_overdue = 1 THEN 1 ELSE 0 END) as overdue_items,
			(SUM(CASE WHEN pit.overall_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as completion_percentage,
			CASE
				WHEN SUM(CASE WHEN pit.overall_status = 'Completed' THEN 1 ELSE 0 END) = COUNT(*) THEN 'Completed'
				WHEN SUM(CASE WHEN pit.is_overdue = 1 THEN 1 ELSE 0 END) > 0 THEN 'Overdue'
				WHEN SUM(CASE WHEN pit.overall_status = 'In Progress' THEN 1 ELSE 0 END) > 0 THEN 'In Progress'
				ELSE 'Not Started'
			END as order_status
		FROM
			`tabProduction Item Tracking` pit
		WHERE
			1=1
			{conditions}
		GROUP BY
			pit.sales_order,
			pit.customer,
			pit.sales_order_delivery_date
		ORDER BY
			pit.sales_order_delivery_date ASC,
			completion_percentage ASC
	""".format(conditions=conditions), filters, as_dict=1)

	return data


def get_conditions(filters):
	conditions = []

	if filters.get("customer"):
		conditions.append("AND customer = %(customer)s")

	if filters.get("sales_order"):
		conditions.append("AND sales_order = %(sales_order)s")

	if filters.get("from_date"):
		conditions.append("AND sales_order_delivery_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND sales_order_delivery_date <= %(to_date)s")

	if filters.get("order_status"):
		if filters.get("order_status") == "Completed":
			conditions.append("""
				AND sales_order IN (
					SELECT sales_order FROM `tabProduction Item Tracking`
					GROUP BY sales_order
					HAVING SUM(CASE WHEN overall_status = 'Completed' THEN 1 ELSE 0 END) = COUNT(*)
				)
			""")
		elif filters.get("order_status") == "Overdue":
			conditions.append("""
				AND sales_order IN (
					SELECT sales_order FROM `tabProduction Item Tracking`
					WHERE is_overdue = 1
				)
			""")

	if filters.get("urgent"):
		conditions.append("""
			AND sales_order IN (
				SELECT sales_order FROM `tabProduction Item Tracking`
				WHERE urgent = 1
			)
		""")

	if filters.get("sales_person"):
		conditions.append("""
			AND sales_order IN (
				SELECT parent FROM `tabSales Team`
				WHERE parenttype = 'Sales Order'
				AND sales_person = %(sales_person)s
			)
		""")

	return " ".join(conditions)
