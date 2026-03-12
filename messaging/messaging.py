# vim: ts=2 sw=2 sts=2 et ai
"""Server Side FCM sample.

Firebase Cloud Messaging (FCM) can be used to send messages to clients on iOS,
Android and Web.

This sample uses FCM to send two types of messages to clients that are subscribed
to the `news` topic. One type of message is a simple notification message (display message).
The other is a notification message (display notification) with platform specific
customizations. For example, a badge is added to messages that are sent to iOS devices.
"""

import argparse
import json
import requests
import google.auth.transport.requests

from google.oauth2 import service_account

# Project Id will be detected from service account key
PROJECT_ID = '<YOUR-PROJECT-ID>'
BASE_URL = 'https://fcm.googleapis.com'
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# [START retrieve_access_token]
def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  # https://cloud.google.com/docs/authentication/application-default-credentials?hl=en#order
  credentials, project = google.auth.default()
  scoped_credentials = credentials.with_scopes(SCOPES)
  request = google.auth.transport.requests.Request()
  scoped_credentials.refresh(request)

  fcm_endpoint = f'v1/projects/{project}/messages:send'
  fcm_url = BASE_URL + '/' + fcm_endpoint

  return fcm_url, scoped_credentials.token
# [END retrieve_access_token]

def _send_fcm_message(fcm_message):
  """Send HTTP request to FCM with given message.

  Args:
    fcm_message: JSON object that will make up the body of the request.
  """
  fcm_url, token =  _get_access_token()
  auth = "Bearer " + token

  # [START use_access_token]
  headers = {
    'Authorization': auth,
    'Content-Type': 'application/json; UTF-8',
  }
  # [END use_access_token]
  resp = requests.post(fcm_url, data=json.dumps(fcm_message), headers=headers)

  if resp.status_code == 200:
    print('Message sent to Firebase for delivery, response:')
    print(resp.text)
  else:
    print('Unable to send message to Firebase')
    print(resp)
    print(resp.text)

def _build_common_message(token, fcmv1):
  """Construct common notifiation message.

  Construct a JSON object that will be used to define the
  common parts of a notification message that will be sent
  to any app instance subscribed to the news topic.
  """

  notification =  {
    'title': 'FCM Notification',
    'body': 'Notification from FCM'
  }
  if fcmv1:
    # https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages/send
    return {
      'message': {
        'token': token,
        'notification': notification,
        "android":{
          "priority":"high"
        }
      }
    }
  else:
    # https://firebase.google.com/docs/cloud-messaging/http-server-ref#downstream-http-messages-json
    return {
      'to':  token,
      'data': notification
    }

def _build_override_message(token, use_fcmv1):
  """Construct common notification message with overrides.

  Constructs a JSON object that will be used to customize
  the messages that are sent to iOS and Android devices.
  """
  fcm_message = _build_common_message(token, use_fcmv1)

  apns_override = {
    'payload': {
      'aps': {
        'badge': 1
      }
    },
    'headers': {
      'apns-priority': '10'
    }
  }

  android_override = {
    'notification': {
      'click_action': 'android.intent.action.MAIN'
    }
  }

  fcm_message['message']['android'] = android_override
  fcm_message['message']['apns'] = apns_override

  return fcm_message

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--message')
  parser.add_argument('--token')
  args = parser.parse_args()
  use_fcmv1 = True

  if args.message and args.message == 'common-message':
    common_message = _build_common_message(args.token, use_fcmv1)
    print('FCM request body for message using common notification object:')
    print(json.dumps(common_message, indent=2))
    _send_fcm_message(common_message)
  elif args.message and args.message == 'override-message':
    override_message = _build_override_message(args.token, use_fcmv1)
    print('FCM request body for override message:')
    print(json.dumps(override_message, indent=2))
    _send_fcm_message(override_message)
  else:
    print('''Invalid command. Please use one of the following commands:
python messaging.py --message=common-message
python messaging.py --message=override-message''')

if __name__ == '__main__':
  main()
