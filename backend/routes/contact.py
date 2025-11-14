from flask import Blueprint, request, jsonify, current_app
import requests

EMAILJS_ENDPOINT = 'https://api.emailjs.com/api/v1.0/email/send'

contact_bp = Blueprint('contact', __name__)


def _normalize(value: str | None) -> str:
    return (value or '').strip()


def _send_via_emailjs(config, payload: dict) -> None:
    service_id = config.get('EMAILJS_SERVICE_ID')
    template_id = config.get('EMAILJS_TEMPLATE_ID')
    public_key = config.get('EMAILJS_PUBLIC_KEY')
    private_key = config.get('EMAILJS_PRIVATE_KEY')
    origin = config.get('EMAILJS_ORIGIN')

    if not all([service_id, template_id, public_key, private_key]):
        raise RuntimeError('EmailJS configuration is incomplete.')

    request_body = {
        'service_id': service_id,
        'template_id': template_id,
        'user_id': public_key,
        'accessToken': private_key,
        'template_params': payload
    }

    headers = {
        'Origin': origin or 'http://localhost'
    }

    response = requests.post(EMAILJS_ENDPOINT, json=request_body, headers=headers, timeout=10)
    if response.status_code >= 400:
        current_app.logger.error(
            'EmailJS request failed (%s): %s', response.status_code, response.text
        )
        raise RuntimeError('EmailJS request failed')


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

    payload = {
        'name': name,
        'email': email,
        'phone': phone,
        'subject': subject,
        'message': message,
    }

    config = current_app.config

    try:
        _send_via_emailjs(config, payload)
    except Exception as exc:  # pragma: no cover
        current_app.logger.exception('EmailJS send failed: %s', exc)
        return jsonify({'error': 'Failed to send message. Please try again later.'}), 500

    return jsonify({'message': 'Message sent successfully.'}), 200
