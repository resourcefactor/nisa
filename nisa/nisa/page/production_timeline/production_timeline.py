# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

import frappe
import json


@frappe.whitelist()
def get_timeline_data(filters=None):
	"""
	Get data for timeline visualization
	"""
	# Parse filters if it comes as JSON string
	if isinstance(filters, str):
		filters = json.loads(filters) if filters else {}

	if filters is None:
		filters = {}

	# Validate that at least one filter is provided
	if not any(filters.values()):
		frappe.throw('Please select at least one filter to load data.')

	# Build query conditions
	conditions = []
	values = {}

	if filters.get('customer'):
		conditions.append('customer = %(customer)s')
		values['customer'] = filters['customer']

	if filters.get('sales_order'):
		conditions.append('sales_order = %(sales_order)s')
		values['sales_order'] = filters['sales_order']

	if filters.get('overall_status'):
		conditions.append('overall_status = %(overall_status)s')
		values['overall_status'] = filters['overall_status']

	if filters.get('current_process'):
		conditions.append('current_process = %(current_process)s')
		values['current_process'] = filters['current_process']

	where_clause = ' AND '.join(conditions) if conditions else '1=1'

	# Get main items
	items = frappe.db.sql(f"""
		SELECT
			name,
			sales_order,
			customer,
			customer_name,
			item_code,
			item_name,
			qty,
			current_process,
			current_assignee,
			assignee_name,
			assigned_date,
			expected_completion_date,
			actual_completion_date,
			overall_status,
			is_overdue,
			days_overdue
		FROM
			`tabProduction Item Tracking`
		WHERE
			{where_clause}
		ORDER BY
			sales_order, item_code
	""", values, as_dict=1)

	# Get assignment history for each item
	for item in items:
		history = frappe.get_all(
			'Item Assignment History',
			filters={'parent': item.name},
			fields=[
				'process_type',
				'assigned_to',
				'assigned_to.supplier_name as supplier_name',
				'assigned_date',
				'received_date',
				'status',
				'days_taken'
			],
			order_by='assigned_date'
		)
		item['history'] = history

	return items


@frappe.whitelist()
def update_status_inline(doc_name, field, value):
	"""
	Update status inline from timeline view
	"""
	doc = frappe.get_doc('Production Item Tracking', doc_name)
	doc.set(field, value)
	doc.save()
	frappe.db.commit()

	return {'success': True, 'message': 'Status updated successfully'}
