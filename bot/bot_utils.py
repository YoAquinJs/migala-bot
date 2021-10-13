"""El módulo bot_utils contiene metodos a los que acceden multiples modulos del bot, tiempo, mensajes y configuracion global"""

import os
import pytz
import json
import asyncio
import discord
import datetime

current_dir = None
global_settings = None


def get_time():
    """Retorna el tiempo y hora actual en UTC

    Returns:
            srt: Tiempo actual
    """

    return str(datetime.datetime.now(pytz.utc))


async def send_message(ctx, text, title="", time=0, auto_time=False):
    """Envía un mensaje en discord en formato embed de discord

    Args:
            ctx (discord.ext.commands.Context): Context de discord
            text (str): Contenido del mensaje
            title (str, optional): titulo del mensaje
            time (int, optional): Especifica el tiempo a esperar para eliminar el mensaje, si es 0 es permanente,
            por defecto es 0
            auto_time (bool, optional): Especifica si despues de el tiempo de lectura promedio el mensaje sera eliminado,
            por defecto falso.

    Returns:
            discord.Message: Mensaje enviado
    """

    embed = discord.Embed(title=title, description=text, colour=discord.colour.Color.gold())
    msg = await ctx.channel.send(embed=embed)

    if auto_time is True:
        wpm = 180  # velocidad de lectura persona promedio (palabras por minuto)
        time = len(text.split())/wpm * 60 + 1
        await asyncio.sleep(time)
        await msg.delete()

    if time != 0:
        await asyncio.sleep(time)
        await msg.delete()

    return msg


def get_global_settings():
    """Retorna la configuracion del bot para todos los servidores de discord

        Returns:
                dict: Configuracion global del bot
    """

    global global_settings
    
    if global_settings is None:
        with open("settings.json", "r") as tmp:
            global_settings = json.load(tmp)

    return global_settings
