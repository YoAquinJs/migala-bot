from bot import discord_client, commands, bot_utils, events
from database import mongo_client, db_utils

global_settings = bot_utils.get_global_settings()

client = discord_client.get_client()
client.run(global_settings["token"])

""" Comandos para Deploy en Heroku
cd .\migala-bot-heroku
heroku login
git add .
git commit -am "cambios"
git push heroku master

    Acceso a logs de la consola

heroku logs -a migala-bot
"""