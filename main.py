import os
import json

from bot import discord_client, commands, bot_utils, events
from database import mongo_client, db_utils

if os.path.isdir(f"{bot_utils.get_current_dir()}/tts") is False:
    os.mkdir(f"{bot_utils.get_current_dir()}/tts")

with open("tts/queue.json", "w") as file:
    pass

client = discord_client.get_client()

global_settings = bot_utils.get_global_settings()

client.run(global_settings["token"])

""" anaconda commands
cd documents\codeprojects\migala-bot-heroku
conda activate migalaenv
python main.py 
"""

""" heroku deply commands
cd documents\codeprojects\migala-bot-heroku
heroku login
git add .
git commit -am "whatever"
git push heroku master
heroku logs -a cb-economy-bot
"""