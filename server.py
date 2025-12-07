import os
from flask import Flask, request, jsonify, send_from_directory
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__, static_folder='.', static_url_path='')

EMAIL_ADDRESS = 'primarnoplava@gmail.com'
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/submit', methods=['POST'])
def submit():
    if not EMAIL_PASSWORD:
        return jsonify({'error': 'Email password not configured', 'success': 'false'}), 500

    nick = request.form.get('nick')
    odgovor = request.form.get('odgovor')
    consent = request.form.get('consent')
    
    # Check for file
    voice_memo = request.files.get('attachment') 

    # Create email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    
    custom_subject = request.form.get('_subject')
    if custom_subject:
        msg['Subject'] = f"{custom_subject} - {nick}"
    else:
        msg['Subject'] = f"Novi odgovor od {nick}"

    body = f"Nick: {nick}\nOdgovor: {odgovor}\nConsent: {consent}"
    msg.attach(MIMEText(body, 'plain'))

    if voice_memo:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(voice_memo.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {voice_memo.filename}")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, text)
        server.quit()
        return jsonify({'message': 'Email sent successfully', 'success': 'true'})
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': str(e), 'success': 'false'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
