import streamlit as st
import pandas as pd
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Load API key from Streamlit Secrets
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"
CSV_FILE = "reminders.csv"

# --- Email sending function ---
def schedule_email(name, client_number, emails, expiry_date):
    reminder_date = expiry_date - datetime.timedelta(days=7)
    send_on = reminder_date.strftime('%Y-%m-%d')

    email_list = [e.strip() for e in emails.split(',') if e.strip()]
    failed = []

    for email in email_list:
        # Add to CSV
        new_entry = pd.DataFrame([{
            "name": name,
            "client_number": client_number,
            "email": email,
            "expiry_date": expiry_date.strftime('%Y-%m-%d'),
            "reminder_date": send_on
        }])

        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, new_entry], ignore_index=True)
        else:
            df = new_entry

        df.to_csv(CSV_FILE, index=False)

        # Prepare email
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=email,
            subject="Guarantee Expiry Reminder",
            plain_text_content=f"Hello,\n\nYour guarantee with client {name} (ID: {client_number}) expires on {expiry_date.strftime('%Y-%m-%d')}.\n\n"
        )

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            failed.append(email)
            st.error(f"Failed to send to {email}: {e}")

    return failed, send_on

# --- Streamlit UI ---
st.set_page_config(page_title="Guarantee Reminder Scheduler")
st.title("📅 Schedule a Guarantee Reminder")

name = st.text_input("Client")
client_number = st.text_input("Guarantee ID")
emails = st.text_input("Email(s) (comma-separated)")
expiry_date = st.date_input("Guarantee Expiration Date", format="YYYY/MM/DD")

if st.button("Schedule"):
    if name and client_number and emails and expiry_date:
        failed_emails, send_on = schedule_email(name, client_number, emails, expiry_date)
        if not failed_emails:
            st.success(f"Email(s) scheduled for {send_on}.")
        else:
            st.warning(f"Some emails failed: {', '.join(failed_emails)}")
    else:
        st.warning("Please fill in all fields.")
