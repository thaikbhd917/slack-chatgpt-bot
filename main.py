import functions_framework
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
from threading import Thread
from flask import jsonify
import re
from google.cloud import firestore

OPENAPI_API_KEY= "#"
OPENAPI_ORGANIZATION_ID="#"
SLACK_APP_TOKEN = "#"
SLACK_APP_SECRET = "#"

# Initialize Firestore client
db = firestore.Client()

@functions_framework.http
def handler(request):
    print(request.headers)
    if "X-Slack-Retry-Num" in request.headers:
        return jsonify({'data':'OK'}), 200
    data = request.get_json()
    print(data)

    # check slack challenge
    if "challenge" in data:
        return data["challenge"]

    if data["event"]["type"]=="app_mention" and re.sub('<.*?>', '', data["event"]["text"]) != "":
        try:
            if re.sub('<.*?>', '', data["event"]["text"]).strip() == "/new":
                delete_messages(data["event"]["channel"])
                send_message_to_slack(":da:", data["event"]["channel"])
            else:
                background_thread = Thread(target=process_query, args=(re.sub('<.*?>', '', data["event"]["text"]), data["event"]["channel"]))
                background_thread.start()
        except Exception as e:
            print("handler unknown error", e)
            send_message_to_slack("<@U02HW6WEWB0> anh ơi em bị hỏng rồi :cry_2:", data["event"]["channel"])
    return jsonify({'data':'OK'}), 200
    
def process_query(query, channel_id):
    try:
        if get_messages(channel_id) is None:
            messages = [{"role": "user", "content": query}]
            answer = generate_answer(messages)
            print("answer: "+answer)
            send_message_to_slack(answer, channel_id)
            messages.append({"role": "assistant", "content": answer})
            set_messages(messages, channel_id)
        else:
            messages = get_messages(channel_id)
            messages.append({"role": "user", "content": query})
            answer = generate_answer(messages)
            print("answer: "+answer)
            send_message_to_slack(answer, channel_id)
            messages.append({"role": "assistant", "content": answer})
            set_messages(messages, channel_id)
    except Exception as e:
        print("query() error", e)
        send_message_to_slack("<@U02HW6WEWB0> anh ơi em bị hỏng rồi :cry_2:", channel_id)
    
def generate_answer(messages):
    try:
        openai.organization = OPENAPI_ORGANIZATION_ID
        openai.api_key = OPENAPI_API_KEY
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
    except Exception as e:
        print("generate_answer() error", e)
        raise Exception("error")
    print(response)
    return response["choices"][0]["message"]["content"]

def send_message_to_slack(message, channel_id):
    try:
        # Get Slack App Credentials
        client = WebClient(token=SLACK_APP_TOKEN)
        
        # Send message to Slack channel
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        print(f'Successfully sent message to channel {channel_id}')
    except Exception as e:
        print("Error sending message to Slack channel: {}".format(e))

# Set an array of messages in the 'messages' collection
def set_messages(messages, slack_channel_id):
    doc_ref = db.collection('messages').document(slack_channel_id)
    doc_ref.set({'messages': messages})
# Get an array of messages from the 'messages' collection
def get_messages(slack_channel_id):
    doc_ref = db.collection('messages').document(slack_channel_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()['messages']
    else:
        return None
# Delete a messages from the 'messages' collection
def delete_messages(slack_channel_id):
    doc_ref = db.collection('messages').document(slack_channel_id)
    doc_ref.delete()