import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardRemove
from explorebot.explorerequestpipeline import ExploreRequestPipeline
from explorebot.variants import is_valid_variant
import explorebot.foursquare as fs

def start(update, context):
    ExploreRequestPipeline.start_empty(update.message)

def reset(update, context):
    chat_id = update.message.chat.id
    if ExploreRequestPipeline.is_started(update.message):
        ExploreRequestPipeline.stop(update.message)
        update.message.reply_text("Successfuly reseted your search!", reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text("There is nothing to reset!", reply_markup=ReplyKeyboardRemove())

def help(update, context):
    update.message.reply_text(
        'I will recommend you a place nearby!\nTry /start or send me your location or maybe even just try typing what do you want, like coffee or food.')

def text(update, context):
    if ExploreRequestPipeline.is_started(update.message):
        ExploreRequestPipeline.handle_msg(update.message)
    else:
        if is_valid_variant(update.message.text):
            ExploreRequestPipeline.start_from_variant(update.message)
        else:
            update.message.reply_text("I do not really undestand you...", reply_markup=ReplyKeyboardRemove())

def location(update, context):
    if ExploreRequestPipeline.is_started(update.message):
        ExploreRequestPipeline.handle_msg(update.message)
    else:
        ExploreRequestPipeline.start_from_location(update.message)

def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    can_launch = True
    BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', None)
    if BOT_TOKEN == None:
        print("Couldn't retrieve TELEGRAM_BOT_TOKEN")
        can_launch = False
    if fs.CLIENT_ID == None:
        print("Couldn't retrieve FS_CLIENT_ID envvar")
        can_launch = False
    if fs.CLIENT_SECRET == None:
        print("Couldn't retrieve FS_CLIENT_SECRET envvar")
        can_launch = False
    if not can_launch:
        print("One more errors happened. Can't launch the bot.")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.location, location))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()