// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Item Tracking', {
	onload: function(frm) {
		// Set query filter for current_assignee to show only production suppliers
		frm.set_query('current_assignee', function() {
			return {
				filters: {
					'supplier_group': ['in', ['Painter', 'Embellisher', 'Tailor', 'Dyer']]
				}
			};
		});
	},

	refresh: function(frm) {
		// Add custom buttons based on status
		if (!frm.is_new()) {
			add_action_buttons(frm);
		}

		// Add color indicators for overdue items
		if (frm.doc.is_overdue) {
			frm.dashboard.set_headline_alert(
				`Overdue by ${frm.doc.days_overdue} days!`,
				'red'
			);
		}

		// Set field colors based on status
		set_field_colors(frm);
	},

	sales_order: function(frm) {
		// Auto-fetch items from sales order
		if (frm.doc.sales_order && !frm.doc.item_code) {
			show_item_selector(frm);
		}
	},

	assigned_date: function(frm) {
		calculate_dates(frm);
	},

	required_days: function(frm) {
		calculate_dates(frm);
	},

	expected_completion_date: function(frm) {
		if (frm.doc.assigned_date && frm.doc.expected_completion_date && !frm.doc.required_days) {
			// Calculate required days from dates
			let days = frappe.datetime.get_day_diff(frm.doc.expected_completion_date, frm.doc.assigned_date);
			frm.set_value('required_days', days);
		}
	}
});

function add_action_buttons(frm) {
	// Remove existing custom buttons
	frm.clear_custom_buttons();

	if (frm.doc.overall_status !== 'Completed') {
		// Assign to Worker button
		frm.add_custom_button(__('Assign to Worker'), function() {
			show_assign_dialog(frm);
		}, __('Actions'));

		if (frm.doc.current_assignee) {
			// Mark Received button
			frm.add_custom_button(__('Mark Received'), function() {
				mark_received(frm);
			}, __('Actions'));

			// Complete Process button
			frm.add_custom_button(__('Complete Process'), function() {
				complete_process(frm);
			}, __('Actions'));

			// Transfer to Next button
			frm.add_custom_button(__('Transfer to Next'), function() {
				show_transfer_dialog(frm);
			}, __('Actions'));
		}
	}

	// Add refresh button for overdue items
	if (frm.doc.is_overdue) {
		frm.add_custom_button(__('View All Overdue'), function() {
			frappe.set_route('query-report', 'Overdue Production Items');
		});
	}
}

function show_assign_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Assign to Worker'),
		fields: [
			{
				fieldname: 'process_type',
				fieldtype: 'Select',
				label: __('Process Type'),
				options: '\nPainter\nEmbellisher\nTailor\nDyer\nQuality Check\nReady for Delivery',
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
		primary_action_label: __('Assign'),
		primary_action: function(values) {
			frappe.call({
				method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.assign_to_worker',
				args: {
					doc_name: frm.doc.name,
					process_type: values.process_type,
					assignee: values.assignee,
					required_days: values.required_days,
					remarks: values.remarks
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: r.message.message,
							indicator: 'green'
						});
						frm.reload_doc();
					}
				}
			});
			d.hide();
		}
	});
	d.show();
}

function show_transfer_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Transfer to Next Process'),
		fields: [
			{
				fieldname: 'next_process',
				fieldtype: 'Select',
				label: __('Next Process'),
				options: '\nPainter\nEmbellisher\nTailor\nDyer\nQuality Check\nReady for Delivery',
				reqd: 1
			},
			{
				fieldname: 'next_assignee',
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
		primary_action_label: __('Transfer'),
		primary_action: function(values) {
			frappe.call({
				method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.transfer_to_next',
				args: {
					doc_name: frm.doc.name,
					next_process: values.next_process,
					next_assignee: values.next_assignee,
					required_days: values.required_days,
					remarks: values.remarks
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: r.message.message,
							indicator: 'green'
						});
						frm.reload_doc();
					}
				}
			});
			d.hide();
		}
	});
	d.show();
}

function mark_received(frm) {
	frappe.prompt({
		label: __('Remarks'),
		fieldtype: 'Small Text',
		fieldname: 'remarks'
	}, function(values) {
		frappe.call({
			method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.mark_received',
			args: {
				doc_name: frm.doc.name,
				remarks: values.remarks
			},
			callback: function(r) {
				if (r.message && r.message.success) {
					frappe.show_alert({
						message: r.message.message,
						indicator: 'green'
					});
					frm.reload_doc();
				}
			}
		});
	}, __('Mark as Received'));
}

function complete_process(frm) {
	frappe.prompt({
		label: __('Remarks'),
		fieldtype: 'Small Text',
		fieldname: 'remarks'
	}, function(values) {
		frappe.call({
			method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.complete_process',
			args: {
				doc_name: frm.doc.name,
				remarks: values.remarks
			},
			callback: function(r) {
				if (r.message && r.message.success) {
					frappe.show_alert({
						message: r.message.message,
						indicator: 'green'
					});
					frm.reload_doc();
				}
			}
		});
	}, __('Complete Process'));
}

function calculate_dates(frm) {
	if (frm.doc.assigned_date && frm.doc.required_days && !frm.doc.expected_completion_date) {
		let expected = frappe.datetime.add_days(frm.doc.assigned_date, frm.doc.required_days);
		frm.set_value('expected_completion_date', expected);
	}
}

function set_field_colors(frm) {
	// Color code the overall status field
	if (frm.doc.overall_status === 'Overdue') {
		frm.fields_dict.overall_status.$wrapper.find('.control-value').css('color', 'red');
		frm.fields_dict.overall_status.$wrapper.find('.control-value').css('font-weight', 'bold');
	} else if (frm.doc.overall_status === 'Completed') {
		frm.fields_dict.overall_status.$wrapper.find('.control-value').css('color', 'green');
		frm.fields_dict.overall_status.$wrapper.find('.control-value').css('font-weight', 'bold');
	} else if (frm.doc.overall_status === 'In Progress') {
		frm.fields_dict.overall_status.$wrapper.find('.control-value').css('color', 'blue');
	}
}

function show_item_selector(frm) {
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Sales Order',
			name: frm.doc.sales_order
		},
		callback: function(r) {
			if (r.message && r.message.items) {
				let items = r.message.items;
				let item_list = items.map(item => {
					return {
						label: `${item.item_code} - ${item.item_name} (Qty: ${item.qty})`,
						value: item.item_code,
						description: item.description,
						qty: item.qty,
						row_name: item.name
					};
				});

				frappe.prompt([
					{
						fieldname: 'item',
						fieldtype: 'Select',
						label: __('Select Item'),
						options: item_list.map(i => i.value),
						reqd: 1
					}
				], function(values) {
					let selected = item_list.find(i => i.value === values.item);
					frm.set_value('item_code', selected.value);
					frm.set_value('qty', selected.qty);
					frm.set_value('sales_order_item_row', selected.row_name);
				}, __('Select Item from Sales Order'));
			}
		}
	});
}
