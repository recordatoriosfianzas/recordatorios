import streamlit as st
import pandas as pd
import datetime
import os

CSV_FILE = "reminders.csv"

st.set_page_config(page_title="Guarantee Reminder Scheduler")
st.title("📅 Schedule a Guarantee Reminder")

def schedule_email(name, client_number, email, expiry_date):
    reminder_date = expiry_date - datetime.timedelta(days=7)
    send_on = reminder_date.strftime('%Y-%m-%d')

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
    return send_on

# --- Streamlit Form ---
name = st.text_input("Client Name")
client_number = st.text_input("Guarantee ID")
email = st.text_input("Client Email")
expiry_date = st.date_input("Guarantee Expiration Date", format="YYYY/MM/DD")

if st.button("Schedule Reminder"):
    if name and client_number and email and expiry_date:
        send_on = schedule_email(name, client_number, email, expiry_date)
        st.success(f"📬 Reminder scheduled to be sent on: {send_on}")
    else:
        st.warning("Please fill in all the fields.")

