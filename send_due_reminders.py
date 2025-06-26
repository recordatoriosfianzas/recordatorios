import pandas as pd
import datetime
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

CSV_FILE = "reminders.csv"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"

def send_reminder(email, name, client_number, expiry_date):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=email,
        subject="Guarantee Expiry Reminder",
        plain_text_content=f"Hello,\n\nYour guarantee with client {name} (ID: {client_number}) expires on {expiry_date}.\n\n"
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {email}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send to {email}: {e}")

def run():
    if not os.path.exists(CSV_FILE):
        print("No reminders.csv file found.")
        return

    df = pd.read_csv(CSV_FILE)
    today = datetime.datetime.utcnow().date().strftime('%Y-%m-%d')
    print(f"Checking reminders for {today}")

    for _, row in df.iterrows():
        if row['reminder_date'] == today:
            send_reminder(
                email=row['email'],
                name=row['name'],
                client_number=row['client_number'],
                expiry_date=row['expiry_date']
            )

if __name__ == "__main__":
    run()
