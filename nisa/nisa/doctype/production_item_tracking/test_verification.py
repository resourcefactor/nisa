import frappe
from frappe.utils import getdate, add_days
from nisa.nisa.doctype.production_item_tracking.production_item_tracking import complete_process, transfer_to_next, assign_to_worker
from nisa.nisa.report.overdue_production_items.overdue_production_items import execute as execute_report

def run_tests():
    # frappe.flags.in_test = True
    print("Starting verification tests...")

    # 1. Setup Data
    # Cleanup first
    if frappe.db.exists("Customer", "Test-Customer-PIT"):
        frappe.delete_doc("Customer", "Test-Customer-PIT", force=1)
    if frappe.db.exists("Item", "Test-Item-PIT"):
        frappe.delete_doc("Item", "Test-Item-PIT", force=1)
    if frappe.db.exists("Supplier", "Test-Supplier-PIT"):
        frappe.delete_doc("Supplier", "Test-Supplier-PIT", force=1)
    frappe.db.commit()

    if not frappe.db.exists("Item", "Test-Item-PIT"):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "Test-Item-PIT",
            "item_name": "Test Item PIT",
            "item_group": "All Item Groups",
            "is_stock_item": 1
        }).insert()
    
    if not frappe.db.exists("Customer", "Test-Customer-PIT"):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Customer PIT",
            "customer_type": "Individual",
            "customer_group": "Commercial",
            "insta_id": "test_insta"
        }).insert()

    if not frappe.db.exists("Sales Order", "Test-SO-PIT"):
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": "Test-Customer-PIT",
            "delivery_date": add_days(getdate(), 10),
            "items": [{
                "item_code": "Test-Item-PIT",
                "qty": 10,
                "delivery_date": add_days(getdate(), 10)
            }]
        }).insert()
        so.submit()
        so_name = so.name
    else:
        so_name = "Test-SO-PIT"

    if not frappe.db.exists("Supplier", "Test-Supplier-PIT"):
        supplier = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": "Test Supplier PIT",
            "supplier_group": "All Supplier Groups"
        }).insert()
        supplier_name = supplier.name
    else:
        supplier_name = "Test-Supplier-PIT"

    frappe.db.commit()

    print(f"Customer exists: {frappe.db.exists('Customer', 'Test-Customer-PIT')}")
    if frappe.db.exists("Customer", "Test-Customer-PIT"):
        print(frappe.get_doc("Customer", "Test-Customer-PIT").as_dict())

    # Create Production Item Tracking
    doc = frappe.get_doc({
        "doctype": "Production Item Tracking",
        "sales_order": so_name,
        "item_code": "Test-Item-PIT",
        "qty": 1,
        "sales_order_item_row": "row_1"
    }).insert()
    
    print(f"Created PIT: {doc.name}")

    # 2. Assign to Worker
    assign_to_worker(doc.name, "Painter", supplier_name, 5, "Test Assignment")
    doc.reload()
    assert doc.current_process == "Painter"
    assert doc.current_assignee == supplier_name
    assert doc.overall_status == "In Progress"
    print("Assignment Verified")

    # 3. Complete Process -> Partially Completed
    complete_process(doc.name, "Done Painting")
    doc.reload()
    assert doc.received_date == getdate()
    assert doc.overall_status == "Partially Completed"
    print("Partially Completed Status Verified")

    # 4. Verify Report Exclusion
    # Force expected date to be in the past to make it potentially overdue
    doc.expected_completion_date = add_days(getdate(), -1)
    doc.save()
    
    # Check report
    columns, data = execute_report()
    item_in_report = any(d['name'] == doc.name for d in data)
    assert not item_in_report, "Item should NOT be in overdue report if Partially Completed"
    print("Report Exclusion Verified")

    # 5. Transfer to Next -> In Progress
    transfer_to_next(doc.name, "Dyer", supplier_name, 5, "Transferring")
    doc.reload()
    assert doc.received_date is None
    assert doc.current_process == "Dyer"
    assert doc.overall_status == "In Progress"
    print("Transfer Logic Verified")

    # Cleanup
    doc.delete()
    # frappe.delete_doc("Sales Order", so_name) # Keep SO for re-runs if needed
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
