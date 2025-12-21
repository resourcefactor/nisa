# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "assigned_to",
			"label": _("Worker"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 180
		},
		{
			"fieldname": "process_type",
			"label": _("Process Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "total_assignments",
			"label": _("Total Assignments"),
			"fieldtype": "Int",
			"width": 130
		},
		{
			"fieldname": "completed",
			"label": _("Completed"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "in_progress",
			"label": _("In Progress"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "overdue",
			"label": _("Overdue"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "avg_days_taken",
			"label": _("Avg Days Taken"),
			"fieldtype": "Float",
			"precision": 1,
			"width": 120
		},
		{
			"fieldname": "completion_rate",
			"label": _("Completion Rate %"),
			"fieldtype": "Percent",
			"width": 130
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)

	# Get worker performance data from assignment history
	data = frappe.db.sql("""
		SELECT
			iah.assigned_to,
			iah.process_type,
			COUNT(*) as total_assignments,
			SUM(CASE WHEN iah.status = 'Completed' THEN 1 ELSE 0 END) as completed,
			SUM(CASE WHEN iah.status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
			SUM(CASE WHEN pit.is_overdue = 1 AND iah.status != 'Completed' THEN 1 ELSE 0 END) as overdue,
			AVG(CASE WHEN iah.days_taken IS NOT NULL THEN iah.days_taken ELSE NULL END) as avg_days_taken,
			(SUM(CASE WHEN iah.status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as completion_rate
		FROM
			`tabItem Assignment History` iah
		LEFT JOIN
			`tabProduction Item Tracking` pit ON iah.parent = pit.name
		WHERE
			1=1
			{conditions}
		GROUP BY
			iah.assigned_to,
			iah.process_type
		ORDER BY
			completion_rate DESC,
			avg_days_taken ASC
	""".format(conditions=conditions), filters, as_dict=1)

	return data


def get_conditions(filters):
	conditions = []

	if filters.get("worker"):
		conditions.append("AND iah.assigned_to = %(worker)s")

	if filters.get("process_type"):
		conditions.append("AND iah.process_type = %(process_type)s")

	if filters.get("from_date"):
		conditions.append("AND iah.assigned_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("AND iah.assigned_date <= %(to_date)s")

	if filters.get("urgent"):
		conditions.append("AND pit.urgent = 1")

	return " ".join(conditions)


def get_chart_data(data):
	if not data:
		return None

	# Create chart showing completion rate by worker
	workers = [d.assigned_to for d in data[:10]]  # Top 10 workers
	completion_rates = [d.completion_rate for d in data[:10]]

	return {
		"data": {
			"labels": workers,
			"datasets": [
				{
					"name": "Completion Rate %",
					"values": completion_rates
				}
			]
		},
		"type": "bar",
		"colors": ["#28a745"]
	}
