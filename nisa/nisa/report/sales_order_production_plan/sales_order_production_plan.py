import frappe


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": "Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150,
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{"fieldname": "customer_name", "label": "Customer Name", "fieldtype": "Data", "width": 150},
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
		{"fieldname": "transaction_date", "label": "Date", "fieldtype": "Date", "width": 100},
		{"fieldname": "delivery_date", "label": "Delivery Date", "fieldtype": "Date", "width": 100},
		{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
		{"fieldname": "custom_urgent", "label": "Urgent", "fieldtype": "Check", "width": 80},
		{"fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 120},
		{
			"fieldname": "terms",
			"label": "Terms",
			"fieldtype": "Text Editor",
			"width": 300,
			"hidden": 0,  # Visible in grid but will be special in Print
		},
	]


def get_data(filters):
	conditions = []
	if filters.get("from_date"):
		conditions.append("so.transaction_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("so.transaction_date <= %(to_date)s")
	if filters.get("customer"):
		conditions.append("so.customer = %(customer)s")
	if filters.get("status"):
		conditions.append("so.status = %(status)s")
	if filters.get("custom_urgent"):
		conditions.append("so.custom_urgent = 1")

	where_clause = " AND ".join(conditions)
	if where_clause:
		where_clause = "WHERE " + where_clause

	sql = f"""
		SELECT
			so.name,
			so.customer,
			c.customer_name,
			soi.item_code,
			soi.item_name,
			so.transaction_date,
			so.delivery_date,
			so.status,
			so.custom_urgent,
			soi.amount,
			so.terms
		FROM
			`tabSales Order` so
		LEFT JOIN
			`tabSales Order Item` soi ON soi.parent = so.name
		LEFT JOIN
			`tabCustomer` c ON c.name = so.customer
		{where_clause}
		ORDER BY so.transaction_date DESC, so.name, soi.idx
	"""

	data = frappe.db.sql(sql, filters, as_dict=True)
	return data
