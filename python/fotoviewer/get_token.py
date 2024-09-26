# %%
from flask import Flask, request
import msal
import webbrowser

# Configuration
CLIENT_ID = ""
CLIENT_SECRET = ""
AUTHORITY = "https://login.microsoftonline.com/common"
REDIRECT_URI = "http://localhost:5006/getAToken"

app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

# Flask web server setup
flask_app = Flask(__name__)

@flask_app.route("/")
def login():
    auth_url = app.get_authorization_request_url(
        scopes=["https://graph.microsoft.com/Mail.Read"],
        redirect_uri=REDIRECT_URI
    )
    print(f"Visit this URL to log in: {auth_url}")
    webbrowser.open(auth_url)
    return "Redirecting to Microsoft login..."

@flask_app.route("/getAToken")
def authorized():
    auth_code = request.args.get('code')
    
    # Exchange the authorization code for an access token
    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=["https://graph.microsoft.com/Mail.Read"],
        redirect_uri=REDIRECT_URI
    )
    
    if "access_token" in result:
        return f"Access token: {result['access_token']}"
    else:
        return f"Error: {result.get('error_description')}"

if __name__ == "__main__":
    flask_app.run(port=5006)
# %%
