# %%
import json
import requests
import msal
import re
from pathlib import Path
from datetime import datetime
from fotoviewer import INBOX, CLIENT_ID, CLIENT_SECRET, AUTHORITY, TOKEN_FILE, create_sub_dirs, date_time_file_prefix

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
    email_endpoint = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$filter=isDraft eq false&$select=id,subject,receivedDateTime"
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

def parse_graph_date(date_string):
    """Handle ISO 8601 date format returned by Microsoft Graph."""
    if date_string:
        try:
            # Remove 'Z' at the end and parse
            date_string = date_string.rstrip('Z')
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            print(f"Error parsing date: {date_string}")
    return None  # Return None if parsing fails or date is not present

def eml_file_name(subject, msg_date_time):
    """Construct new file name from date_time, sender and file_name"""
    eml_file_name = ""

    if msg_date_time is not None:
        eml_file_name = date_time_file_prefix(msg_date_time)
    return f"{sanitize_filename(f"{eml_file_name}_{subject}")}.eml"

def sanitize_filename(filename):
    """Sanitize file-name so it can be read"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

def save_as_emls(emails: dict, inbox: Path, access_token: str):
    for email_data in emails:
        subject = email_data.get("subject")
        msg_date_time = parse_graph_date(email_data.get("receivedDateTime"))
        message_id = email_data.get("id")

        
        url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/$value"

        headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/octet-stream"
        }

        response = requests.get(url, headers=headers)

        if response.ok:
            eml_file_path = inbox / eml_file_name(subject, msg_date_time)
            with open(eml_file_path, 'wb') as eml_file:
                eml_file.write(response.content)
            print(f"Email saved as: {eml_file_path}")


def read_mailbox(inbox: Path = INBOX):
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
    save_as_emls(emails=emails, inbox=inbox, access_token=access_token)