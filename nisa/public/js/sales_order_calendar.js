// Show Sales Order number + Customer name as the calendar event title,
// and add a button to print the whole calendar view.

if (frappe.views.calendar["Sales Order"]) {
	frappe.views.calendar["Sales Order"].field_map.title = "custom_calendar_title";
	frappe.views.calendar["Sales Order"].get_events_method = "nisa.nisa.sales_order.get_events";
}

frappe.views.CalendarView = class NisaSalesOrderCalendarView extends frappe.views.CalendarView {
	setup_page() {
		super.setup_page();
		if (this.doctype === "Sales Order") {
			this.page.add_inner_button(__("Print Calendar"), () => this.print_calendar());
			this.add_full_title_style();
		}
	}

	render() {
		super.render();
		if (this.doctype === "Sales Order") {
			this.$result.addClass("nisa-sales-order-calendar");
		}
	}

	add_full_title_style() {
		if (document.getElementById("nisa-calendar-full-title-style")) return;

		const style = document.createElement("style");
		style.id = "nisa-calendar-full-title-style";
		style.innerHTML = `
			.nisa-sales-order-calendar .fc-event .fc-title,
			.nisa-sales-order-calendar .fc-event .fc-content {
				white-space: normal !important;
				overflow: visible !important;
				text-overflow: unset !important;
				line-height: 1.3;
			}
			.nisa-sales-order-calendar .fc-day-grid-event {
				white-space: normal !important;
			}
		`;
		document.head.appendChild(style);
	}

	print_calendar() {
		// FullCalendar renders the day-grid as two absolutely-positioned tables
		// layered on top of each other. Browsers can't paginate absolutely
		// positioned content — the whole grid jumps to the next page as one
		// atomic block instead of splitting cleanly. So instead of printing
		// FullCalendar's own DOM, render a plain HTML table from the same
		// event data and print that in a new window.
		const fc = this.calendar && this.calendar.$cal;
		if (!fc) {
			window.print();
			return;
		}

		const view = fc.fullCalendar("getView");
		const start = view.start.clone();
		const end = view.end.clone();

		// Open the window synchronously (within the click handler) so popup
		// blockers don't reject it — it gets filled in once data arrives.
		const win = window.open("", "_blank");
		win.document.write("<p>Loading…</p>");
		win.document.close();

		frappe.call({
			method: "nisa.nisa.sales_order.get_events",
			args: {
				start: start.format("YYYY-MM-DD"),
				end: end.format("YYYY-MM-DD"),
			},
			callback: (r) => {
				this.write_print_window(win, view.title, start, end, r.message || []);
			},
		});
	}

	write_print_window(win, title, start, end, events) {
		const events_by_date = {};
		events.forEach((e) => {
			const date = e.delivery_date;
			if (!events_by_date[date]) events_by_date[date] = [];
			events_by_date[date].push(e.custom_calendar_title || `${e.name} - ${e.customer_name}`);
		});

		const week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
		let rows = "";
		const day = start.clone();
		while (day.isBefore(end)) {
			rows += "<tr>";
			for (let i = 0; i < 7; i++) {
				const date_str = day.format("YYYY-MM-DD");
				const titles = events_by_date[date_str] || [];
				const items = titles
					.map((t) => `<div class="event">${frappe.utils.escape_html(t)}</div>`)
					.join("");
				rows += `<td><div class="date-num">${day.date()}</div>${items}</td>`;
				day.add(1, "day");
			}
			rows += "</tr>";
		}

		const html = `
			<html>
			<head>
				<title>${frappe.utils.escape_html(title)}</title>
				<style>
					body { font-family: sans-serif; margin: 20px; }
					h2 { text-align: center; }
					table { width: 100%; border-collapse: collapse; }
					th, td {
						border: 1px solid #ccc;
						vertical-align: top;
						padding: 4px;
						width: 14.28%;
					}
					th { background: #f5f5f5; text-align: center; }
					.date-num { font-weight: bold; margin-bottom: 4px; }
					.event { font-size: 11px; color: #c0392b; margin-bottom: 2px; }
					tr { page-break-inside: avoid; }
				</style>
			</head>
			<body>
				<h2>${frappe.utils.escape_html(title)}</h2>
				<table>
					<thead><tr>${week_days.map((d) => `<th>${d}</th>`).join("")}</tr></thead>
					<tbody>${rows}</tbody>
				</table>
			</body>
			</html>
		`;

		win.document.open();
		win.document.write(html);
		win.document.close();

		let printed = false;
		const trigger_print = () => {
			if (printed) return;
			printed = true;
			win.focus();
			win.print();
		};
		win.onload = trigger_print;
		// Fallback in case "load" doesn't fire for a document.write()'d page.
		setTimeout(trigger_print, 300);
	}
};
