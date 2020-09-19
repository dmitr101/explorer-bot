from telegram import Message, ReplyKeyboardRemove

from explorebot.explorerequest import ExploreRequest
from explorebot.explorerequeststage import VariantRequestStage, LocationRequestStage, RadiusRequestStage
from explorebot.variants import variant_to_query, is_valid_variant

import explorebot.foursquare as fs

_open_erps = {}

class ExploreRequestPipeline(object):
    def __init__(self, erp_dict, request, bot, chat_id, stages):
        self._erp_dict = erp_dict
        self._request = request
        self._bot = bot
        self._chat_id = chat_id
        self._stages = stages
        self._current_stage_index = 0
        self._error = None
        self._start_current_stage()

    def _next_stage(self):
        self._current_stage_index += 1

    def _current_stage(self):
        return self._stages[self._current_stage_index]

    def _is_last_stage(self):
        return self._current_stage_index == (len(self._stages) - 1)

    def _start_current_stage(self):
        self._current_stage().start(self._request, self._bot, self._chat_id)

    def _pop_self_from_dict(self):
        self._erp_dict.pop(self._chat_id)

    def _finish_success(self):
        self._pop_self_from_dict()
        response = fs.make_request(self._request)
        if(response.error != None):
            self._bot.send_message(self._chat_id,
                                   f"Sorry but I couldn't finish your request! Reason: {response.error}",
                                   reply_markup=ReplyKeyboardRemove())
            return
        self._bot.send_message(
            self._chat_id, "Here are some places for you: ", reply_markup=ReplyKeyboardRemove())
        for place in response.places:
            self._bot.send_message(
                self._chat_id, f"{place.name} | {place.address}")
            self._bot.send_location(
                self._chat_id, latitude=place.latitude, longitude=place.longitude)

    def _finish_failure(self):
        self._pop_self_from_dict()
        self._bot.send_message(self._chat_id,
                               f"Sorry something went horribly wrong. Try again or tell my creator! Error: {self._error}",
                               reply_markup=ReplyKeyboardRemove())

    def handle(self, msg):
        self._current_stage().handle(msg)
        self._error = self._current_stage().error
        if self._error != None:
            self._finish_failure()
            return
        if self._is_last_stage():
            self._finish_success()
            return
        self._next_stage()
        self._start_current_stage()

    @staticmethod
    def start_empty(bot, chat_id, erp_dict = _open_erps):
        erp_dict[chat_id] = ExploreRequestPipeline(
            erp_dict=erp_dict,
            request=ExploreRequest(),
            bot=bot,
            chat_id=chat_id,
            stages=[VariantRequestStage(), RadiusRequestStage(), LocationRequestStage()])

    @staticmethod
    def start_from_location(msg, erp_dict = _open_erps):
        erp_dict[msg.chat.id] = ExploreRequestPipeline(
            erp_dict=erp_dict,
            request=ExploreRequest(location=msg.location),
            bot=msg.bot,
            chat_id=msg.chat.id,
            stages=[VariantRequestStage(), RadiusRequestStage()])

    @staticmethod
    def start_from_variant(msg, erp_dict = _open_erps):
        erp_dict[msg.chat.id] = ExploreRequestPipeline(
            erp_dict=erp_dict,
            request=ExploreRequest(query=variant_to_query(msg.text)),
            bot=msg.bot,
            chat_id=msg.chat.id,
            stages=[RadiusRequestStage(), LocationRequestStage()])

    @staticmethod
    def start_from_message(msg, erp_dict = _open_erps):
        if msg.location != None:
            ExploreRequestPipeline.start_from_location(msg, erp_dict)
        elif is_valid_variant(msg.text):
            ExploreRequestPipeline.start_from_variant(msg, erp_dict)
        else:
            msg.reply_text("I do not really understand you...", reply_markup=ReplyKeyboardRemove())

    @staticmethod
    def is_started(chat_id, erp_dict = _open_erps):
        return chat_id in erp_dict

    @staticmethod
    def stop(chat_id, erp_dict = _open_erps):
        erp_dict.pop(chat_id)

    @staticmethod
    def handle_message(msg, erp_dict = _open_erps):
        if ExploreRequestPipeline.is_started(msg.chat.id):
            erp_dict.get(msg.chat.id, None).handle(msg)
        else:
            ExploreRequestPipeline.start_from_message(msg, erp_dict)