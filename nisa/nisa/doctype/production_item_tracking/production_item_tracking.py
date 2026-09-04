# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import getdate, add_days, date_diff


def autoname_doc(doc, method=None):
    if doc.sales_order and doc.item_code:
        doc.name = make_autoname(f"PIT-{doc.sales_order}-{doc.item_code}-.####")
    elif doc.item_code:
        doc.name = make_autoname(f"PIT-IH-{doc.item_code}-.####")
    else:
        doc.name = make_autoname("PIT-IH-.####")


class ProductionItemTracking(Document):
	def validate(self):
		if not self.in_house and not self.sales_order:
			frappe.throw(_("Sales Order is mandatory unless In-House is checked."))
		if self.in_house and not self.sales_order:
			# Clear SO-linked fields so there are no orphan references
			self.customer = self.customer or None
			self.customer_name = self.customer_name or None
			self.sales_order_delivery_date = None

	def before_insert(self):
		if not self.urgent and self.sales_order:
			self.urgent = frappe.db.get_value("Sales Order", self.sales_order, "custom_urgent")

	def onload(self):
		"""Recalculate overdue status on document load for real-time accuracy"""
		self.calculate_overdue_status()
		self.update_overall_status()
	
	def before_save(self):
		"""Auto-calculate dates and overdue status before saving"""
		self.calculate_expected_completion_date()
		self.calculate_overdue_status()
		self.update_overall_status()

	def calculate_expected_completion_date(self):
		"""Calculate expected completion date based on assigned date and required days"""
		if self.assigned_date and self.required_days:
			self.expected_completion_date = add_days(self.assigned_date, self.required_days)
		elif self.assigned_date and self.expected_completion_date:
			# If expected date is set, calculate required days
			self.required_days = date_diff(self.expected_completion_date, self.assigned_date)

	def calculate_overdue_status(self):
		"""Calculate if item is overdue and by how many days"""
		# If received_date is set (Partially Completed), don't mark as overdue
		if self.received_date:
			self.is_overdue = 0
			self.days_overdue = 0
			return
			
		if self.expected_completion_date and not self.actual_completion_date:
			today = getdate()
			expected_date = getdate(self.expected_completion_date)

			if today > expected_date:
				self.is_overdue = 1
				self.days_overdue = date_diff(today, expected_date)
			else:
				self.is_overdue = 0
				self.days_overdue = 0
		else:
			self.is_overdue = 0
			self.days_overdue = 0

	def update_overall_status(self):
		"""Update overall status based on current state"""
		if self.actual_completion_date:
			self.overall_status = "Completed"
		elif self.received_date:
			self.overall_status = "Partially Completed"
		elif self.is_overdue:
			self.overall_status = "Overdue"
		elif self.current_assignee:
			self.overall_status = "In Progress"
		else:
			self.overall_status = "Not Started"


@frappe.whitelist()
def assign_to_worker(doc_name, process_type, assignee, required_days, remarks=None):
	"""
	Assign item to a worker and create history record
	"""
	doc = frappe.get_doc("Production Item Tracking", doc_name)

	# Convert required_days to int (comes as string from form)
	required_days = int(required_days)

	# Update current assignment
	doc.current_process = process_type
	doc.current_assignee = assignee
	doc.assigned_date = getdate()
	doc.required_days = required_days
	doc.required_days = required_days
	doc.actual_completion_date = None
	doc.received_date = None

	# Add to history
	doc.append("assignment_history", {
		"process_type": process_type,
		"assigned_to": assignee,
		"assigned_date": getdate(),
		"expected_date": add_days(getdate(), required_days),
		"status": "Assigned",
		"remarks": remarks
	})

	doc.save()
	frappe.db.commit()

	return {"success": True, "message": f"Item assigned to {assignee} for {process_type}"}


@frappe.whitelist()
def mark_received(doc_name, remarks=None):
	"""
	Mark current assignment as received (in progress)
	"""
	doc = frappe.get_doc("Production Item Tracking", doc_name)

	# Update last history entry status
	if doc.assignment_history:
		last_entry = doc.assignment_history[-1]
		last_entry.status = "In Progress"
		if remarks:
			last_entry.remarks = (last_entry.remarks or "") + "\n" + remarks

	doc.save()
	frappe.db.commit()

	return {"success": True, "message": "Item marked as received"}


@frappe.whitelist()
def complete_process(doc_name, remarks=None):
	"""
	Mark current process as completed
	"""
	doc = frappe.get_doc("Production Item Tracking", doc_name)

	# Update last history entry
	if doc.assignment_history:
		last_entry = doc.assignment_history[-1]
		last_entry.status = "Completed"
		last_entry.received_date = getdate()

		doc.received_date = getdate()

		# Calculate days taken
		if last_entry.assigned_date:
			last_entry.days_taken = date_diff(getdate(), last_entry.assigned_date)

		if remarks:
			last_entry.remarks = (last_entry.remarks or "") + "\n" + remarks

	# If all processes are complete, mark actual completion
	if doc.current_process == "Out for Delivery":
		doc.actual_completion_date = getdate()

	doc.save()
	frappe.db.commit()

	return {"success": True, "message": "Process completed successfully"}


@frappe.whitelist()
def transfer_to_next(doc_name, next_process, next_assignee, required_days, remarks=None):
	"""
	Complete current process and assign to next worker in one action
	"""
	doc = frappe.get_doc("Production Item Tracking", doc_name)

	# Convert required_days to int (comes as string from form)
	required_days = int(required_days)

	# Complete current process
	if doc.assignment_history:
		last_entry = doc.assignment_history[-1]
		last_entry.status = "Completed"
		last_entry.received_date = getdate()

		if last_entry.assigned_date:
			last_entry.days_taken = date_diff(getdate(), last_entry.assigned_date)

	# Assign to next
	doc.current_process = next_process
	doc.current_assignee = next_assignee
	doc.assigned_date = getdate()
	doc.required_days = required_days
	doc.required_days = required_days
	doc.actual_completion_date = None
	doc.received_date = None

	# Add to history
	doc.append("assignment_history", {
		"process_type": next_process,
		"assigned_to": next_assignee,
		"assigned_date": getdate(),
		"expected_date": add_days(getdate(), required_days),
		"status": "Assigned",
		"remarks": remarks
	})

	doc.save()
	frappe.db.commit()

	return {"success": True, "message": f"Transferred to {next_assignee} for {next_process}"}


@frappe.whitelist()
def get_overdue_items():
	"""
	Get all overdue items for dashboard/reports
	"""
	items = frappe.get_all(
		"Production Item Tracking",
		filters={"is_overdue": 1, "actual_completion_date": ["is", "not set"]},
		fields=[
			"name", "sales_order", "customer", "item_code", "item_name",
			"current_process", "current_assignee", "assigned_date",
			"expected_completion_date", "days_overdue"
		],
		order_by="days_overdue desc"
	)

	return items


@frappe.whitelist()
def bulk_assign(item_names, process_type, assignee, required_days, remarks=None):
	"""
	Bulk assign multiple items to same worker
	"""
	import json
	if isinstance(item_names, str):
		item_names = json.loads(item_names)

	results = []
	for item_name in item_names:
		try:
			result = assign_to_worker(item_name, process_type, assignee, required_days, remarks)
			results.append({"name": item_name, "success": True})
		except Exception as e:
			results.append({"name": item_name, "success": False, "error": str(e)})

	return results


def update_all_overdue_status():
	"""
	Scheduled function to update overdue status for all incomplete Production Item Tracking records.
	This runs daily at 1:00 AM to keep the database synchronized.
	Called from hooks.py scheduler_events.
	Updates database directly without creating activity logs.
	"""
	from frappe.utils import getdate, date_diff
	
	frappe.logger().info("Starting daily overdue status update for Production Item Tracking")
	
	# Get all incomplete records with expected completion dates
	items = frappe.get_all(
		"Production Item Tracking",
		filters={
			"actual_completion_date": ["is", "not set"]
		},
		fields=["name", "expected_completion_date"],
		limit_page_length=0
	)
	
	if not items:
		frappe.logger().info("No incomplete items found to update")
		return
	
	updated_count = 0
	error_count = 0
	today = getdate()
	
	for item in items:
		try:
			# First check if received_date is set (Partially Completed)
			received_date = frappe.db.get_value("Production Item Tracking", item.name, "received_date")
			
			if received_date:
				# Partially Completed items are never overdue
				is_overdue = 0
				days_overdue = 0
				overall_status = "Partially Completed"
			elif item.expected_completion_date:
				# Calculate overdue status
				expected_date = getdate(item.expected_completion_date)
				
				if today > expected_date:
					# Overdue
					is_overdue = 1
					days_overdue = date_diff(today, expected_date)
					overall_status = "Overdue"
				else:
					# Not overdue
					is_overdue = 0
					days_overdue = 0
					# Check if in progress or not started
					current_assignee = frappe.db.get_value("Production Item Tracking", item.name, "current_assignee")
					overall_status = "In Progress" if current_assignee else "Not Started"
			else:
				# No expected date
				is_overdue = 0
				days_overdue = 0
				current_assignee = frappe.db.get_value("Production Item Tracking", item.name, "current_assignee")
				overall_status = "In Progress" if current_assignee else "Not Started"
			
			# Update database directly without triggering document events
			# This avoids creating activity logs and version history
			frappe.db.set_value(
				"Production Item Tracking",
				item.name,
				{
					"is_overdue": is_overdue,
					"days_overdue": days_overdue,
					"overall_status": overall_status
				},
				update_modified=False  # Don't update modified timestamp
			)
			
			updated_count += 1
			
			# Commit in batches of 50 to avoid long transactions
			if updated_count % 50 == 0:
				frappe.db.commit()
				
		except Exception as e:
			error_count += 1
			frappe.logger().error(f"Error updating {item.name}: {str(e)}")
			continue
	
	# Final commit
	frappe.db.commit()
	
	frappe.logger().info(
		f"Completed daily overdue status update: "
		f"{updated_count} items updated, {error_count} errors"
	)
