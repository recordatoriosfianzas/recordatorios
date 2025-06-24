import pandas as pd
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = "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"
SENDER_EMAIL = "recordatoriosfianzas@gmail.com"
CSV_FILE = "reminders.csv"

def send_reminders():
    today = datetime.date.today().strftime('%Y-%m-%d')
    try:
        df = pd.read_csv(CSV_FILE)
        due_today = df[df['reminder_date'] == today]

        for _, row in due_today.iterrows():
            message = Mail(
                from_email=SENDER_EMAIL,
                to_emails=row['email'],
                subject="Guarantee Expiry Reminder",
                plain_text_content=f"Hello {row['name']},\n\nYour guarantee (ID: {row['client_number']}) expires on {row['expiry_date']}.\n\n– Reminder App"
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            print(f"✅ Email sent to {row['email']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_reminders()