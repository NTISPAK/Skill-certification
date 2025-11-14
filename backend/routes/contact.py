from flask import Blueprint, request, jsonify, current_app
from email.message import EmailMessage
import smtplib
import ssl

contact_bp = Blueprint('contact', __name__)


def _normalize(value: str | None) -> str:
    return (value or '').strip()


@contact_bp.route('/contact/submit', methods=['POST'])
def submit_contact():
    data = request.get_json(silent=True) or {}

    name = _normalize(data.get('name'))
    email = _normalize(data.get('email'))
    phone = _normalize(data.get('phone'))
    subject = _normalize(data.get('subject')) or 'New Inquiry'
    message = _normalize(data.get('message'))

    errors: list[str] = []
    if not name:
        errors.append('Name is required.')
    if not email:
        errors.append('Email is required.')
    if not message:
        errors.append('Message is required.')

    if errors:
        return jsonify({'errors': errors}), 400

    app_config = current_app.config
    smtp_server = app_config.get('SMTP_SERVER')
    smtp_port = app_config.get('SMTP_PORT')
    smtp_username = app_config.get('SMTP_USERNAME')
    smtp_password = app_config.get('SMTP_PASSWORD')
    smtp_use_tls = app_config.get('SMTP_USE_TLS', True)
    recipient = app_config.get('CONTACT_RECIPIENT') or smtp_username

    if not all([smtp_server, smtp_port, smtp_username, smtp_password, recipient]):
        current_app.logger.error('SMTP configuration is incomplete. Skipping contact email send.')
        return jsonify({'error': 'Email service not configured.'}), 500

    email_body = (
        f"You have received a new message from the Skill-Cert contact form.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone or 'Not provided'}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n"
    )

    msg = EmailMessage()
    msg['Subject'] = f"Skill-Cert Contact: {subject}"
    msg['From'] = smtp_username
    msg['To'] = recipient
    msg['Reply-To'] = email
    msg.set_content(email_body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            if smtp_use_tls:
                smtp.starttls(context=context)
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg)
    except Exception as exc:  # pragma: no cover - log and hide internal details from response
        current_app.logger.exception('Failed to send contact email: %s', exc)
        return jsonify({'error': 'Failed to send message. Please try again later.'}), 500

    return jsonify({'message': 'Message sent successfully.'}), 200
