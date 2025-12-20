// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.query_reports["Partially Completed Orders"] = {
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
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "days_pending" && data && data.days_pending > 0) {
			value = "<span style='color: orange; font-weight: bold;'>" + data.days_pending + "</span>";
		}

		return value;
	}
};
