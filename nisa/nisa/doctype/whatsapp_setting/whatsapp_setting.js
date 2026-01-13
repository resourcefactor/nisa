// Copyright (c) 2026, RF and contributors
// For license information, please see license.txt

frappe.ui.form.on("WhatsApp Setting", {
 	refresh(frm) {
            frm.fields_dict.register_device.$input.addClass("btn-primary");
     	},
     	register_device(frm) {
             window.open('https://console.green-api.com/auth')
     	},
});
