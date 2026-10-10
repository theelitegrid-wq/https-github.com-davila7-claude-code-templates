"""One-time, on your own computer: prints the YT_REFRESH_TOKEN to store as a GitHub secret.

pip install google-auth-oauthlib
python automation/get_youtube_token.py path/to/client_secret.json
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    sys.argv[1], ["https://www.googleapis.com/auth/youtube.upload"]
)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print("\nYT_CLIENT_ID     =", creds.client_id)
print("YT_CLIENT_SECRET =", creds.client_secret)
print("YT_REFRESH_TOKEN =", creds.refresh_token)
