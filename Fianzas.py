import streamlit as st
import pandas as pd
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Set up SendGrid API Key
SENDGRID_API_KEY = "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"
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"
CSV_FILE = "reminders.csv"

# --- Email sending function ---
def schedule_email(name, client_number, email_list, expiry_date):
    reminder_date = expiry_date - datetime.timedelta(days=7)
    send_on = reminder_date.strftime('%Y-%m-%d')

    # One row per recipient
    new_entries = pd.DataFrame([{
        "name": name,
        "client_number": client_number,
        "email": email,
        "expiry_date": expiry_date.strftime('%Y-%m-%d'),
        "reminder_date": send_on
    } for email in email_list])

    # Append to CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_entries], ignore_index=True)
    else:
        df = new_entries

    df.to_csv(CSV_FILE, index=False)

    # Send email now (for testing)
    success = True
    for email in email_list:
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=email,
            subject="Guarantee Expiry Reminder",
            plain_text_content=f"Hello {name},\n\nYour guarantee (ID: {client_number}) expires on {expiry_date.strftime('%Y-%m-%d')}.\n\n– Reminder App"
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            st.error(f"Failed to send to {email}: {e}")
            success = False

    return success, send_on

# --- Streamlit App UI ---
st.set_page_config(page_title="Guarantee Reminder Scheduler")
st.title("📅 Schedule a Guarantee Reminder")

name = st.text_input("Client")
client_number = st.text_input("Guarantee ID")
email_input = st.text_input("Email(s) (comma-separated)")
emails = [e.strip() for e in email_input.split(",") if e.strip()]
expiry_date = st.date_input("Guarantee Expiration Date", format="YYYY/MM/DD")

if st.button("Schedule"):
    if name and client_number and emails and expiry_date:
        success, send_on = schedule_email(name, client_number, emails, expiry_date)
        if success:
            st.success(f"Email scheduled for: {', '.join(emails)} on {send_on}.")
        else:
            st.error("Failed to schedule email(s).")
    else:
        st.warning("Please fill in all fields.")
