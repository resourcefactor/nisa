// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.query_reports["Worker Performance"] = {
	"filters": [
		{
			"fieldname": "worker",
			"label": __("Worker"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname": "process_type",
			"label": __("Process Type"),
			"fieldtype": "Select",
			"options": "\nDyer\nPainter\nEmbellisher\nTailor\nQuality Check\nOut for Delivery"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "overdue" && data && data.overdue > 0) {
			value = "<span style='color: red; font-weight: bold;'>" + data.overdue + "</span>";
		}

		if (column.fieldname == "completion_rate" && data) {
			let rate = data.completion_rate;
			let color = rate >= 80 ? 'green' : rate >= 50 ? 'orange' : 'red';
			value = "<span style='color: " + color + "; font-weight: bold;'>" + rate.toFixed(1) + "%</span>";
		}

		if (column.fieldname == "avg_days_taken" && data && data.avg_days_taken) {
			value = data.avg_days_taken.toFixed(1);
		}

		return value;
	}
};
