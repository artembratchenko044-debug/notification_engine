import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load variables from .env (for local testing)
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
ONESIGNAL_API_KEY = os.environ.get('ONESIGNAL_API_KEY')
# Your verified sender email in SendGrid
FROM_EMAIL = 'artem.bratchenko044@gmail.com' 

# Your new Template IDs
SENDGRID_TEMPLATE_ID = 'd-d11db0e0e1a745b29ad37f512cca3f3c'
ONESIGNAL_TEMPLATE_ID = 'c7feed75-c7ff-4e21-9554-44a502254a36'
ONESIGNAL_APP_ID = 'a10f1409-7129-4703-810f-dfcf43c7efb7'

@app.route('/event-webhook', methods=['POST'])
def handle_supabase_event():
    """
    This function catches the Webhook from Supabase.
    """
    payload = request.json
    
    # Supabase sends the new row data in the 'record' field
    record = payload.get('record', {})
    
    # Extract data from the new row (adjust keys to match your table columns)
    user_email = record.get('email')
    user_name = record.get('user_id', 'Valued Customer')
    event_name = record.get('event_name', 'New Activity')

    if not user_email:
        print("⚠️ Webhook received but no email found in record.")
        return jsonify({"error": "No email in record"}), 400

    print(f"🚀 Processing event: {event_name} for {user_email}")

    # 1. Trigger SendGrid Email
    email_status = send_sendgrid_email(user_email, user_name, event_name)
    
    # 2. Trigger OneSignal Push
    push_status = send_onesignal_push(event_name)

    return jsonify({
        "status": "processed",
        "email": email_status,
        "push": push_status
    }), 200

def send_sendgrid_email(to_email, name, event):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email
    )
    message.template_id = SENDGRID_TEMPLATE_ID
    # Pass variables to your Handlebars template
    message.dynamic_template_data = {
        "first_name": name,
        "event_type": event,
        "subject": f"Update: {event}"
    }
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email sent! Status: {response.status_code}")
        return "sent"
    except Exception as e:
        print(f"❌ SendGrid Error: {e}")
        return f"failed: {str(e)}"

def send_onesignal_push(event):
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    
    push_payload = {
        "app_id": ONESIGNAL_APP_ID,
        "template_id": ONESIGNAL_TEMPLATE_ID,
        "included_segments": ["Total Subscriptions"],
        # Your specific fixed custom_data logic
        "custom_data": {
            "event_name": event
        }
    }
    
    try:
        response = requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers=header,
            json=push_payload
        )
        print(f"✅ Push sent! Response: {response.text}")
        return "sent"
    except Exception as e:
        print(f"❌ OneSignal Error: {e}")
        return f"failed: {str(e)}"

if __name__ == "__main__":
    # Render uses the PORT env var
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


