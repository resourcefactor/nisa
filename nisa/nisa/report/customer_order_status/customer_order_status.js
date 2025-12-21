// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Order Status"] = {
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
			"fieldname": "from_date",
			"label": __("From Delivery Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Delivery Date"),
			"fieldtype": "Date"
		},
		{
			"fieldtype": "Select",
			"options": "\nCompleted\nIn Progress\nOverdue\nNot Started"
		},
		{
			"fieldname": "urgent",
			"label": __("Urgent"),
			"fieldtype": "Check"
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "overdue_items" && data && data.overdue_items > 0) {
			value = "<span style='color: red; font-weight: bold;'>" + data.overdue_items + "</span>";
		}

		if (column.fieldname == "order_status" && data) {
			let status = data.order_status;
			let color = 'gray';
			if (status === 'Completed') color = 'green';
			else if (status === 'In Progress') color = 'blue';
			else if (status === 'Overdue') color = 'red';

			value = "<span style='color: " + color + "; font-weight: bold;'>" + status + "</span>";
		}

		if (column.fieldname == "completion_percentage" && data) {
			let pct = data.completion_percentage;
			let color = pct >= 80 ? 'green' : pct >= 50 ? 'orange' : 'red';
			value = "<span style='color: " + color + "; font-weight: bold;'>" + pct.toFixed(1) + "%</span>";
		}

		return value;
	}
};
