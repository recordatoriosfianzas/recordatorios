import streamlit as st
import pandas as pd
import datetime
import base64
import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load secrets from Streamlit Cloud
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # e.g., "username/repo"
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "reminders.csv")
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"

# 📤 Function to upload reminders.csv to GitHub
def upload_csv_to_github(df):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Get SHA if file exists
    res = requests.get(url, headers=headers)
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

    response = requests.put(url, json=data, headers=headers)
    if response.status_code not in [200, 201]:
        st.error(f"GitHub upload failed: {response.status_code}")
        st.text(response.text)

# 📬 Email and reminder scheduling
def schedule_email(name, client_number, emails, expiry_date):
    reminder_date = expiry_date - datetime.timedelta(days=7)
    send_on = reminder_date.strftime('%Y-%m-%d')
    today = datetime.date.today().strftime('%Y-%m-%d')

    email_list = [e.strip() for e in emails.split(',') if e.strip()]
    failed = []

    # Fetch existing CSV from GitHub
    try:
        csv_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{CSV_FILE_PATH}"
        r = requests.get(csv_url)
        if r.status_code == 200:
            df = pd.read_csv(pd.compat.StringIO(r.text))
        else:
            df = pd.DataFrame()
    except Exception as e:
        st.error("Error loading CSV")
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

        # Optional: send now if testing
        if send_on == today:
            try:
                message = Mail(
                    from_email=SENDER_EMAIL,
                    to_emails=email,
                    subject="Guarantee Expiry Reminder",
                    plain_text_content=(
                        f"Hello,\n\nYour guarantee for {name} (ID: {client_number}) "
                        f"expires on {expiry_date.strftime('%Y-%m-%d')}.\n"
                    )
                )
                SendGridAPIClient(SENDGRID_API_KEY).send(message)
            except Exception as e:
                failed.append(email)
                st.error(f"Failed to send to {email}: {e}")

    upload_csv_to_github(df)
    return failed, send_on

# ✅ Streamlit Web UI
st.set_page_config(page_title="Guarantee Reminder Scheduler")
st.title("📅 Schedule a Guarantee Reminder")

# 🔍 Optional test GitHub access button
if st.button("🔍 Test GitHub Access"):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"
    res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if res.status_code == 200:
        st.success("✅ GitHub access confirmed!")
    else:
        st.error(f"❌ GitHub access failed: {res.status_code}")
        st.text(res.text)

name = st.text_input("Client")
client_number = st.text_input("Guarantee ID")
emails = st.text_input("Email(s) (comma-separated)")
expiry_date = st.date_input("Guarantee Expiration Date", format="YYYY/MM/DD")

if st.button("Schedule"):
    if name and client_number and emails and expiry_date:
        failed_emails, send_on = schedule_email(name, client_number, emails, expiry_date)
        if not failed_emails:
            st.success(f"✅ Email(s) scheduled for {send_on}.")
        else:
            st.warning(f"⚠️ Failed for: {', '.join(failed_emails)}")
    else:
        st.warning("⚠️ Please complete all fields.")
