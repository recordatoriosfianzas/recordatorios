import pandas as pd
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

CSV_FILE = "reminders.csv"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"

def send_reminders():
    if not os.path.exists(CSV_FILE):
        print("No reminders.csv file found.")
        return

    df = pd.read_csv(CSV_FILE)
    today = datetime.date.today().strftime('%Y-%m-%d')
    due = df[df["reminder_date"] == today]

    print(f"Today's date: {today}")
    print(f"Found {len(due)} reminders due today.")

    for _, row in due.iterrows():
        to_email = row["email"]
        subject = "Reminder: Guarantee Expiration"
        content = f"Hi,\n\nYour guarantee with client {row['name']} (ID: {row['client_number']}) expires on {row['expiry_date']}."

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content
        )

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Error sending to {to_email}: {e}")

if __name__ == "__main__":
    send_reminders()
