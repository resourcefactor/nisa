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
		}
	]
};
