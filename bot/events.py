"""El módulo events maneja eventos de discord, mensaje de inicio en consola, mensajes de bienvenida y reacciones a selectores de roles"""

import discord
from discord.ext import commands

from bot.bot_utils import *
from bot.discord_client import get_client
from database.db_utils import insert, modify, query, delete, Collection

client = get_client()
global_settings = get_global_settings()


@client.event
async def on_ready():
    """(Evento de discord, se llama cuando el bot esta listo para inicializarse) imprime el nombre e id del bot
    """

    print("logged as")
    print(client.user.name)
    print(client.user.id)
    print('-----------')


#@client.event
#async def on_slash_command_error(ctx, error):
#   if isinstance(error, commands.CommandNotFound):
#       return
#
#   msg = "ha ocurrido un error"
#   if isinstance(error, commands.MissingRequiredArgument):
#       msg = f"{msg}, faltan argumentos"
#   elif isinstance(error, commands.BadArgument):
#       msg = f"{msg}, un argumento no es valido"
#   elif isinstance(error, commands.TooManyArguments):
#       msg = f"{msg}, demasiados argumentos"
#   elif isinstance(error, commands.MissingPermissions):
#       msg = f"{msg}, no tienes permisos para realizar esta accion"
#   elif isinstance(error, commands.BotMissingPermissions):
#       msg = f"{msg}, de bot no tiene permisos para realizar esta accion"
#   else:
#       error = f"exception in {ctx.command}: {error}"
#       print(error)
#       for dev_id in global_settings["dev_ids"]:
#           dev = await client.fetch_user(dev_id)
#           await dev.send(f"BUG REPORT: {error}")
#       msg = f"{msg}, ah sido reportado a los desarrolladores"
#
#   await send_message(ctx, msg)


@client.event
async def on_member_join(member):
    """(Evento de discord, se llama cuandoun nuevo miembro se une a un servidor) envia un mensaje de bienvenida
        personalizado al nuevo usuario

        Args:
                member (discord.Member): Nuevo miembro en el servidor
    """

    welcome = query("name", "welcome_stt", member.guild, Collection.general.value)
    if welcome is None:
        return
    embed = discord.Embed(title=f"Bienvenido {member.display_name}, estamos gustosos de tu ingreso al proyecto", 
                          description=welcome["welcome_msg"], color=discord.colour.Color.gold())
    embed.set_image(url=member.avatar_url)

    for channel in member.guild.channels:
        if channel.id == welcome["welcome_channel"]:
            await channel.send(embed=embed)


@client.event
async def on_raw_reaction_add(payload):
    """(Evento de discord, se llama cuando un usuario reacciona a un mensaje del bot) si se esta reaccionando a un
        selector de roles se le asigna el rol correspondiente al emoji al usuario

        Args:
                payload (discord.On_Raw_Reaction_Add): Contiene la informacion de la reaccion
    """

    if payload.member.bot:
        return

    guild = client.get_guild(payload.guild_id)
    channel = discord.utils.get(client.get_guild(payload.guild_id).channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    selector = query("msg_id", payload.message_id, guild, Collection.selectors.value)
    if selector is not None:

        await msg.remove_reaction(payload.emoji, payload.member)
    
        if str(payload.emoji) == "❌":
            if payload.member.permissions_in(channel).administrator is True:
                await msg.delete()
                delete("msg_id", payload.message_id, guild, Collection.selectors.value)
                payload.member.send("selector eliminado")
                return
        
        role = discord.utils.get(guild.roles, id=selector['emoji_role'][str(payload.emoji)])
        if not(role in payload.member.roles):
            await payload.member.add_roles(role)
        else:
            await payload.member.remove_roles(role)

    poll = query("msg_id", payload.message_id, guild, Collection.polls.value)
    if poll is not None:
        if str(payload.emoji) == "❌" and poll["user_id"] == payload.member.id:
            await msg.delete()
            delete("msg_id", payload.message_id, guild, Collection.polls.value)

        if str(payload.emoji) in poll["options"].keys():
            poll["options"][str(payload.emoji)]["votes"].append(payload.member.id)

        if poll["unique_vote"] is True:
            for emoji in poll["options"].keys():
                if str(payload.emoji) == emoji:
                    continue

                if payload.member.id in poll["options"][emoji]["votes"]:
                    await msg.remove_reaction(emoji, payload.member)

        modify("msg_id", payload.message_id, "options", poll["options"], guild, Collection.polls.value)


@client.event
async def on_raw_reaction_remove(payload):
    """(Evento de discord, se llama cuando un usuario remueve una reaccion a un mensaje del bot) si se remueve la
        reaccion en un mensaje del bot se le remueve el rol correspondiente al emoji al usuario

        Args:
                payload (discord.On_Raw_Reaction_Add): Contiene la informacion de la reaccion
    """

    guild = client.get_guild(payload.guild_id)
    poll = query("msg_id", payload.message_id, guild, Collection.polls.value)

    if poll is not None:
        user = await client.fetch_user(payload.user_id)
        user_id = user.id

        if str(payload.emoji) in poll["options"].keys():
            poll["options"][str(payload.emoji)]["votes"].remove(user_id)

        modify("msg_id", payload.message_id, "options", poll["options"], guild, Collection.polls.value)
