// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.query_reports["Production Status"] = {
	"filters": [
		{
			"fieldname": "supplier_name",
			"label": __("Supplier Name"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname": "completion_status",
			"label": __("Completion Status"),
			"fieldtype": "Select",
			"options": "Not Completed\nCompleted\nAll",
			"default": "Not Completed"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -30)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "urgent",
			"label": __("Urgent"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "show_partially_completed",
			"label": __("Show Partially Completed"),
			"fieldtype": "Check",
			"default": 0
		}
	],
	"onload": function (report) {
		// Highlight rows where In Stock = "Yes"
		report.page.add_inner_button(__('Refresh'), function () {
			report.refresh();
		});
	},
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Highlight entire row if in_stock is "Yes"
		if (data && data.in_stock === "Yes") {
			var style = "background-color: #fffacd !important;"; // Light yellow
			if (value.indexOf("style=") !== -1) {
				value = value.replace(/style="/, 'style="' + style);
			} else {
				value = value.replace(/<td/, '<td style="' + style + '"');
			}
		}

		return value;
	}
};
