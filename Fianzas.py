import streamlit as st
import pandas as pd
import datetime
import os

SENDER_EMAIL = "recordatoriosfianzas@gmail.com"
CSV_FILE = "reminders.csv"

# --- Schedule reminder only ---
def schedule_email(name, client_number, emails, expiry_date):
    reminder_date = expiry_date - datetime.timedelta(days=7)
    send_on = reminder_date.strftime('%Y-%m-%d')

    email_list = [e.strip() for e in emails.split(',') if e.strip()]
    new_entries = []

    for email in email_list:
        new_entries.append({
            "name": name,
            "client_number": client_number,
            "email": email,
            "expiry_date": expiry_date.strftime('%Y-%m-%d'),
            "reminder_date": send_on
        })

    new_df = pd.DataFrame(new_entries)

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df

    df.to_csv(CSV_FILE, index=False)
    return send_on

# --- Streamlit UI ---
st.set_page_config(page_title="Guarantee Reminder Scheduler")
st.title("📅 Schedule a Guarantee Reminder")

name = st.text_input("Client")
client_number = st.text_input("Guarantee ID")
emails = st.text_input("Email(s) (comma-separated)")
expiry_date = st.date_input("Guarantee Expiration Date", format="YYYY/MM/DD")

if st.button("Schedule"):
    if name and client_number and emails and expiry_date:
        send_on = schedule_email(name, client_number, emails, expiry_date)
        st.success(f"Reminder saved. Emails will be sent on {send_on}.")
    else:
        st.warning("Please fill in all fields.")
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "rb") as file:
        st.download_button("📥 Download Reminders CSV", file, file_name="reminders.csv")
