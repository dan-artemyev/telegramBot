from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import constants

SCOPES = ['https://www.googleapis.com/auth/calendar']


def show_events(start_time, end_time):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # output
    event_list = []
    id_list = []
    date = constants.datePattern.search(start_time)
    id_list.extend(["<b>{2}/{1}/{0}</b>\n".format(date.group(1), date.group(2), date.group(3))])
    event_list.extend(["<b>{2}/{1}/{0}</b>\n".format(date.group(1), date.group(2), date.group(3))])
    if not events:
        event_list.extend(["No events found"])
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        answer = start + end + event['summary']
        answer = constants.outputPattern.search(answer)
        id_list.extend([event['id']])
        event_list.extend(["{0}-{1} {2}".format(answer.group(1), answer.group(2), answer.group(3))])
    return event_list, id_list


def delete_events(event_id):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return True


def add_events(start_time, end_time, name):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    event = {'summary': name, 'start': {'dateTime': start_time % constants.GMT},
             'end': {'dateTime': end_time % constants.GMT}}
    add = service.events().insert(calendarId='primary', sendNotifications=True, body=event).execute()
    if add:
        result = 'Successfully added {0}'.format(name)
    else:
        result = 'Error occurred'
    return result


def get_event(event_id):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    name = event['summary']
    return start, end, name


if __name__ == '__main__':
    print("It's just supporting module, run main.py")
