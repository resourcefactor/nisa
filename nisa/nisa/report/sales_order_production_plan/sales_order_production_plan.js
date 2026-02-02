frappe.query_reports["Sales Order Production Plan"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "width": "80"
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": "80"
        },
        {
            "fieldname": "sales_person",
            "label": "Sales Person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": "80"
        },
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": "60"
        },
        {
            "fieldname": "customer_name",
            "label": "Customer Name",
            "fieldtype": "Data",
            "width": "80"
        },

        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": ["", "Draft", "On Hold", "To Deliver and Bill", "To Bill", "To Deliver", "Completed", "Cancelled", "Closed"],
            "width": "80"
        },
        {
            "fieldname": "custom_urgent",
            "label": "Urgent",
            "fieldtype": "Check",
            "width": "80"
        }
    ]
};
