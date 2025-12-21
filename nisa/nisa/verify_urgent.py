import frappe
from frappe.utils import today

def execute():
    try:
        frappe.reload_doc("nisa", "doctype", "production_item_tracking")
        # 1. Create a Sales Order with Urgent = 1
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": frappe.get_all("Customer", limit=1)[0].name,
            "delivery_date": today(),
            "custom_urgent": 1,
            "items": [
                {
                    "item_code": frappe.get_all("Item", limit=1)[0].name,
                    "qty": 1,
                    "delivery_date": today(),
                    "rate": 100
                }
            ]
        })
        so.insert()
        print(f"Created Sales Order: {so.name} with Urgent={so.custom_urgent}")

        # 2. Create Production Item Tracking
        pit = frappe.get_doc({
            "doctype": "Production Item Tracking",
            "sales_order": so.name,
            "item_code": so.items[0].item_code,
            "qty": 1
        })
        pit.insert()
        print(f"Created Production Item Tracking: {pit.name}")

        # 3. Verify propagation
        if pit.urgent:
            print("SUCCESS: Urgent status propagated to Production Item Tracking")
        else:
            print("FAILURE: Urgent status NOT propagated")

        # 4. Verify Reports
        print("Verifying Reports...")
        reports = [
            "Production Status",
            "Overdue Production Items",
            "Worker Performance",
            "Partially Completed Orders",
            "Customer Order Status"
        ]
        
        for report in reports:
            try:
                # Just checking if execute runs without error with the new filter
                frappe.get_doc("Report", report).execute(filters={"urgent": 1})
                print(f"Report '{report}' ran successfully with urgent filter")
            except Exception as e:
                print(f"Report '{report}' FAILED: {str(e)}")

    except Exception as e:
        print(f"Verification Failed: {str(e)}")
        frappe.db.rollback()
    finally:
        frappe.db.rollback()
