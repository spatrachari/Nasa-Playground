"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
import json
import random
from rapidconnect import RapidConnect
rapid = RapidConnect("FitVoice", "fbfab538-b442-42ab-bc4e-2861da68995f")

#print("{Title}\n{Image}\n{Description}".format(Title=title, Image=image_url, Description=description))

account_sid = "AC5f9d3cb624a7ef8592558e8b8ba94c7b"
auth_token = "39cc170b206a2efd90100db6c0a4711e"


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Send Nasa space facts by saying send space facts to phone number, " 
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Sorry, I couldn't quite catch that. You can send space facts by saying send space pictures to phone number"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Have a nice day! I hope to see you soon."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_phone_number_attributes(phone_number):
    return {"CallNumber": phone_number}


def set_number_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    rand_year = random.randint(2010,2016)
    rand_month = random.randint(1,12)
    rand_day = random.randint(1,28)

    our_date = '{Year}-{Month}-{Day}'.format(Year = rand_year, Month = rand_month, Day = rand_day)
    nasa = rapid.call('NasaAPI', 'getPictureOfTheDay', { 
        'apiKey': 'oIQ6aw0O6Fc9h5islHbO9c789S3sztX7DpOjmejq',
        'date': our_date, 
        'highResolution': ''
    })

    image_url = nasa['url']
    title = nasa['title']
    description = nasa['explanation']

    if 'PhoneNumber' in intent['slots']:
        phone_number = intent['slots']['PhoneNumber']['value']
        session_attributes = create_phone_number_attributes(phone_number)
        #speech_output = "Sending message to " + \
        #                phone_number + "Success!"
        
        try:
            resulttwo = rapid.call('Twilio', 'sendMms', { 
                'accountSid': account_sid,
                'accountToken': auth_token,
                'from': '+18584139533',
                'messagingServiceSid': '',
                'to': '+1{}'.format(phone_number),
                'body': '{Title}\nTaken on {Date}\n{Image}\n{Description}'.format(Title=title, Date=our_date,
                        Image=image_url, Description=description),
                'mediaUrl': image_url,
                'statusCallback': '',
                'applicationSid': '',
                'maxPrice': '',
                'provideFeedback': ''
             
            })
        except:
            should_end_session = True
            pass

        speech_output = "Here is " + title +\
                         "........ The description reads" + description
        reprompt_text = ""
        
    else:
        speech_output = "I'm sorry, I couldn't quite catch that. " \
                        "Could you please repeat the number."
        reprompt_text = "I'm sorry, I couldn't quite catch that. " \
                        "Sorry, I couldn't quite catch that. You can send space facts by saying send space pictures to phone number"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_number_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "CallNumber" in session.get('attributes', {}):
        phone_number = session['attributes']['CallNumber']
        speech_output = "The number you requested to send a message to is " + phone_number + \
                        ". Come back soon."
        should_end_session = True
    else:
        speech_output = "Sorry, I couldn't quite catch that. You can send space facts by saying send space pictures to phone number"
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PhoneNumberIsIntent":
        return set_number_in_session(intent, session)
    elif intent_name == "WhatsPhoneNumberIntent":
        return get_number_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
