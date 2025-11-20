// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.listview_settings['Production Item Tracking'] = {
	add_fields: ['overall_status', 'is_overdue', 'current_process', 'current_assignee', 'days_overdue'],

	get_indicator: function(doc) {
		if (doc.overall_status === 'Completed') {
			return [__('Completed'), 'green', 'overall_status,=,Completed'];
		} else if (doc.overall_status === 'Overdue') {
			return [__('Overdue'), 'red', 'overall_status,=,Overdue'];
		} else if (doc.overall_status === 'In Progress') {
			return [__('In Progress'), 'blue', 'overall_status,=,In Progress'];
		} else {
			return [__('Not Started'), 'gray', 'overall_status,=,Not Started'];
		}
	},

	formatters: {
		current_assignee: function(value, df, doc) {
			if (value && doc.current_process) {
				return `${value} <span class="text-muted">(${doc.current_process})</span>`;
			}
			return value || '-';
		},
		days_overdue: function(value, df, doc) {
			if (doc.is_overdue && value > 0) {
				return `<span class="text-danger">${value} days</span>`;
			}
			return '-';
		}
	},

	onload: function(listview) {
		// Add bulk actions
		listview.page.add_inner_button(__('Bulk Assign'), function() {
			let selected = listview.get_checked_items();
			if (selected.length === 0) {
				frappe.msgprint(__('Please select items to assign'));
				return;
			}
			show_bulk_assign_dialog(selected);
		});

		// Add filter shortcuts
		listview.page.add_button(__('Show Overdue'), function() {
			listview.filter_area.clear();
			listview.filter_area.add([[listview.doctype, 'is_overdue', '=', 1]]);
		}, 'btn-default btn-sm');

		listview.page.add_button(__('Show In Progress'), function() {
			listview.filter_area.clear();
			listview.filter_area.add([[listview.doctype, 'overall_status', '=', 'In Progress']]);
		}, 'btn-default btn-sm');
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
				get_query: function() {
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
		primary_action: function(values) {
			frappe.call({
				method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.bulk_assign',
				args: {
					item_names: item_names,
					process_type: values.process_type,
					assignee: values.assignee,
					required_days: values.required_days,
					remarks: values.remarks
				},
				callback: function(r) {
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
