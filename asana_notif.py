import sys, os

import asana
import json
from six import print_
from pync import Notifier

from twilio.rest import TwilioRestClient


TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
ASANA_ACCESS_TOKEN = os.environ["ASANA_ACCESS_TOKEN"]
TWILIO_NUMBER = os.environ["TWILIO_NUMBER"]
OWN_NUMBER = os.environ["OWN_NUMBER"]


def get_my_tasks(client, asana_id):
	query_params = {
		"workspace": asana_id,
		"assignee": "me",
		"completed": False
	}
	return client.tasks.find_all(query_params)


def get_notif_string(event):
	if event["type"] == "task":
		resource_name = event["resource"]["name"]
		user_name = event["user"]["name"]
		action = event["action"]
		return user_name + "'s task: " + resource_name + " was " + action
	elif event["type"] == "project":
		return None
	elif event["type"] == "story":
		return None
	else:
		return "update on unhandled object"

twilio_client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
asana_client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

me = asana_client.users.me()
personal_projects = next(workspace for workspace in me['workspaces'] if workspace['name'] == 'Personal Projects')

projects = asana_client.projects.find_by_workspace(personal_projects['id'], iterator_type=None)
project = next(project for project in projects)
my_asana_id = me["id"]

while True:
	my_tasks = get_my_tasks(asana_client, my_asana_id)

	for event in asana_client.events.get_iterator({ 'resource': project["id"] }):
		print_("event", event)
		notif_string = get_notif_string(event)

		if notif_string is not None:
			print(notif_string)
			twilio_client.messages.create(body=notif_string,
			    to=OWN_NUMBER,
			    from_=TWILIO_NUMBER)



