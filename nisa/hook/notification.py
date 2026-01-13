
import frappe
import requests
from frappe import _, msgprint
import json
from frappe.email.doctype.notification.notification import Notification, get_context
from frappe.core.doctype.sms_settings.sms_settings import validate_receiver_nos
from frappe.utils.pdf import get_pdf
import base64
from io import BytesIO


class OvrNotification(Notification):
    def send(self, doc):
        """Build recipients and send Notification"""

        context = get_context(doc)
        context = {"doc": doc, "alert": self, "comments": None}
        if doc.get("_comments"):
            context["comments"] = json.loads(doc.get("_comments"))

        if self.is_standard:
            self.load_standard_properties(context)
        try:
            if self.channel == "Email":
                self.send_an_email(doc, context)

            if self.channel == "Slack":
                self.send_a_slack_msg(doc, context)

            if self.channel == "SMS":
                self.send_sms(doc, context)

            if self.channel == "WhatsApp":
                self.send_whatsapp(doc, context)

            if self.channel == "System Notification" or self.send_system_notification:
                self.create_system_notification(doc, context)

        except Exception:
            self.log_error("Failed to send Notification")

        if self.set_property_after_alert:
            allow_update = True
            if (
                    doc.docstatus.is_submitted()
                    and not doc.meta.get_field(self.set_property_after_alert).allow_on_submit
            ):
                allow_update = False
            try:
                if allow_update and not doc.flags.in_notification_update:
                    fieldname = self.set_property_after_alert
                    value = self.property_value
                    if doc.meta.get_field(fieldname).fieldtype in frappe.model.numeric_fieldtypes:
                        value = frappe.utils.cint(value)

                    doc.reload()
                    doc.set(fieldname, value)
                    doc.flags.updater_reference = {
                        "doctype": self.doctype,
                        "docname": self.name,
                        "label": _("via Notification"),
                    }
                    doc.flags.in_notification_update = True
                    doc.save(ignore_permissions=True)
                    doc.flags.in_notification_update = False
            except Exception:
                self.log_error("Document update failed")

    def send_whatsapp(self, doc, context):
        pdf_bytes = ''
        if self.attach_print:
            print_settings = frappe.get_doc("Print Settings", "Print Settings")
            html = frappe.get_print(doc.doctype, doc.name,
                                    doc=doc,
                                    print_format=self.print_format,
                                    letterhead=print_settings.with_letterhead)
            pdf_bytes = get_pdf(html)
        send_whatsapp_msg(
            receiver_list=self.get_receiver_list(doc, context),
            msg=frappe.render_template(self.message, context),
            attachments=pdf_bytes,
            is_attachment=self.attach_print,
            filename=f"{doc.doctype}-{doc.name}.pdf"
        )


@frappe.whitelist()
def send_whatsapp_msg(receiver_list, msg, attachments=None, is_attachment=False, filename=""):
    # ensure receiver_list is always a list
    if isinstance(receiver_list, str):
        try:
            receiver_list = json.loads(receiver_list)
        except Exception:
            receiver_list = [receiver_list]
    if not isinstance(receiver_list, list):
        receiver_list = [receiver_list]

    receiver_list = validate_receiver_nos(receiver_list)

    if not frappe.db.get_single_value("WhatsApp Setting", "enable"):
        frappe.msgprint(_("Please Enable <a href='/app/whatsapp-setting'><b>WhatsApp Setting</b></a>."), indicator='red')
        return

    setting = frappe.get_single("WhatsApp Setting")
    api_url = setting.url.rstrip("/")
    media_url = setting.media_url.rstrip("/")
    id_instance = setting.id_instance
    token = setting.token

    try:
        for rec in receiver_list:
            # ✅ determine chatId type
            chat_id = f"{rec}@c.us" if len(rec) == 12 else f"{rec}@g.us"
            if is_attachment:
                # ✅ build upload URL
                url = f"{media_url}/waInstance{id_instance}/sendFileByUpload/{token}"

                # ✅ payload — Green API expects caption + chatId only
                payload = {
                    "chatId": chat_id,
                    "caption": msg or ""
                }

                # ✅ DO NOT set Content-Type manually when using files
                files = [
                    ("file", (filename or "file.pdf", BytesIO(attachments), "application/pdf"))
                ]

                response = requests.post(url, data=payload, files=files, timeout=60)

            else:
                # ✅ simple message endpoint
                url = f"{api_url}/waInstance{id_instance}/sendMessage/{token}"
                payload = {
                    "chatId": chat_id,
                    "message": msg or ""
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, json=payload, headers=headers, timeout=60)

            # ✅ check response
            if response.status_code == 200:
                frappe.msgprint(_("WhatsApp message sent."), indicator='green', alert=True)
            else:
                frappe.log_error(
                    title="Green API Send Error",
                    message=f"URL: {url}\nStatus: {response.status_code}\nResponse: {response.text}"
                )
                frappe.msgprint(_("WhatsApp message send error. Check error log."),
                                indicator='red', alert=True)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "WhatsApp Send Exception")
        frappe.msgprint(_("WhatsApp message send error. Check error log."), indicator='red', alert=True)


