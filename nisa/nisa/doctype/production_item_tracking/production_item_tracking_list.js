// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.listview_settings['Production Item Tracking'] = {
	add_fields: ['overall_status', 'is_overdue', 'current_process', 'current_assignee', 'days_overdue', 'expected_completion_date', 'actual_completion_date'],

	get_indicator: function (doc) {
		if (doc.overall_status === 'Completed') {
			return [__('Completed'), 'green', 'overall_status,=,Completed'];
		} else if (doc.overall_status === 'Overdue') {
			return [__('Overdue'), 'red', 'overall_status,=,Overdue'];
		} else if (doc.overall_status === 'In Progress') {
			return [__('In Progress'), 'blue', 'overall_status,=,In Progress'];
		} else if (doc.overall_status === 'Partially Completed') {
			return [__('Partially Completed'), 'orange', 'overall_status,=,Partially Completed'];
		} else {
			return [__('Not Started'), 'gray', 'overall_status,=,Not Started'];
		}
	},

	formatters: {
		overall_status: function (value, df, doc) {
			// Calculate real-time status for list view display
			if (doc.actual_completion_date) {
				return '<span class="indicator-pill green">Completed</span>';
			}

			if (doc.expected_completion_date) {
				let today = frappe.datetime.get_today();
				let expected_date = doc.expected_completion_date;

				// Check if overdue
				if (frappe.datetime.get_day_diff(today, expected_date) > 0) {
					let days = frappe.datetime.get_day_diff(today, expected_date);
					return `<span class="indicator-pill red" title="${days} days overdue">Overdue</span>`;
				}
			}

			if (doc.current_assignee) {
				return '<span class="indicator-pill blue">In Progress</span>';
			}

			if (doc.overall_status === 'Partially Completed') {
				return '<span class="indicator-pill orange">Partially Completed</span>';
			}

			return '<span class="indicator-pill gray">Not Started</span>';
		},
		current_assignee: function (value, df, doc) {
			if (value && doc.current_process) {
				return `${value} <span class="text-muted">(${doc.current_process})</span>`;
			}
			return value || '-';
		},
		days_overdue: function (value, df, doc) {
			// Calculate real-time days overdue for list view
			if (doc.expected_completion_date && !doc.actual_completion_date) {
				let today = frappe.datetime.get_today();
				let expected_date = doc.expected_completion_date;

				if (frappe.datetime.get_day_diff(today, expected_date) > 0) {
					let days = frappe.datetime.get_day_diff(today, expected_date);
					return `<span class="text-danger">${days} days</span>`;
				}
			}
			return '-';
		}
	},

	onload: function (listview) {
		// Add bulk actions
		listview.page.add_inner_button(__('Bulk Assign'), function () {
			let selected = listview.get_checked_items();
			if (selected.length === 0) {
				frappe.msgprint(__('Please select items to assign'));
				return;
			}
			show_bulk_assign_dialog(selected);
		});
	}
};

function show_bulk_assign_dialog(items) {
	let item_names = items.map(item => item.name);

	let d = new frappe.ui.Dialog({
		title: __('Bulk Assign Items'),
		fields: [
			{
				fieldname: 'selected_items',
				fieldtype: 'HTML',
				options: `<div class="alert alert-info">
					<b>${items.length} items selected</b><br>
					${items.map(i => i.item_name || i.item_code).join(', ')}
				</div>`
			},
			{
				fieldname: 'process_type',
				fieldtype: 'Select',
				label: __('Process Type'),
				options: '\nDyer\nPainter\nEmbellisher\nTailor\nQuality Check\nOut for Delivery',
				reqd: 1
			},
			{
				fieldname: 'assignee',
				fieldtype: 'Link',
				label: __('Assign To'),
				options: 'Supplier',
				reqd: 1,
				get_query: function () {
					return {
						filters: {
							'supplier_group': ['in', ['Painter', 'Embellisher', 'Tailor', 'Dyer']]
						}
					};
				}
			},
			{
				fieldname: 'required_days',
				fieldtype: 'Int',
				label: __('Required Days'),
				reqd: 1,
				default: 5
			},
			{
				fieldname: 'remarks',
				fieldtype: 'Small Text',
				label: __('Remarks')
			}
		],
		primary_action_label: __('Assign All'),
		primary_action: function (values) {
			frappe.call({
				method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.bulk_assign',
				args: {
					item_names: item_names,
					process_type: values.process_type,
					assignee: values.assignee,
					required_days: values.required_days,
					remarks: values.remarks
				},
				callback: function (r) {
					if (r.message) {
						let success_count = r.message.filter(i => i.success).length;
						let failed_count = r.message.filter(i => !i.success).length;

						if (failed_count > 0) {
							frappe.msgprint({
								title: __('Bulk Assignment Results'),
								message: `${success_count} items assigned successfully. ${failed_count} items failed.`,
								indicator: 'orange'
							});
						} else {
							frappe.show_alert({
								message: `${success_count} items assigned successfully`,
								indicator: 'green'
							});
						}
						cur_list.refresh();
					}
				}
			});
			d.hide();
		}
	});
	d.show();
}
