import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "api_keys/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save credentials
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    # Calling api here
    try:
        files = []
        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        results = (
            service.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
    )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return
        print("Files:")
        for item in items:
            files.append(item['id'])
            print(f"{item['name']} ({item['id']})")

        for file in files:
            print (results.get(file, []))

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")

# File -> Permision JSON
def getPermissions(file):
    result = file.list("permissions(id)")
    return result

if __name__ == "__main__":
    print ("Hello world")
    main()