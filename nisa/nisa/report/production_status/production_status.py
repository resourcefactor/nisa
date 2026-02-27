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
			"fieldname": "delivery_date",
			"label": _("Delivery Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "supplier_name",
			"label": _("Supplier Name"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "supplier_code",
			"label": _("Supplier Code"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 100
		},
		{
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
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
		},
		{
			"fieldname": "in_stock",
			"label": _("In Stock"),
			"fieldtype": "Data",
			"width": 80
		}
	]


def get_data(filters):
	if filters.get("completion_status") == "Not Started":
		return get_not_started_data(filters)

	conditions = get_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			pit.sales_order,
			sup.supplier_name as supplier_name,
			pit.current_assignee as supplier_code,
			pit.customer,
			pit.customer_name,
			(
				SELECT st.sales_person
				FROM `tabSales Team` st
				WHERE st.parent = pit.sales_order
				AND st.parenttype = 'Sales Order'
				ORDER BY st.idx
				LIMIT 1
			) as sales_person,
			pit.item_code,
			pit.item_name,
			pit.qty,
			pit.assigned_date as assignment_date,
			pit.expected_completion_date,
			pit.actual_completion_date as actual_date,
			pit.received_date,
			pit.current_assignee,
			pit.overall_status,
			(SELECT delivery_date FROM `tabSales Order` WHERE name = pit.sales_order) as delivery_date
		FROM
			`tabProduction Item Tracking` pit
		LEFT JOIN
			`tabSupplier` sup ON pit.current_assignee = sup.name
		WHERE
			1=1
			{conditions}
		ORDER BY
			pit.sales_order,
			pit.assigned_date
	""".format(conditions=conditions), filters, as_dict=1)

	# Calculate in_stock status for each row
	for row in data:
		# In Stock = received_date exists AND (assigned_date <= received_date) AND no actual_completion_date
		# This means item was received back but hasn't been assigned to next process yet
		received_date = row.get('received_date')
		assignment_date = row.get('assignment_date')
		actual_date = row.get('actual_date')
		
		# Check if received_date exists (not None and not empty)
		# AND assignment_date exists
		# AND received_date >= assignment_date
		# AND actual_date is empty (None or empty string)
		if (received_date and received_date != '' and
				assignment_date and assignment_date != '' and
				received_date >= assignment_date and
				not actual_date):
			row['in_stock'] = 'Yes'
		else:
			row['in_stock'] = ''

	return data


def get_not_started_data(filters):
	pit_conditions = ["AND pit.overall_status = 'Not Started'"]
	so_conditions = []

	if filters.get("supplier_name"):
		pit_conditions.append("AND pit.current_assignee = %(supplier_name)s")

	if filters.get("from_date"):
		pit_conditions.append("AND pit.assigned_date >= %(from_date)s")
		so_conditions.append("AND so.transaction_date >= %(from_date)s")

	if filters.get("to_date"):
		pit_conditions.append("AND pit.assigned_date <= %(to_date)s")
		so_conditions.append("AND so.transaction_date <= %(to_date)s")

	if filters.get("urgent"):
		pit_conditions.append("AND pit.urgent = 1")

	if filters.get("sales_person"):
		sp_subquery = """
			AND pit.sales_order IN (
				SELECT parent FROM `tabSales Team`
				WHERE parenttype = 'Sales Order'
				AND sales_person = %(sales_person)s
			)
		"""
		pit_conditions.append(sp_subquery)
		so_sp_subquery = """
			AND so.name IN (
				SELECT parent FROM `tabSales Team`
				WHERE parenttype = 'Sales Order'
				AND sales_person = %(sales_person)s
			)
		"""
		so_conditions.append(so_sp_subquery)

	pit_where = " ".join(pit_conditions)
	so_where = " ".join(so_conditions)

	# Part A: existing PIT records with no assignee yet
	part_a = frappe.db.sql("""
		SELECT
			pit.sales_order,
			sup.supplier_name as supplier_name,
			pit.current_assignee as supplier_code,
			pit.customer,
			pit.customer_name,
			(
				SELECT st.sales_person FROM `tabSales Team` st
				WHERE st.parent = pit.sales_order AND st.parenttype = 'Sales Order'
				ORDER BY st.idx LIMIT 1
			) as sales_person,
			pit.item_code,
			pit.item_name,
			pit.qty,
			pit.assigned_date as assignment_date,
			pit.expected_completion_date,
			pit.actual_completion_date as actual_date,
			pit.received_date,
			pit.current_assignee,
			pit.overall_status,
			(SELECT delivery_date FROM `tabSales Order` WHERE name = pit.sales_order) as delivery_date
		FROM `tabProduction Item Tracking` pit
		LEFT JOIN `tabSupplier` sup ON pit.current_assignee = sup.name
		WHERE 1=1 {pit_where}
		ORDER BY pit.sales_order, pit.assigned_date
	""".format(pit_where=pit_where), filters, as_dict=1)

	# Part B: Sales Orders that have NO Production Item Tracking record at all
	# supplier_name filter is not applicable here (no assignee exists)
	part_b = frappe.db.sql("""
		SELECT
			so.name as sales_order,
			NULL as supplier_code,
			NULL as supplier_name,
			so.customer,
			so.customer_name,
			(
				SELECT st.sales_person FROM `tabSales Team` st
				WHERE st.parent = so.name AND st.parenttype = 'Sales Order'
				ORDER BY st.idx LIMIT 1
			) as sales_person,
			soi.item_code,
			soi.item_name,
			soi.qty,
			NULL as assignment_date,
			NULL as expected_completion_date,
			NULL as actual_date,
			NULL as received_date,
			NULL as current_assignee,
			'Not Started' as overall_status,
			so.delivery_date
		FROM `tabSales Order` so
		JOIN `tabSales Order Item` soi ON soi.parent = so.name AND soi.parenttype = 'Sales Order'
		WHERE so.docstatus = 1
		{so_where}
		AND NOT EXISTS (
			SELECT 1 FROM `tabProduction Item Tracking` pit
			WHERE pit.sales_order = so.name
		)
		ORDER BY so.name
	""".format(so_where=so_where), filters, as_dict=1)

	data = list(part_a) + list(part_b)
	for row in data:
		row['in_stock'] = ''

	return data


def get_conditions(filters):
	conditions = []

	if filters.get("supplier_name"):
		conditions.append("AND pit.current_assignee = %(supplier_name)s")

	if filters.get("from_date"):
		conditions.append("AND pit.assigned_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND pit.assigned_date <= %(to_date)s")

	if filters.get("urgent"):
		conditions.append("AND pit.urgent = 1")

	if filters.get("sales_person"):
		conditions.append("""
			AND pit.sales_order IN (
				SELECT parent FROM `tabSales Team`
				WHERE parenttype = 'Sales Order'
				AND sales_person = %(sales_person)s
			)
		""")

	if filters.get("completion_status"):
		if filters.get("completion_status") == "Not Started":
			conditions.append("AND pit.overall_status = 'Not Started'")
		elif filters.get("completion_status") == "In Progress":
			conditions.append("AND pit.overall_status = 'In Progress'")
		elif filters.get("completion_status") == "Overdue":
			conditions.append("AND pit.overall_status = 'Overdue'")
		elif filters.get("completion_status") == "Not Completed":
			conditions.append("AND pit.actual_completion_date IS NULL")
		elif filters.get("completion_status") == "Completed":
			conditions.append("AND pit.actual_completion_date IS NOT NULL")
		# "All" option doesn't add any condition

	# Filter out Partially Completed items if checkbox is not checked
	# Partially Completed = received_date exists but actual_completion_date does not exist
	if not filters.get("show_partially_completed"):
		conditions.append("""
			AND NOT (
				(pit.received_date IS NOT NULL AND pit.received_date != '')
				AND (pit.actual_completion_date IS NULL OR pit.actual_completion_date = '')
			)
		""")

	return " ".join(conditions)
