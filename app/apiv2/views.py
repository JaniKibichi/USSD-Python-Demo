from flask import request
from ..models import User, SessionLevel
from utils import respond, add_session
from . import api_v11
from menu import LowerLevelMenu, HighLevelMenu, RegistrationMenu


@api_v11.route('/', methods=['POST', 'GET'])
def index():
    return respond("END connection ok")


@api_v11.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    """
    Handles post call back from AT

    :return:
    """

    # GET values from the AT's POST request
    session_id = request.values.get("sessionId", None)
    serviceCode = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    text_array = text.split("*")
    user_response = text_array[len(text_array) - 1]

    # get user
    user = User.query.filter_by(phone_number=phone_number).first()
    # get user USSD journey level
    session = SessionLevel.query.filter_by(session_id=session_id).first()
    # if user is registered serve appropriate user menu
    # else register user
    if user:
        # if session is registered serve approriate menu
        # else register session
        if session:
            level = session.level
            # if level is less than 2 serve lower level menus
            if level < 2:
                menu = LowerLevelMenu(session_id=session_id, phone_number=phone_number)
                # initialise menu dict
                menus = {
                    "0": menu.home,
                    "1": menu.please_call,
                    "2": menu.deposit,
                    "3": menu.withdraw,
                    "4": menu.send_money,
                    "5": menu.buy_airtime,
                    "6": menu.pay_loan_menu,
                    "default": menu.default_menu
                }
                # serve menu
                return menus.get(user_response or "default")()

            # if level is between 9 and 12 serve high level response
            elif level <= 12:
                menu = HighLevelMenu(user_response, phone_number, session_id)
                # initialise menu dict
                menus = {
                    9: {
                        # user_response : c2b_checkout(phone_number= phone_number, amount = int(user_response))
                        "1": menu.c2b_checkout,
                        "2": menu.c2b_checkout,
                        "3": menu.c2b_checkout,
                        "default": menu.default_mpesa_checkout
                    },
                    10: {
                        # user_response : b2c_checkout(phone_number=phone_number, amount=int(user_response))
                        "1": menu.b2c_checkout,
                        "2": menu.b2c_checkout,
                        "3": menu.b2c_checkout,
                        "default": menu.b2c_default
                    },
                    11: {
                        # "default": send_loan(session_id=session_id,
                        #                      creditor_phone_number=phone_number,
                        #                      debptor_phone_number=user_response)
                        "default": menu.send_loan
                    },
                    12: {
                        # "4": re_pay_loan(session_id, phone_number, amount)
                        "4": menu.repay_loan,  # 1
                        "5": menu.repay_loan,  # 2
                        "6": menu.repay_loan,  # 3
                        "default": menu.default_loan_checkout
                    },
                    "default": {
                        "default": menu.default_loan_checkout
                    }
                }
                try:
                    return menus[level].get(user_response)()
                except TypeError:
                    return menus[level]["default"]()
            elif level <= 22:
                menu = RegistrationMenu(session_id=session_id, phone_number=phone_number, user_response=user_response)
                # handle higher level user registration
                menus = {
                0: menu.get_number,  # params = (session_id, phone_number=phone_number)
                21: menu.get_name,
                # params = (session_id, phone_number=phone_number, user_response=user_response)
                22: menu.get_city,
                # params = (session_id, phone_number=phone_number, user_response=user_response)
                "default": menu.register_default,  # params = (session_id)
                }

                return menus.get(level or "default")()
            else:
                return LowerLevelMenu.class_menu(session)
        else:
            # add a new session level
            add_session(session_id=session_id, phone_number=phone_number)
            # create a menu instance
            menu = LowerLevelMenu(session_id=session_id, phone_number=phone_number)
            # serve home menu
            return menu.home()

    else:
        # create a menu instance
        menu = RegistrationMenu(session_id=session_id, phone_number=phone_number, user_response=user_response)
        # register user
        return menu.get_number()


