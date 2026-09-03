frappe.ui.form.on("Sales Order", {
	custom_shade_code: function (frm) {
		if (frm.doc.custom_shade_code) {
			frappe.db.get_value("Shades", frm.doc.custom_shade_code, "picture", function (r) {
				frm.set_value("custom_shade_picture", r && r.picture || null);
			});
		} else {
			frm.set_value("custom_shade_picture", null);
		}
	}
});
