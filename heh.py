#!/usr/bin/env python

import os,praw, re, wget, shutil
import json, urllib, time
import requests
from urllib.parse import urlparse
import logging
from telegram.ext import Updater, CommandHandler

url = 'https://www.reddit.com/'
with open('credentials.json') as f:
    params = json.load(f)


#mode = "dev" for running locally and prod for hosting on Heroku

mode = "prod"
TOKEN = "TG Token"
HEROKU_APP_NAME = "<HEROKU_APP_NAME>"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()



if mode == "dev":
    def run(updater):
        updater.start_polling()
        updater.idle()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8449"))
        print(HEROKU_APP_NAME)
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)



reddit = praw.Reddit(client_id=params['client_id'], 
                     client_secret=params['api_key'],
                     password=params['password'], 
                     user_agent='Waah Modiji Waah',
                     username=params['username'])



client_id = params['client']
client_secret = params['client_secret']





def get_credentials(client_id, client_secret):
    data = {
            "client_id": client_id, 
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

    print('DATA:', data)

    r = requests.post(url='https://api.gfycat.com/v1/oauth/token', data=str(data))
    d = r.json()
    expires_in = d['expires_in']
    access_token = d['access_token']
    print('\nResponse to credentials:', access_token)
    return access_token

def download_gfy(access_token, gfyid):
    header = {'Authorization': 'Bearer {}'.format(access_token)}
    url = 'https://api.gfycat.com/v1/gfycats/{}'.format(gfyid)

    r = requests.get(url=url, headers=header)
    #print('\n\t\tResponse:')
    #pp.pprint(r)
    return r.json()

def largest_gif_url(response):
    return response['gfyItem']['miniUrl']



def start(update,context):
    print('START')
    access_token = get_credentials(client_id, client_secret)
    subs = ['desinsfw']
    links = list()
    imgs_folder = 'book/'

    if not os.path.exists(imgs_folder):
        os.makedirs(imgs_folder)
    reply_database = []
    with open("database.txt", "r") as _file:
        reply_database = _file.read().splitlines()

    for submission in reddit.multireddit(name = 'myprivatebot', redditor = '1amaditya').stream.submissions():
        i = submission.url
        caption = submission.title + "\n" + submission.shortlink
        header = {'User-Agent': 'Aditya7069 Telegram Bot'}
        data = urlparse(i)
        rec = re.compile(r"https?://(www\.)?")
        if (submission.id not in reply_database):
            try:
                if rec.sub('', data.netloc).strip().strip('/') == 'gfycat.com':
                    gfyid = data.path.strip('/')
                    response = download_gfy(access_token, gfyid)
                    #print(response)
                    url = largest_gif_url(response)
                    print(url)
                    #wget.download(url,imgs_folder)
                    r = requests.get(url = url, headers = header)
                    with open(imgs_folder + data.path.strip('/') + '.mp4', 'wb') as f:
                        f.write(r.content)
                        f.close()
                    context.bot.send_video(chat_id=update.message.chat_id, caption = caption, video=open(imgs_folder + data.path.strip('/') + '.mp4', 'rb'),timeout = 120,   supports_streaming =True)
                    if os.path.exists(imgs_folder + data.path.strip('/') + '.mp4'):
                        os.remove(imgs_folder + data.path.strip('/') + '.mp4')
                
                elif rec.sub('', data.netloc).strip().strip('/') == 'v.redd.it':
                    #wget.download(i+'/DASH_480?source=fallback',imgs_folder+data.path.strip('/')+'.mp4')
                    print(i+'/DASH_480?source=fallback')
                    r = requests.get(url = i+'/DASH_480?source=fallback', headers = header)
                    with open(imgs_folder + data.path.strip('/') + '.mp4', 'wb') as f:
                        f.write(r.content)
                        f.close()
                    context.bot.send_video(chat_id=update.message.chat_id, caption = caption ,video=open(imgs_folder + data.path.strip('/') + '.mp4', 'rb'),timeout = 120,  supports_streaming =True)
                    if os.path.exists(imgs_folder + data.path.strip('/') + '.mp4'):
                        os.remove(imgs_folder + data.path.strip('/') + '.mp4')
                
                elif rec.sub('', data.netloc).strip().strip('/') == 'i.redd.it' or rec.sub('', data.netloc).strip().strip('/') == 'i.imgur.com':            
                    print(i)
                    if data.path.strip('/').endswith('.jpg'):
                        
                        r = requests.get(url = i, headers = header)
                        with open(imgs_folder + data.path.strip('/') + '.jpg', 'wb') as f:
                            f.write(r.content)
                            f.close()
                        context.bot.send_photo(chat_id=update.message.chat_id, caption = caption ,photo=open(imgs_folder + data.path.strip('/') + '.jpg', 'rb'), timeout =120)
                        if os.path.exists(imgs_folder + data.path.strip('/') + '.jpg'):
                            os.remove(imgs_folder + data.path.strip('/') + '.jpg')
                    
                    elif data.path.strip('/').endswith('.gif'):
                        
                        r = requests.get(url = i, headers = header)
                        with open(imgs_folder + data.path.strip('/') + '.gif', 'wb') as f:
                            f.write(r.content)
                            f.close()
                        context.bot.send_animation(chat_id=update.message.chat_id, caption = caption, animation=open(imgs_folder + data.path.strip('/') + '.gif', 'rb'), timeout =120)
                        if os.path.exists(imgs_folder + data.path.strip('/') + '.'):
                            os.remove(imgs_folder + data.path.strip('/') + '.gif')
                with open("database.txt", "a") as _file:
                    _file.write(submission.id + "\n")
                reply_database.append(submission.id)
            except:
                continue    
        

if __name__ == "__main__":

    dispatcher.add_handler(CommandHandler('start', start))
    run(updater)