import logging
import json
import requests
import os
import traceback
from math import floor, ceil, sqrt
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Location

# Unused port(webhooks didn't fly, will try later)
PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', None)
CLIENT_ID = os.environ.get('FS_CLIENT_ID', None)
CLIENT_SECRET = os.environ.get('FS_CLIENT_SECRET', None)

BUTTON_COFFEE_TEXT = "Coffee ☕"
BUTTON_BEER_TEXT = "Beer 🍺"
BUTTON_DINNER_TEXT = "Dinner 🍷"
BUTTON_DRINKS_TEXT = "Drinks 🥃"
BUTTON_PARK_TEXT = "Park 🌳"
BUTTON_SIGHT_TEXT = "Sight 🗽"
BUTTON_MUSEUM_TEXT = "Museum 🏛️"
BUTTON_CINEMA_TEXT = "Cinema 🍿"
BUTTON_ENTERTAINMENT_TEXT = "Entertainment 🕺"
VARIANT_BUTTONS = [BUTTON_COFFEE_TEXT, BUTTON_BEER_TEXT, BUTTON_DINNER_TEXT, BUTTON_DRINKS_TEXT,
                   BUTTON_PARK_TEXT, BUTTON_SIGHT_TEXT, BUTTON_MUSEUM_TEXT, BUTTON_CINEMA_TEXT, BUTTON_ENTERTAINMENT_TEXT]
DISTANCE_BUTTONS = ['250', '500', '1000', '5000']


def to_reply_keyboard(arr, request_location=False):
    grid_side = sqrt(len(arr))
    grid_width = floor(grid_side)
    grid_height = ceil(grid_side)
    keys = []
    for i in range(grid_height):
        row = []
        for j in range(grid_width):
            lin_index = i * grid_width + j
            row.append(KeyboardButton(
                arr[lin_index], request_location=request_location))
        keys.append(row)
    return ReplyKeyboardMarkup(keys, one_time_keyboard=True)


def invert_dict(in_dict):
    result = {}
    for key in in_dict.keys():
        value = in_dict[key]
        if isinstance(value, list):
            for inner_value in value:
                result[inner_value] = key
        else:
            result[value] = key
    return result


QUERIES_TO_VARIATIONS = {'coffee': [BUTTON_COFFEE_TEXT, 'coffee', 'Coffee', '☕'],
                         'beer': [BUTTON_BEER_TEXT, 'beer', 'Beer', '🍺'],
                         'dinner': [BUTTON_DINNER_TEXT, 'dinner', 'Dinner', '🥗', 'food', 'Food'],
                         'bar': [BUTTON_DRINKS_TEXT, 'drinks', 'Drinks', 'bar', 'Bar', 'cocktail', 'Cocktail', 'cocktails', 'Cocktails'],
                         'park': [BUTTON_PARK_TEXT],
                         'sight': [BUTTON_SIGHT_TEXT],
                         'museum': [BUTTON_MUSEUM_TEXT],
                         'cinema': [BUTTON_CINEMA_TEXT],
                         'entertainment': [BUTTON_ENTERTAINMENT_TEXT]}
VARIATIONS_TO_QUERIES = invert_dict(QUERIES_TO_VARIATIONS)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# It's a clusterfuck of a state machine right now. Maybe refactor it using some actual state machines?


class Session(object):
    def __init__(self, query=None, radius=None, location=None):
        self.query = query
        self.radius = radius
        self.location = location

    def is_valid(self):
        return self.query != None and self.radius != None and self.location != None


open_sessions = {}


def fs_request(session):
    url = 'https://api.foursquare.com/v2/venues/explore'
    params = dict(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        v='20180323',
        ll=f'{session.location.latitude},{session.location.longitude}',
        radius=session.radius,
        query=session.query,
        limit=3
    )
    resp = requests.get(url=url, params=params)
    return json.loads(resp.text)


def reply_places(message, session):
    places_response = fs_request(session)
    if(places_response['meta']['code'] != 200):
        message.reply_text("Sorry, something went wrong...")
        print(f"User {message.from_user.first_name} id {message.from_user.id} in chat {message.chat.id} failed fs request with session {session}!")
    else:
        body = places_response['response']
        groups = body['groups']
        try:
            recommended = next(g for g in groups if g['name'] == 'recommended')
            if len(recommended['items']) == 0:
                raise StopIteration
            # A horrible workaround, will deal with it later
            message.reply_text("Here are some places for you:",
                               reply_markup=ReplyKeyboardRemove())
            for item in recommended['items']:
                venue = item['venue']
                loc = venue['location']
                message.reply_text(f"{venue['name']} | {loc['address']}")
                message.bot.send_location(
                    chat_id=message.chat.id, latitude=loc['lat'], longitude=loc['lng'])
        except StopIteration:
            message.reply_text(
                "Sorry but there are no recommended places near you.", reply_markup=ReplyKeyboardRemove())


def end_success(session, message):
    print(f"User {message.from_user.first_name} id {message.from_user.id} in chat {message.chat.id} successfully ended the session!")
    reply_places(message, session)
    open_sessions.pop(message.chat.id)


def end_failure(session, message):
    print(f"User {message.from_user.first_name} id {message.from_user.id} in chat {message.chat.id} failed session {session} with a message {message}!")
    for line in traceback.format_stack():
        print(line.strip())
    message.reply_text("Sorry something went horribly wrong. Try again or tell my creator!",
                       reply_markup=ReplyKeyboardRemove())
    open_sessions.pop(message.chat.id)


def resolve_radius_reply(session, msg):
    if session.location == None:
        msg.reply_text("And one last thing: send me your location!",
                       reply_markup=ReplyKeyboardRemove())
    elif session.is_valid():
        end_success(session, msg)
    else:
        end_failure(session, msg)


def start(update, context):
    open_sessions[update.message.chat.id] = Session()
    update.message.reply_text("Hi! I'm an explorer bot! \nWhat are you up to?",
                              reply_markup=to_reply_keyboard(VARIANT_BUTTONS))


def reset(update, context):
    chat_id = update.message.chat.id
    if chat_id in open_sessions:
        open_sessions.pop(chat_id)
        update.message.reply_text(
            "Successfuly reseted your search!", reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(
            "There is nothing to reset!", reply_markup=ReplyKeyboardRemove())


def help(update, context):
    update.message.reply_text(
        'I will recommend you a place nearby!\nTry /start or send me your location or maybe even just try typing what do you want, like coffee or food.')


def text(update, context):
    msg = update.message
    chat_id = msg.chat.id
    msg_text = msg.text
    session = open_sessions.get(chat_id, None)
    if session != None:
        if session.query == None and msg_text in VARIANT_BUTTONS:
            session.query = VARIATIONS_TO_QUERIES[msg_text]
            msg.reply_text("How far are you willing to walk?",
                           reply_markup=to_reply_keyboard(DISTANCE_BUTTONS))
        elif session.radius == None and msg.text in DISTANCE_BUTTONS:
            session.radius = int(msg_text)
            resolve_radius_reply(session, msg)
        else:
            end_failure(session, msg)
    else:
        possible_variant = VARIATIONS_TO_QUERIES.get(msg_text, None)
        if possible_variant != None:
            open_sessions[chat_id] = Session(
                query=VARIATIONS_TO_QUERIES[msg_text])
            msg.reply_text("How far are you willing to walk?",
                           reply_markup=to_reply_keyboard(DISTANCE_BUTTONS))
        else:
            msg.reply_text("I do not really understand you...")


def location(update, context):
    msg = update.message
    chat_id = msg.chat.id
    session = open_sessions.get(chat_id, None)
    if session == None:
        open_sessions[chat_id] = Session(location=msg.location)
        msg.reply_text("What are you up to?",
                       reply_markup=to_reply_keyboard(VARIANT_BUTTONS))
        print(
            f"User {msg.from_user.first_name} id {msg.from_user.id} in chat {chat_id} starting new session with a location!")
    else:
        session.location = msg.location
        if session.is_valid():
            end_success(session, msg)
        else:
            end_failure(session, msg)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    can_launch = True
    if TOKEN == None:
        print("Couldn't retrieve TELEGRAM_BOT_TOKEN")
        can_launch = False
    if CLIENT_ID == None:
        print("Couldn't retrieve FS_CLIENT_ID envvar")
        can_launch = False
    if CLIENT_SECRET == None:
        print("Couldn't retrieve FS_CLIENT_SECRET envvar")
        can_launch = False
    if not can_launch:
        print("On more errors happened. Can't launch the bot.")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.location, location))
    dp.add_error_handler(error)

    '''
    doesn't work for some reason, will use polling for now
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://140.82.38.106/' + TOKEN)
    '''
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
