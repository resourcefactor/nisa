app_name = "nisa"
app_title = "Nisa"
app_publisher = "RF"
app_description = "Nisa"
app_email = "it@resourcefactors.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "nisa",
# 		"logo": "/assets/nisa/logo.png",
# 		"title": "Nisa",
# 		"route": "/nisa",
# 		"has_permission": "nisa.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nisa/css/nisa.css"
# app_include_js = "/assets/nisa/js/nisa.js"

# include js, css files in header of web template
# web_include_css = "/assets/nisa/css/nisa.css"
# web_include_js = "/assets/nisa/js/nisa.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "nisa/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"Sales Order": "public/js/sales_order_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "nisa/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "nisa.utils.jinja_methods",
# 	"filters": "nisa.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "nisa.install.before_install"
# after_install = "nisa.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "nisa.uninstall.before_uninstall"
# after_uninstall = "nisa.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "nisa.utils.before_app_install"
# after_app_install = "nisa.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "nisa.utils.before_app_uninstall"
# after_app_uninstall = "nisa.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nisa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Notification": "nisa.hook.notification.OvrNotification",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Order": {
        "validate": "nisa.nisa.sales_order.validate",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        # Run daily at 1:00 AM to update overdue status
        "0 1 * * *": [
            "nisa.nisa.doctype.production_item_tracking.production_item_tracking.update_all_overdue_status"
        ]
    }
}

# Testing
# -------

# before_tests = "nisa.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "nisa.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "nisa.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["nisa.utils.before_request"]
# after_request = ["nisa.utils.after_request"]

# Job Events
# ----------
# before_job = ["nisa.utils.before_job"]
# after_job = ["nisa.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"nisa.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", ["Sales Order", "Sales Order Item"]],
        ],
    }
]
