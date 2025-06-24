import pandas as pd
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Load SendGrid API key from environment variable (GitHub Actions uses this)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"
CSV_FILE = "reminders.csv"

def send_email(to_email, subject, body):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

def run_scheduler():
    if not os.path.exists(CSV_FILE):
        print("No reminder file found.")
        return

    today = datetime.date.today().strftime('%Y-%m-%d')
    df = pd.read_csv(CSV_FILE)

    # Filter for reminders due today
    due_today = df[df['reminder_date'] == today]

    for _, row in due_today.iterrows():
        subject = "Guarantee Expiry Reminder"
        body = (
            f"Hello,\n\n"
            f"Your guarantee with client {row['name']} (ID: {row['client_number']}) "
            f"expires on {row['expiry_date']}.\n\n– Reminder App"
        )
        try:
            send_email(row['email'], subject, body)
            print(f"✅ Email sent to {row['email']}")
        except Exception as e:
            print(f"❌ Failed to send to {row['email']}: {e}")

if __name__ == "__main__":
    run_scheduler()
