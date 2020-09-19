from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Location
from explorebot.util import to_reply_keyboard
from explorebot.variants import all_variant_buttons, all_distance_buttons, is_valid_distance, is_valid_variant, variant_to_query

#Maybe add ABC(abstract base class) support
class VariantRequestStage(object):
    def __init__(self):
        self.req = None
        self.error = None

    def start(self, req, bot, chat_id):
        self.req = req
        bot.send_message(chat_id, "What are you up to?", reply_markup=to_reply_keyboard(all_variant_buttons()))

    def handle(self, message):
        if is_valid_variant(message.text):
            self.req.query = variant_to_query(message.text)
        else:
            self.error = "Not able to parse variant reply"


class RadiusRequestStage(object):
    def __init__(self):
        self.req = None
        self.error = None

    def start(self, req, bot, chat_id):
        self.req = req
        bot.send_message(chat_id, "How far are you willing to walk?", reply_markup=to_reply_keyboard(all_distance_buttons()))

    def handle(self, message):
        if is_valid_distance(message.text):
            self.req.radius = int(message.text)
        else:
            self.error = "Not able to parse radius reply"


class LocationRequestStage(object):
    def __init__(self):
        self.req = None
        self.error = None

    def start(self, req, bot, chat_id):
        self.req = req
        bot.send_message(chat_id, "We are all ready but first give me your location!", reply_markup=to_reply_keyboard(['Give location 📍'], request_location=True))

    def handle(self, message):
        if message.location != None:
            self.req.location = message.location
        else:
            self.error = "Was expecting a location"
