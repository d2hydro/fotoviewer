# %%
import json
import requests
import msal
import re
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
from fotoviewer import FOTOVIEWER_DATA_DIR, create_sub_dirs, date_time_file_prefix
import base64  # Import base64 module for decoding attachment content

# Constants
TOKEN_FILE = "tokens.json"
CLIENT_ID = "see secret.env"
CLIENT_SECRET = "see secret.env"
AUTHORITY = "https://login.microsoftonline.com/common"

# MSAL setup
app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

def load_tokens():
    try:
        with open(TOKEN_FILE, "r") as token_file:
            return json.load(token_file)
    except FileNotFoundError:
        return None

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as token_file:
        json.dump(tokens, token_file)

def refresh_access_token():
    print("Attempting to refresh access token...")
    tokens = load_tokens()
    if tokens:
        result = app.acquire_token_by_refresh_token(tokens['refresh_token'], 
                                                    scopes=["https://graph.microsoft.com/Mail.Read"])
        if "access_token" in result:
            print("Token refreshed successfully.")
            tokens.update(result)  # Update with new tokens
            save_tokens(tokens)    # Save updated tokens
            return result['access_token']
        else:
            print(f"Failed to refresh token: {result.get('error_description')}")
            return None
    print("No tokens found. Cannot refresh.")
    return None

def fetch_emails_from_microsoft_graph(access_token):
    """Fetch emails using Microsoft Graph API and OAuth access token, filter out deleted and irrelevant emails."""
    email_endpoint = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$filter=isDraft eq false"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(email_endpoint, headers=headers)
    
    if response.status_code == 200:
        emails = response.json().get('value', [])
        print("Emails fetched:", emails)
        return emails
    else:
        print(f"Error fetching emails: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Failed to retrieve emails. Status code: {response.status_code}")

# Handle ISO 8601 date format
def parse_graph_date(date_string):
    """Handle ISO 8601 date format returned by Microsoft Graph."""
    if date_string:
        try:
            # Remove 'Z' at the end and parse
            date_string = date_string.rstrip('Z')
            print(date_string)
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            print(f"Error parsing date: {date_string}")
    return None  # Return None if parsing fails or date is not present

def fetch_attachments(message_id, access_token):
    """Fetch attachments from Microsoft Graph API."""
    attachment_endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(attachment_endpoint, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        print(f"Failed to retrieve attachments for message {message_id}: {response.text}")
        return []

def add_attachments_to_message(msg, attachments):
    """Add fetched attachments to the email message."""
    for attachment in attachments:
        if attachment["@odata.type"] == "#microsoft.graph.fileAttachment":
            # Decode the Base64 contentBytes
            attachment_content = base64.b64decode(attachment['contentBytes'])
            attachment_name = attachment['name']
            
            # Add the attachment to the message
            msg.add_attachment(attachment_content, maintype='application', subtype='octet-stream', filename=attachment_name)

def process_emails_and_save_as_eml(emails, inbox: Path, archive: Path, datastore: Path, access_token, to_archive=False):
    """Process the emails from the Graph API and save them as .eml files."""
    for email_data in emails:
        subject = email_data.get("subject", "No Subject")
        date = email_data.get("receivedDateTime", None)
        print(date)
        # Parse email date
        msg_date_time = parse_graph_date(date)
        
        if not msg_date_time:
            print(f"Warning: No valid date found for email with subject '{subject}'. Using fallback date.")
            # Use a fallback timestamp (e.g., current time)
            msg_date_time = datetime.now()

        # Create EmailMessage from the fetched data
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email_data.get("from", {}).get("emailAddress", {}).get("address", "unknown@unknown.com")
        msg['To'] = email_data.get("toRecipients", [{}])[0].get("emailAddress", {}).get("address", "unknown@unknown.com")

        # Set body content
        body_content = email_data.get("body", {}).get("content", "")
        content_type = email_data.get("body", {}).get("contentType", "text")

        if content_type == "html":
            msg.add_alternative(body_content, subtype="html")
        else:
            msg.set_content(body_content)

        # Handle attachments
        message_id = email_data.get("id")
        if email_data.get("hasAttachments", False):
            attachments = fetch_attachments(message_id, access_token)
            add_attachments_to_message(msg, attachments)

        # Save and parse the email file using parse_eml
        eml_file_path = inbox / eml_file_name(subject, msg_date_time)  # Use 'msg_date_time' instead of 'date_time'
        with open(eml_file_path, 'wb') as eml_file:
            eml_file.write(msg.as_bytes())
        print(f"Email saved as: {eml_file_path}")

def eml_file_name(subject, msg_date_time):
    """Construct new file name from date_time, sender and file_name"""
    eml_file_name = ""

    if msg_date_time is not None:
        eml_file_name = date_time_file_prefix(msg_date_time)
    return f"{sanitize_filename(f"{eml_file_name}_{subject}")}.eml"

def sanitize_filename(filename):
    """Sanitize file-name so it can be read"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

def read_mailbox(inbox: Path, archive: Path, datastore: Path, to_archive=False):
    """Read mailbox using Microsoft Graph API and save emails as .eml files."""
    access_token = refresh_access_token()
    
    if access_token is None:
        raise ValueError(f"'access_token' should not be 'None'.")

    if inbox is None:
        raise FileNotFoundError(f"Inbox not found: {inbox}")
    else:
        create_sub_dirs(inbox.parent)

    try:
        emails = fetch_emails_from_microsoft_graph(access_token)
    except Exception as e:
        print(f"Failed to fetch emails: {e}")
        return

    # Pass 'access_token' to process_emails_and_save_as_eml
    process_emails_and_save_as_eml(emails, inbox, archive, datastore, access_token, to_archive)


# Example usage
if __name__ == "__main__":
    print("Starting to read mailbox...")
    inbox = FOTOVIEWER_DATA_DIR / "inbox"
    archive = FOTOVIEWER_DATA_DIR / "archive"
    datastore = FOTOVIEWER_DATA_DIR / "datastore"
    read_mailbox(inbox, archive, datastore, to_archive=True)




# %%
