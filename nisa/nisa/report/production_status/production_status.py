# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "sales_order",
			"label": _("SO No."),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 130
		},
		{
			"fieldname": "supplier_code",
			"label": _("Supplier Code"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 100
		},
		{
			"fieldname": "supplier_name",
			"label": _("Supplier Name"),
			"fieldtype": "Data",				
			"width": 180
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
			"width": 180
		},
		{
			"fieldname": "qty",
			"label": _("Qty"),
			"fieldtype": "Float",
			"width": 80
		},
		{
			"fieldname": "assignment_date",
			"label": _("Assignment Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "expected_completion_date",
			"label": _("Expected Completion Date"),
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "actual_date",
			"label": _("Actual Date"),
			"fieldtype": "Date",
			"width": 120
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			pit.sales_order,
			sup.supplier_name as supplier_code,
			pit.current_assignee as supplier_name,
			pit.customer,
			pit.customer_name,
			pit.item_code,
			pit.item_name,
			pit.qty,
			pit.assigned_date as assignment_date,
			pit.expected_completion_date,
			pit.actual_completion_date as actual_date
		FROM
			`tabProduction Item Tracking` pit
		LEFT JOIN
			`tabSupplier` sup ON pit.current_assignee = sup.name
		WHERE
			pit.received_date is not null and  1=1
			{conditions}
		ORDER BY
			pit.sales_order,
			pit.assigned_date
	""".format(conditions=conditions), filters, as_dict=1)

	return data


def get_conditions(filters):
	conditions = []

	if filters.get("supplier_name"):
		conditions.append("AND pit.current_assignee = %(supplier_name)s")

	if filters.get("from_date"):
		conditions.append("AND pit.assigned_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND pit.assigned_date <= %(to_date)s")

	return " ".join(conditions)
