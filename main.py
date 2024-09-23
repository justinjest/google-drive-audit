import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def main():
    creds = validate_creds()
    # Calling api here
    try:
        files = []
        risk_detection = []
        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        print ("Starting to scan files")
        results = (
            service.files()
            .list(fields="files(id, name)")
            .execute()
    )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return
        print("Files:")
        for item in items:
            files.append((item['name'], item['id']))
            print(f"{item['name']} ({item['id']})")
        print ("Found all items")
        print ("Scanning for shared links")
        for file in files:
            file_roles = get_file_roles(file[1], creds)
            for item in file_roles:
                if {item['id']} == {'anyoneWithLink'}:
                    risk_detection.append(file[0])
        print ("Following files have an outstanding vulnerability")
        print(risk_detection)
        output_results (risk_detection)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")
# Authenticate and create the Drive API client

def validate_creds():
    creds = None
    print ("Conncecting to google drive")
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
    print ("Logged in, accessing API")
    return creds

# File -> Permision JSON
def get_file_roles(file_id, creds):
    try:
        service = build('drive', 'v3', credentials = creds)
        permissions = service.permissions().list(fileId=file_id).execute()
        
        roles = []
        for permission in permissions.get('permissions', []):
            roles.append({
                'id': permission.get('id'),
                'role': permission.get('role'),
                'emailAddress': permission.get('emailAddress', 'N/A')
            })
        # Returns user ID's of all accounts that have access

        return roles
    except:
        return []

def output_results(results):
    output_path = "results/output.txt"
    if not os.path.exists(output_path):
        with open (output_path, "x") as txt:
            txt.write("")
        print ("File created")
    with open(output_path, "w") as txt:
        txt.write("\n".join(results))

if __name__ == "__main__":
    main()