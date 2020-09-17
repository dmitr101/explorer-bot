import logging
import json
import requests
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000)) #Unused port(webhooks didn't fly, will try later)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', None)
CLIENT_ID = os.environ.get('FS_CLIENT_ID', None)
CLIENT_SECRET = os.environ.get('FS_CLIENT_SECRET', None)

def explore_request(loc):
    url = 'https://api.foursquare.com/v2/venues/explore'
    params = dict(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        v='20180323',
        ll=f'{loc.latitude},{loc.longitude}',
        query='coffee',
        limit=5
    )
    resp = requests.get(url=url, params=params)
    return json.loads(resp.text)

def start(update, context):
    update.message.reply_text('Hi! I am an explorer bot! \nI may not be finished but let us try!\nSend me your location!')

def help(update, context):
    update.message.reply_text('Right now I only reply with 5 nearby coffee shops to a sent location but my strength will grow!')

def text(update, context):
    update.message.reply_text("I'm not really interested in text messages. Locations on the other hand...")

def location(update, context):
    resp = explore_request(update.message.location)
    if(resp['meta']['code'] != 200):
        update.message.reply_text("Sorry, something went wrong...")
    else:
        body = resp['response']
        # not sure if it's useful
        # if 'warning' in body:
        #     update.message.reply_text(f"Warning: {body['warning']['text']}")
        groups = body['groups']
        try:
            recommended = next(g for g in groups if g['name'] == 'recommended')
            update.message.reply_text("Here are some places for you:")
            i = 1
            for item in recommended['items']:
                update.message.reply_text(f"{i}){item['venue']['name']} \n{item['venue']['location']['address']}")
                i = i + 1
        except StopIteration:
            update.message.reply_text("Sorry but there are no recommended places near you.")

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
