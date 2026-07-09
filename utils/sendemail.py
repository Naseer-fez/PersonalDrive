import os
import requests
def Messages_to_send(to: str, content: str, subject: str):
    receiver = f"{to}@gmail.com" if "@" not in to else to
    
    api_key = os.getenv("EmailAPi")
    sender_email = os.getenv("sendemail")
    sender_name = os.getenv("sendemail", "TapNap Assistant")

    if not api_key or not sender_email:
        return [0,"Error: Email configuration missing in environment"]

    url = "https://api.brevo.com/v3/smtp/email"
    
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": receiver}],
        "replyTo": {"name": sender_name, "email": sender_email},
        "subject": subject,
        "textContent": content
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code in [200, 201, 202]:
            return [1]
        return [0,f"Error {response.status_code}: {response.text}"]
            
    except requests.exceptions.RequestException as e:
        return [0,str(e)]