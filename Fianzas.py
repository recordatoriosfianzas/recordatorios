import streamlit as st
import pandas as pd
import datetime
import base64
import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Environment Variables
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "reminders.csv")
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"

# --- Function to commit updated CSV to GitHub ---
def upload_csv_to_github(df):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"

    # Get current SHA if file exists
    res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = res.json().get("sha") if res.status_code == 200 else None

    content = df.to_csv(index=False).encode()
    b64_content = base64.b64encode(content).decode()

    data = {
        "message": "Update reminders.csv",
        "content": b64_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        data["sha"] = sha

    res = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if res.status_code not in [200, 201]:
        raise Exception(f"GitHub upload failed: {res.status_code} - {res.text}")

# --- Email Scheduling ---
def schedule_email(name, client_number, emails, expiry_date):
    reminder_date = expiry_date - datetime.timedelta(days=7)
    send_on = reminder_date.strftime('%Y-%m-%d')

    email_list = [e.strip() for e in emails.split(',') if e.strip()]
    failed = []

    # Load or create CSV
    try:
        res = requests.get(
            f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{CSV_FILE_PATH}"
        )
        df = pd.read_csv(pd.compat.StringIO(res.text)) if res.status_code == 200 else pd.DataFrame()
    except Exception:
        df = pd.DataFrame()

    for email in email_list:
        new_entry = {
            "name": name,
            "client_number": client_number,
            "email": email,
            "expiry_date": expiry_date.strftime('%Y-%m-%d'),
            "reminder_date": send_on
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

        try:
            message = Mail(
                from_email=SENDER_EMAIL,
                to_emails=email,
                subject="Guarantee Expiry Reminder",
                plain_text_content=(
                    f"Hello,\n\nYour guarantee with client {name} (ID: {client_number}) "
                    f"expires on {expiry_date.strftime('%Y-%m-%d')}.\n\n"
                )
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            failed.append(email)
            st.error(f"Failed to send to {email}: {e}")

    upload_csv_to_github(df)
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
