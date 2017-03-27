from flask import jsonify, json, current_app, request, make_response
import requests
from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from .. import db
from ..models import User, SessionLevel

from . import api_v1


@api_v1.route('/', methods=['POST', 'GET'])
def index():
    return jsonify({"message":"ok"})


@api_v1.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", None)
    serviceCode = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", None)

    text_array = text.split("*")
    user_response = text_array[len(text_array)-1]

    lowerUserLevels = {
        "0": home,
        "1": please_call,
        "2": deposit,
        "3": withdraw,
        "4": send_money,
        "5": buy_airtime,
        "6": pay_loan,
        "default": default_menu
    }
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        session_level = SessionLevel.query.filter_by(session_id=session_id).first()
        if session_level:
            if user_response:
                if session_level.level == 1 or session_level.level == 0:
                    # serve lower reponses
                    return lowerUserLevels[user_response](user=user, session_id=session_id)
                else:
                    # serve higher responses
                    return respond("END serving higher responses")
            else:
                return default_menu(user, session_id)
        else:
            # add a new session level
            session_level = SessionLevel(phone_number=phone_number, session_id=session_id)
            db.session.add(session_level)
            db.session.commit()
            return home(user=user, session_id=session_id)
    else:
        return respond("END you need to register before accession or services")

def home(user, session_id):
    """
    If user level is zero or zero
    Serves the home menu
    :return: a response object with headers['Content-Type'] = "text/plain" headers
    """

    # upgrade user level and serve home menu
    session_level = SessionLevel.query.filter_by(session_id=session_id).first()
    session_level.promote_level()
    db.session.add(session_level)
    db.session.commit()
    # serve the menu
    menu_text = "CON Welcome to Nerd Microfinance, {} Choose a service.\n".format(user.name)
    menu_text += " 1. Please call me.\n"
    menu_text += " 2. Deposit Money\n"
    menu_text += " 3. Withdraw Money\n"
    menu_text += " 4. Send Money\n"
    menu_text += " 5. Buy Airtime\n"
    menu_text += " 6. Repay Loan\n"

    # print the response on to the page so that our gateway can read it
    return respond(menu_text)

def please_call(user, session_id=None):
    # call the user and bridge to a sales person
    menu_text = "END Please wait while we place your call.\n"

    # make a call
    caller  = "+254703554404"
    recepient = user.phone_number

    # create a new instance of our awesome gateway
    gateway = AfricasTalkingGateway(current_app.config["AT_USERNAME"],current_app.config["AT_APIKEY"])
    try:
        gateway.call(caller, recepient)
    except AfricasTalkingGateway as e:
        menu_text = "Encountered an error when calling: {}".format(str(e))

    # print the response on to the page so that our gateway can read it
    return respond(menu_text)

def deposit(session_id, user=None):
    # as how much and Launch teh Mpesa Checkout to the user
    menu_text = "CON How much are you depositing?\n"
    menu_text += " 1. 1 Shilling.\n"
    menu_text += " 2. 2 Shillings.\n"
    menu_text += " 3. 3 Shillings.\n"

    # Update sessions to level 9
    update_session(session_id, SessionLevel, 9)
    # print the response on to the page so that our gateway can read it
    return respond(menu_text)

def withdraw(session_id, user=None):
    # Ask how much and Launch B2C to the user
    menu_text = "CON How much are you withdrawing?\n"
    menu_text += " 1. 1 Shilling.\n"
    menu_text += " 2. 2 Shillings.\n"
    menu_text += " 3. 3 Shillings.\n"

    # Update sessions to level 10
    update_session(session_id, SessionLevel, 10)

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

def send_money(session_id, user=None):
    # Send Another User Some Money
    menu_text =  "CON You can only send 1 shilling.\n"
    menu_text += " Enter a valid phonenumber (like 0722122122)\n"

    # Update sessions to level 11
    update_session(session_id, SessionLevel, 11)
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

def buy_airtime(user, session_id=None):
    # 9e.Send user airtime
    menu_text = "END Please wait while we load your account.\n"

    # Search DB and the Send Airtime
    recipients = {"phoneNumber": user.phone_number,  "amount": "KES 5"}
    # JSON encode
    recipientStringFormat = json.dumps(recipients)

    # Create an instance of our gateway
    gateway = AfricasTalkingGateway(current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])
    try:
        results = gateway.sendAirtime(recipientStringFormat)
    except AfricasTalkingGatewayException as e:
        menu_text = str(e)

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

def pay_loan(session_id, user=None):
    # Ask how much and Launch the Mpesa Checkout to the user
    menu_text = "CON How much are you depositing?\n"
    menu_text += " 4. 1 Shilling.\n"
    menu_text += " 5. 2 Shillings.\n"
    menu_text += " 6. 3 Shillings.\n"

    # Update sessions to level 9
    session_level = SessionLevel.query.filter_by(session_id=session_id).first()
    session_level.promote_level(9)
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

def default_menu(user, session_id):
    # Return user to Main Menu & Demote user's level
    menu_text = "CON You have to choose a service.\n"
    menu_text += "Press 0 to go back to main menu.\n"
    # demote
    session_level = SessionLevel.query.filter_by(session_id=session_id).first()
    session_level.demote_level()
    db.session.add(session_level)
    db.session.commit()
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

def update_session(session_id, session_level, level):
    session_level = session_level.query.filter_by(session_id=session_id).first()
    session_level.promote_level(level)
    db.session.add(session_level)
    db.session.commit()

def respond(menu_text):
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response

