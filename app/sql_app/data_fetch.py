from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import googleapiclient
from app.secret import GPJSON, SPREADSHEETID

def read_old_laps(gp, rows):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(GPJSON, scope)

    service = build("sheets", "v4", credentials = creds)

    ark = service.spreadsheets()

    try:
        result = ark.values().get(spreadsheetId = SPREADSHEETID, range=f"{gp}!T{rows[0]}:Z{rows[1]}").execute()
        verdier = result.get("values", [])
        for value in verdier:
            value.append("Tromsø")
        return verdier
    except googleapiclient.errors.HttpError as e:
        print("Google API error:", e)
        return None

def read_mid_laps(gp, rows):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(GPJSON, scope)

    service = build("sheets", "v4", credentials = creds)

    ark = service.spreadsheets()

    try:
        result = ark.values().get(spreadsheetId = SPREADSHEETID, range=f"{gp}!U{rows[0]}:AB{rows[1]}").execute()
        verdier = result.get("values", [])
        return verdier
    except googleapiclient.errors.HttpError as e:
        print("Google API error:", e)
        return None
    
def read_new_laps(gp, rows):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(GPJSON, scope)

    service = build("sheets", "v4", credentials = creds)

    ark = service.spreadsheets()

    try:
        result = ark.values().get(spreadsheetId = SPREADSHEETID, range=f"{gp}!B{rows[0]}:I{rows[1]}").execute()
        verdier = result.get("values", [])
        return verdier
    except googleapiclient.errors.HttpError as e:
        print("Google API error:", e)
        return None

if __name__ == "__main__":
    read_old_laps("Skaustralia GP")