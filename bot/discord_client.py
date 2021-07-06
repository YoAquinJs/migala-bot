import discord
from discord.ext import commands
from bot.bot_utils import get_global_settings

client = None


def init_client():
    global client
    global_settings = get_global_settings()
    
    intents = discord.Intents.all()
    intents.members = True

    client = commands.Bot(command_prefix=global_settings["prefix"], help_command=None,
                        activity=discord.Game(f"Migala Bot | {global_settings['prefix']}help"),
                        status=discord.Status.online, intents=intents)


def get_client():
    if client is None:
        init_client()

    return client
