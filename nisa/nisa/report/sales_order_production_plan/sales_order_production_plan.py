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
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "transaction_date",
			"label": "Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "delivery_date",
			"label": "Delivery Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "custom_urgent",
			"label": "Urgent",
			"fieldtype": "Check",
			"width": 80
		},
		{
			"fieldname": "grand_total",
			"label": "Grand Total",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "terms",
			"label": "Terms",
			"fieldtype": "Text Editor",
			"width": 300,
			"hidden": 0 # Visible in grid but will be special in Print
		}
	]

def get_data(filters):
	conditions = []
	if filters.get("from_date"):
		conditions.append("transaction_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("transaction_date <= %(to_date)s")
	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
	if filters.get("status"):
		conditions.append("status = %(status)s")
	if filters.get("custom_urgent"):
		conditions.append("custom_urgent = 1")

	where_clause = " AND ".join(conditions)
	if where_clause:
		where_clause = "WHERE " + where_clause
	
	sql = f"""
		SELECT
			name, customer, transaction_date, delivery_date, status, custom_urgent, grand_total, terms
		FROM
			`tabSales Order`
		{where_clause}
		ORDER BY transaction_date DESC
	"""
	
	data = frappe.db.sql(sql, filters, as_dict=True)
	return data
