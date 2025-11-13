# Copyright (c) 2025, RF and contributors
# For license information, please see license.txt

"""
Utility to sync Nisa workspace from JSON file to database.
Run this after any workspace JSON changes to ensure DB is updated.
"""

import frappe
import json
import os


def sync_workspace():
	"""Sync workspace from JSON file to database"""

	# Path to workspace JSON file
	workspace_path = frappe.get_app_path('nisa', 'nisa', 'workspace', 'nisa', 'nisa.json')

	if not os.path.exists(workspace_path):
		print(f"Workspace file not found at: {workspace_path}")
		return

	# Read workspace JSON
	with open(workspace_path, 'r') as f:
		workspace_data = json.load(f)

	workspace_name = workspace_data.get('name')

	# Check if workspace exists
	if frappe.db.exists('Workspace', workspace_name):
		print(f"Workspace '{workspace_name}' exists. Deleting old version...")
		frappe.delete_doc('Workspace', workspace_name, force=True)

	# Create new workspace
	print(f"Creating workspace '{workspace_name}'...")
	workspace_doc = frappe.get_doc(workspace_data)
	workspace_doc.insert(ignore_permissions=True)

	frappe.db.commit()
	print(f"✓ Workspace '{workspace_name}' synced successfully!")


def delete_workspace():
	"""Delete Nisa workspace from database"""
	workspace_name = 'Nisa'

	if frappe.db.exists('Workspace', workspace_name):
		print(f"Deleting workspace '{workspace_name}'...")
		frappe.delete_doc('Workspace', workspace_name, force=True)
		frappe.db.commit()
		print(f"✓ Workspace '{workspace_name}' deleted successfully!")
	else:
		print(f"Workspace '{workspace_name}' does not exist.")


if __name__ == '__main__':
	# This can be run from bench console
	sync_workspace()
