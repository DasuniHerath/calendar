import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel
import sys

# If modifying the scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_user():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, log in
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
    
    return creds

def get_google_calendar_events():
    creds = authenticate_google_user()
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(calendarId='primary', 
                                          maxResults=10, 
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    event_list = []
    if not events:
        event_list.append('No upcoming events found.')
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # Check if 'summary' exists before appending
        summary = event.get('summary', 'No Title')
        event_list.append(f"{start}: {summary}")
    
    return event_list



