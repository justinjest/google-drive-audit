import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.activity.readonly"]

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "api_keys/credentils.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save credentials
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    service = build("driveactivity", "v2", credentials=creds)

    # Calling api here
    try:
        results = service.activity().query(body={"pageSize": 10}).execute()
        activities = results.get("activities", [])

        if not activities:
            print("No activity.")
        else:
            print("Recent activity:")
            for activity in activities:
                time = getTimeInfo(activity)
                action = getActionInfo(activity["primaryActionDetail"])
                actors = map(getActorInfo, activity["actors"])
                targets = map(getTargetInfo, activity["targets"])
                actors_str, targets_str = "", ""
                actor_name = actors_str.join(actors)
                target_name = targets_str.join(targets)

                # Print the action occurred on drive with actor, target item and timestamp
                print(f"{time}: {action}, {actor_name}, {target_name}")

    except HttpError as error:
        # TODO(developer) - Handleerrors from drive activity API.
        print(f"An error occurred: {error}")


    # Returns the name of a set property in an object, or else "unknown".
def getOneOf(obj):
    for key in obj:
        return key
    return "unknown"


# Returns a time associated with an activity.
def getTimeInfo(activity):
    if "timestamp" in activity:
        return activity["timestamp"]
    if "timeRange" in activity:
        return activity["timeRange"]["endTime"]
    return "unknown"


# Returns the type of action.
def getActionInfo(actionDetail):
    return getOneOf(actionDetail)


# Returns user information, or the type of user if not a known user.
def getUserInfo(user):
    if "knownUser" in user:
        knownUser = user["knownUser"]
        isMe = knownUser.get("isCurrentUser", False)
        return "people/me" if isMe else knownUser["personName"]
    return getOneOf(user)


# Returns actor information, or the type of actor if not a user.
def getActorInfo(actor):
    if "user" in actor:
        return getUserInfo(actor["user"])
    return getOneOf(actor)


# Returns the type of a target and an associated title.
def getTargetInfo(target):
    if "driveItem" in target:
        title = target["driveItem"].get("title", "unknown")
        return f'driveItem:"{title}"'
    if "drive" in target:
        title = target["drive"].get("title", "unknown")
        return f'drive:"{title}"'
    if "fileComment" in target:
        parent = target["fileComment"].get("parent", {})
        title = parent.get("title", "unknown")
        return f'fileComment:"{title}"'
        return f"{getOneOf(target)}:unknown"

if __name__ == "__main__":
    print ("Hello world")
    main()