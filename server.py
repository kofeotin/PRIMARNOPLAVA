import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_url_path='', static_folder='.')

# --- CONFIGURATION ---
# PLEASE UPDATE THESE VALUES WITH YOUR EMAIL CREDENTIALS
# For Gmail, you likely need an App Password if 2FA is enabled.
# See: https://support.google.com/accounts/answer/185833
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'primarnoplava@gmail.com')
# Use an environment variable or replace 'YOUR_APP_PASSWORD_HERE' with your actual password
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'YOUR_APP_PASSWORD_HERE')
EMAIL_RECIPIENT = 'primarnoplava@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/submit', methods=['POST'])
def submit():
    nick = request.form.get('nick')
    answer = request.form.get('odgovor')
    consent = request.form.get('consent')
    audio_file = request.files.get('audio')

    print(f"Received submission from {nick}")

    # Construct email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = f"New Answer from {nick}"

    body = f"""
    Nick: {nick}
    Answer: {answer}
    Consent: {consent}
    """
    msg.attach(MIMEText(body, 'plain'))

    if audio_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(audio_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {audio_file.filename}")
        msg.attach(part)

    try:
        # Check if password is set to default
        if EMAIL_PASSWORD == 'YOUR_APP_PASSWORD_HERE':
             error_msg = "Error: Email password not configured. Please set EMAIL_PASSWORD environment variable or update server.py."
             print(error_msg)
             return jsonify({'error': error_msg}), 500

        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        print("Logging in...")
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        print("Sending email...")
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, text)
        server.quit()
        print("Email sent successfully.")
        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)
