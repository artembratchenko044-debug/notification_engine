import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

message = Mail(
    from_email='artem.bratchenko044@gmail.com', # MUST BE VERIFIED
    to_emails='nova.shift1996@proton.me'    # Send to yourself to test
)
message.template_id = 'd-d11db0e0e1a745b29ad37f512cca3f3c'
message.dynamic_template_data = {
    "first_name": "Test",
    "event_name": "Manual Test"
}

try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(f"Status Code: {response.status_code}")
    print("Success! Check your inbox.")
except Exception as e:
    print(f"Error: {e}")