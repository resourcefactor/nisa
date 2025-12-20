// Copyright (c) 2025, RF and contributors
// For license information, please see license.txt

frappe.pages['production_timeline'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Production Timeline',
		single_column: true
	});

	frappe.production_timeline = new ProductionTimeline(page);
};

class ProductionTimeline {
	constructor(page) {
		this.page = page;
		this.setup_filters();
		this.setup_refresh_button();
		this.load_data();
	}

	setup_filters() {
		// Customer filter
		this.page.add_field({
			fieldname: 'customer',
			label: __('Customer'),
			fieldtype: 'Link',
			options: 'Customer',
			change: () => this.load_data()
		});

		// Sales Order filter
		this.page.add_field({
			fieldname: 'sales_order',
			label: __('Sales Order'),
			fieldtype: 'Link',
			options: 'Sales Order',
			change: () => this.load_data()
		});

		// Status filter
		this.page.add_field({
			fieldname: 'overall_status',
			label: __('Status'),
			fieldtype: 'Select',
			options: '\nNot Started\nIn Progress\nCompleted\nOverdue',
			change: () => this.load_data()
		});

		// Process filter
		this.page.add_field({
			fieldname: 'current_process',
			label: __('Current Process'),
			fieldtype: 'Select',
			options: '\nPainter\nEmbellisher\nTailor\nDyer\nQuality Check\nReady for Delivery',
			change: () => this.load_data()
		});
	}

	setup_refresh_button() {
		this.page.set_primary_action(__('Refresh'), () => {
			this.load_data();
		}, 'octicon octicon-sync');
	}

	get_filters() {
		return {
			customer: this.page.fields_dict.customer.get_value(),
			sales_order: this.page.fields_dict.sales_order.get_value(),
			overall_status: this.page.fields_dict.overall_status.get_value(),
			current_process: this.page.fields_dict.current_process.get_value()
		};
	}

	load_data() {
		// Check if at least one mandatory filter (Sales Order or Customer) is provided
		const filters = this.get_filters();

		if (!filters.sales_order && !filters.customer) {
			this.page.main.html(`
				<div class="alert alert-warning" style="margin: 20px;">
					<strong>Filter Required:</strong> Please select either a Sales Order or Customer to load data.
				</div>
			`);
			return;
		}

		frappe.call({
			method: 'nisa.nisa.page.production_timeline.production_timeline.get_timeline_data',
			args: {
				filters: filters
			},
			callback: (r) => {
				if (r.message) {
					this.render_timeline(r.message);
				}
			}
		});
	}

	render_timeline(items) {
		let html = '<div class="production-timeline-container">';

		if (items.length === 0) {
			html += '<div class="alert alert-info">No items found matching the filters.</div>';
		} else {
			// Group by sales order
			let grouped = this.group_by_sales_order(items);

			for (let [sales_order, order_items] of Object.entries(grouped)) {
				html += this.render_sales_order_group(sales_order, order_items);
			}
		}

		html += '</div>';

		this.page.main.html(html);
		this.attach_event_handlers();
	}

	group_by_sales_order(items) {
		let grouped = {};
		items.forEach(item => {
			if (!grouped[item.sales_order]) {
				grouped[item.sales_order] = [];
			}
			grouped[item.sales_order].push(item);
		});
		return grouped;
	}

	render_sales_order_group(sales_order, items) {
		let customer = items[0].customer;
		let html = `
			<div class="sales-order-group" style="margin-bottom: 30px; border: 1px solid #d1d8dd; border-radius: 5px; padding: 15px; background: #f9fafb;">
				<h4 style="margin-top: 0;">
					<a href="/app/sales-order/${sales_order}" target="_blank">${sales_order}</a>
					<span style="color: #8d99a6; font-size: 14px; margin-left: 10px;">${customer}</span>
				</h4>
		`;

		items.forEach(item => {
			html += this.render_item_timeline(item);
		});

		html += '</div>';
		return html;
	}

	render_item_timeline(item) {
		let status_color = this.get_status_color(item.overall_status);
		let overdue_badge = item.is_overdue ? `<span class="badge badge-danger">Overdue ${item.days_overdue} days</span>` : '';

		let html = `
			<div class="item-timeline" style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
				<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
					<div>
						<strong><a href="/app/production-item-tracking/${item.name}" target="_blank">${item.item_name || item.item_code}</a></strong>
						<span style="color: #8d99a6; margin-left: 10px;">Qty: ${item.qty || 1}</span>
					</div>
					<div>
						<span class="badge" style="background-color: ${status_color};">${item.overall_status}</span>
						${overdue_badge}
					</div>
				</div>

				<div class="timeline-track" style="position: relative; height: 80px;">
					${this.render_timeline_track(item)}
				</div>

				<div style="margin-top: 10px; text-align: right;">
					<button class="btn btn-xs btn-default view-details" data-item="${item.name}">
						View Details
					</button>
					<button class="btn btn-xs btn-primary quick-update" data-item="${item.name}">
						Quick Update
					</button>
				</div>
			</div>
		`;

		return html;
	}

	render_timeline_track(item) {
		let processes = ['Dyer', 'Painter', 'Embellisher', 'Tailor', 'Quality Check', 'Out for Delivery'];
		let history_map = {};

		// Create a map of process history
		if (item.history) {
			item.history.forEach(h => {
				history_map[h.process_type] = h;
			});
		}

		let html = '<div style="display: flex; justify-content: space-between; align-items: center; height: 100%;">';

		processes.forEach((process, index) => {
			let history = history_map[process];
			let is_current = item.current_process === process;
			let is_completed = history && history.status === 'Completed';
			let is_in_progress = history && history.status === 'In Progress';

			let circle_class = 'timeline-circle-empty';
			let circle_color = '#d1d8dd';
			let worker_name = '';

			if (is_completed) {
				circle_class = 'timeline-circle-completed';
				circle_color = '#28a745';
				worker_name = history.assigned_to;
			} else if (is_in_progress || is_current) {
				circle_class = 'timeline-circle-current';
				circle_color = '#007bff';
				worker_name = item.current_assignee || history.assigned_to;
			}

			// Draw connecting line (except for first element)
			if (index > 0) {
				let line_color = is_completed || (is_current && processes.indexOf(item.current_process) > index) ? '#28a745' : '#d1d8dd';
				html += `<div style="flex: 1; height: 2px; background-color: ${line_color}; margin: 0 -1px;"></div>`;
			}

			// Draw circle and label
			html += `
				<div style="text-align: center; position: relative; z-index: 10;">
					<div style="
						width: 40px;
						height: 40px;
						border-radius: 50%;
						background-color: ${circle_color};
						border: 3px solid white;
						box-shadow: 0 2px 5px rgba(0,0,0,0.2);
						display: flex;
						align-items: center;
						justify-content: center;
						margin: 0 auto;
					">
						${is_completed ? '<span style="color: white;">✓</span>' : ''}
						${is_in_progress || is_current ? '<span style="color: white;">●</span>' : ''}
					</div>
					<div style="margin-top: 5px; font-size: 11px; font-weight: bold; color: #36414c;">
						${process}
					</div>
					${worker_name ? `<div style="font-size: 10px; color: #8d99a6;">${worker_name}</div>` : ''}
					${history && history.days_taken ? `<div style="font-size: 10px; color: #6c757d;">${history.days_taken} days</div>` : ''}
				</div>
			`;
		});

		html += '</div>';
		return html;
	}

	get_status_color(status) {
		const colors = {
			'Completed': '#28a745',
			'In Progress': '#007bff',
			'Overdue': '#dc3545',
			'Not Started': '#6c757d'
		};
		return colors[status] || '#6c757d';
	}

	attach_event_handlers() {
		// View Details button
		this.page.main.find('.view-details').on('click', (e) => {
			let item_name = $(e.currentTarget).data('item');
			frappe.set_route('Form', 'Production Item Tracking', item_name);
		});

		// Quick Update button
		this.page.main.find('.quick-update').on('click', (e) => {
			let item_name = $(e.currentTarget).data('item');
			this.show_quick_update_dialog(item_name);
		});
	}

	show_quick_update_dialog(item_name) {
		frappe.call({
			method: 'frappe.client.get',
			args: {
				doctype: 'Production Item Tracking',
				name: item_name
			},
			callback: (r) => {
				if (r.message) {
					let doc = r.message;

					let d = new frappe.ui.Dialog({
						title: __('Quick Update: {0}', [doc.item_name || doc.item_code]),
						fields: [
							{
								fieldname: 'action',
								fieldtype: 'Select',
								label: __('Action'),
								options: '\nMark Received\nComplete Process\nTransfer to Next',
								reqd: 1,
								onchange: function() {
									let action = d.get_value('action');
									d.fields_dict.transfer_section.df.hidden = (action !== 'Transfer to Next');
									d.refresh();
								}
							},
							{
								fieldname: 'transfer_section',
								fieldtype: 'Section Break',
								label: __('Transfer Details'),
								hidden: 1
							},
							{
								fieldname: 'next_process',
								fieldtype: 'Select',
								label: __('Next Process'),
								options: '\nDyer\nPainter\nEmbellisher\nTailor\nQuality Check\nOut for Delivery',
								depends_on: 'eval:doc.action=="Transfer to Next"'
							},
							{
								fieldname: 'next_assignee',
								fieldtype: 'Link',
								label: __('Assign To'),
								options: 'Supplier',
								depends_on: 'eval:doc.action=="Transfer to Next"'
							},
							{
								fieldname: 'required_days',
								fieldtype: 'Int',
								label: __('Required Days'),
								default: 5,
								depends_on: 'eval:doc.action=="Transfer to Next"'
							},
							{
								fieldname: 'remarks_section',
								fieldtype: 'Section Break'
							},
							{
								fieldname: 'remarks',
								fieldtype: 'Small Text',
								label: __('Remarks')
							}
						],
						primary_action_label: __('Update'),
						primary_action: (values) => {
							let method = '';

							if (values.action === 'Mark Received') {
								method = 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.mark_received';
							} else if (values.action === 'Complete Process') {
								method = 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.complete_process';
							} else if (values.action === 'Transfer to Next') {
								method = 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.transfer_to_next';
							}

							let args = {
								doc_name: item_name,
								remarks: values.remarks
							};

							if (values.action === 'Transfer to Next') {
								args.next_process = values.next_process;
								args.next_assignee = values.next_assignee;
								args.required_days = values.required_days;
							}

							frappe.call({
								method: method,
								args: args,
								callback: (r) => {
									if (r.message && r.message.success) {
										frappe.show_alert({
											message: r.message.message,
											indicator: 'green'
										});
										this.load_data();
									}
								}
							});

							d.hide();
						}
					});

					d.show();
				}
			}
		});
	}
}
