// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.query_reports["Overdue Production Items"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "sales_order",
			"label": __("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname": "current_process",
			"label": __("Current Process"),
			"fieldtype": "Select",
			"options": "\nDyer\nPainter\nEmbellisher\nTailor\nQuality Check\nOut for Delivery"
		},
		{
			"fieldname": "current_assignee",
			"label": __("Current Assignee"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "urgent",
			"label": __("Urgent"),
			"fieldtype": "Check"
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "days_overdue" && data && data.days_overdue > 0) {
			value = "<span style='color: red; font-weight: bold;'>" + data.days_overdue + "</span>";
		}

		return value;
	}
};
