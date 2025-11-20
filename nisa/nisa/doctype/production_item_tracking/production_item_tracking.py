# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff


class ProductionItemTracking(Document):
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
	doc.actual_completion_date = None

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
	doc.actual_completion_date = None

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
