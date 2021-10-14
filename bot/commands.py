"""El módulo commands contiene los metodos de los comandos del bot (incluyendo los SlashCommands), comandos normales y admin"""

import json
import math
import asyncio
import requests
#from gtts import gTTS
from random import randint
#from tube_dl import Youtube
#from moviepy.editor import *
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext import commands
from discord.ext.commands import Context, BadArgument

from bot.bot_utils import *
from bot.discord_client import get_client
from database.db_utils import *
from database.mongo_client import close_client

client = get_client()
global_settings = get_global_settings()

slash = SlashCommand(client, sync_commands=True)
guild_ids = global_settings["guild_ids"]


@client.command(name="stop")
async def stop_bot(ctx: Context):
    """Detiene el bot y termina el proceso en terminal (Command, Dev)

    Args:
        ctx (Context): Context de discord
    """

    for dev_id in global_settings["dev_ids"]:
        if dev_id == ctx.author.id:
            close_client()
            await client.logout()
            await client.close()

            break


@slash.slash(name="ping", description="latencia del bot")
async def ping_chek(ctx: SlashContext):
    """Retorna la latencia del bot, sirve para verificar el estado de activacion del bot (Command)

        Args:
                ctx (SlashContext): Context de discord
    """

    await ctx.send(f"latencia: {round(client.latency * 1000)}ms")


@slash.slash(name="borrar", description="borra la cantidad de mensajes especificada",
             options=[create_option(name="cantidad", description="mensajes a borrar", option_type=4, required=True)],
             connector={"cantidad": "del_msg"})
@commands.has_permissions(manage_messages=True)
async def delete_line(ctx: SlashContext, del_msg: int):
    """Elimina la cantidad especificada de mensajes menor a 100 (SlashComand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    del_msg (int): Numero de mensajes a eliminar
    """

    if del_msg > 100:
        del_msg = 100

    messages = await ctx.channel.history(limit=del_msg).flatten()
    if del_msg > len(messages):
        del_msg = len(messages)

    await ctx.channel.purge(limit=del_msg)

    if del_msg > 1:
        await ctx.send(f"{del_msg} mensajes eliminados")
    else:
        await ctx.send( "1 mensaje eliminado")


@slash.slash(name="canalbienvenida", description="guarda el canal donde se mandaran los mensajes de bienvenida",
             options=[create_option(name="canal", description="canal a guardar", option_type=7, required=True)],
             connector={"canal": "channel"})
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx: SlashContext, channel: discord.TextChannel):
    """Guarda el canal de bienvenida (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    channel (discord.TextChannel): Canal de discord a guardar
    """

    if exists("name", "welcome_stt", ctx.guild, Collection.general.value) is False:
        insert({"name": "welcome_stt", "welcome_channel":0, "welcome_msg":""}, ctx.guild, Collection.general.value)

    modify("name", "welcome_stt", "welcome_channel", channel.id, ctx.guild, Collection.general.value)
    await ctx.send(f"canal de bienvenida {channel}, guardado")


@slash.slash(name="msgbienvenida", description="guarda un mensaje de bienvenida",
             options=[create_option(name="mensaje", description="mensaje a guardar", option_type=3, required=True)],
             connector={"mensaje": "msg"})
@commands.has_permissions(administrator=True)
async def set_welcome_msg(ctx: SlashContext, msg: str):
    """Guarda el mensaje de bienvenida (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    msg (str): Mensaje a guardar
    """

    if exists("name", "welcome_stt", ctx.guild, Collection.general.value) is False:
        insert({"name": "welcome_stt", "welcome_channel":0, "welcome_msg":""}, ctx.guild, Collection.general.value)

    modify("name", "welcome_stt", "welcome_msg", msg, ctx.guild, Collection.general.value)
    await ctx.send(f"""mensaje de bienvenida "{msg}", guardado""")


@slash.slash(name="operacion", description="realiza una operacion matematica",
             options=[create_option(name="num1", description="numero flotante", option_type=3, required=True),
                      create_option(name="operador", description="operador matematico", option_type=3, required=True),
                      create_option(name="num2", description="numero flotante", option_type=3, required=False)],
             connector={"num1": "num1", "operador": "operator", "num2": "num2"})
async def math_operation(ctx: SlashContext, num1: float, operator: str, num2=0.0):
    """Realiza una operacion matematica y devuelve el resultado (SlashCommand)

            Args:
                    ctx (SlashContext): Context de discord
                    num1 (float): Primer numero
                    operator (str): Operador a ejecutar
                    num2 (float): Segundo numero
    """

    num1 = float(num1)
    if num2 is not None:
        num2 = float(num2)

    if operator == "+":
        await ctx.send(str(num1 + num2))
    elif operator == "-":
        await ctx.send(str(num1 - num2))
    elif operator == "*":
        await ctx.send(str(num1 * num2))
    elif operator == "/":
        if num2 == 0:
            await ctx.send("no puedes dividir entre 0")
            return
        await ctx.send(str(num1 / num2))
    elif operator == "^":
        await ctx.send(str(pow(num1, num2)))
    elif operator == "|":
        await ctx.send(str(math.sqrt(num1)))
    elif operator == "!":
        result = int(1)
        for i in range(1, int(num1)+1):
            result = result * i

        await ctx.send(f"{result}")
    elif operator == "%":
        await ctx.send(f"{num1 % num2}")
    else:
        await ctx.send("operador invalido\noperadores validos: +, *, /, ^, |sqrt, !factorial, %modulo")


@slash.slash(name="votacion", description="crea una votacion",
             options=[create_option(name="titulo", description="titulo de la votacion", option_type=3, required=True),
                      create_option(name="tiempo", description="tiempo de la votacion (formato seg':'min':'hora)",
                                    option_type=3, required=True),
                      create_option(name="tipo_de_voto",
                                    description="multiple (votar por varias opciones) unico (votar solo por una "
                                                "opcion)", option_type=3, required=True,
                                    choices=[create_choice(name="multiple", value="f"),
                                             create_choice(name="unico", value="t")]),
                      create_option(name="voto_anonimo",
                                    description="public se mostraran los nombre de los votantes en cada opcion",
                                    option_type=3, required=True,
                                    choices=[create_choice(name="anonimo", value="f"),
                                             create_choice(name="publico", value="t")]),
                      create_option(name="opciona", description="opcion de la votacion", option_type=3, required=True),
                      create_option(name="opcionb", description="opcion de la votacion", option_type=3, required=True),
                      create_option(name="opcionc", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opciond", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opcione", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opcionf", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opciong", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opcionh", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opcioni", description="opcion de la votacion", option_type=3, required=False),
                      create_option(name="opcionj", description="opcion de la votacion", option_type=3,
                                    required=False)],
             connector={"titulo": "tittle", "tiempo": "time", "tipo_de_voto": "vote_type", "voto_anonimo": "anonimous",
                        "opciona": "option1", "opcionb": "option2", "opcionc": "option3", "opciond": "option4",
                        "opcione": "option5", "opcionf": "option6", "opciong": "option7", "opcionh": "option8",
                        "opcioni": "option9", "opcionj": "option10"}, guild_ids=guild_ids)
async def poll(ctx: SlashContext, tittle: str, time: str, vote_type: str, anonimous: str, option1: str, option2: str,
               option3=None, option4=None, option5=None, option6=None, option7=None, option8=None, option9=None,
               option10=None):
    """Genera una votacion con los parametros seleccionados (slashCommand)

            Args:
                    ctx (SlashContext): Context de discord
                    tittle (str): Titulo de la votacion
                    time (str): Duracion de la votacion
                    vote_type (str): 'f' varias opciones, 't' opcion unica
                    anonimous (str): 'f' voto anonimo, 't' voto publico
                    option1 (str): Descripcion de la opcion 1
                    option2 (str): Descripcion de la opcion 2
                    option3 (str): Descripcion de la opcion 3
                    option4 (str): Descripcion de la opcion 4
                    option5 (str): Descripcion de la opcion 5
                    option6 (str): Descripcion de la opcion 6
                    option7 (str): Descripcion de la opcion 7
                    option8 (str): Descripcion de la opcion 8
                    option9 (str): Descripcion de la opcion 9
                    option10 (str): Descripcion de la opcion 10
    """

    if vote_type == "t":
        unique_vote = True
        vote_type = "por una sola opcion"
    else:
        unique_vote = False
        vote_type = "por varias opciones"

    if anonimous == "f":
        anonimous = True
        vote_type += ", voto anonimo"
    else:
        anonimous = False
        vote_type += ", voto publico"

    secs = 0
    i = 0
    y = 0
    j = 0

    for char in time:
        if char == ":" or i + 1 == len(time):
            num = int(time[y:i])
            if i + 1 == len(time):
                try:
                    num = int(time[y:len(time)])
                except:
                    raise BadArgument

            for x in range(j):
                num *= 60

            secs += num
            j += 1
            y = i + 1
        i += 1

    embed = discord.Embed(title=tittle, description=f"La votacion durara {time}, puedes votar {vote_type}")
    embed.set_footer(text="Votacion, reacciona a una letra para votar")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("❌")

    poll = {
        "msg_id": msg.id,
        "user_id": ctx.author.id,
        "unique_vote": unique_vote,
        "anonimous_vote": anonimous,
        "options": {}
    }

    poll["options"]["🇦"] = {"votes": [], "description": option1}
    if anonimous is False:
        poll["options"]["🇦"] = {"votes": [], "description": option1, "voters": []}

    await msg.add_reaction("🇦")
    embed.add_field(
        name=str(option1),
        value="🇦")

    poll["options"]["🇧"] = {"votes": [], "description": option2}
    if anonimous is False:
        poll["options"]["🇧"] = {"votes": [], "description": option1, "voters": []}

    await msg.add_reaction("🇧")
    embed.add_field(
        name=str(option2),
        value="🇧")

    if option3 is not None:
        poll["options"]["🇨"] = {"votes": [], "description": option3}
        if anonimous is False:
            poll["options"]["🇨"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇨")
        embed.add_field(
            name=str(option3),
            value="🇨")
    if option4 is not None:
        poll["options"]["🇩"] = {"votes": [], "description": option4}
        if anonimous is False:
            poll["options"]["🇩"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇩")
        embed.add_field(
            name=str(option4),
            value="🇩")
    if option5 is not None:
        poll["options"]["🇪"] = {"votes": [], "description": option5}
        if anonimous is False:
            poll["options"]["🇪"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇪")
        embed.add_field(
            name=str(option5),
            value="🇪")
    if option6 is not None:
        poll["options"]["🇫"] = {"votes": [], "description": option6}
        if anonimous is False:
            poll["options"]["🇫"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇫")
        embed.add_field(
            name=str(option6),
            value="🇫")
    if option7 is not None:
        poll["options"]["🇬"] = {"votes": [], "description": option7}
        if anonimous is False:
            poll["options"]["🇬"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇬")
        embed.add_field(
            name=str(option7),
            value="🇬")
    if option8 is not None:
        poll["options"]["🇭"] = {"votes": [], "description": option8}
        if anonimous is False:
            poll["options"]["🇭"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇭")
        embed.add_field(
            name=str(option8),
            value="🇭")
    if option9 is not None:
        poll["options"]["🇮"] = {"votes": [], "description": option9}
        if anonimous is False:
            poll["options"]["🇮"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇮")
        embed.add_field(
            name=str(option9),
            value="🇮")
    if option10 is not None:
        poll["options"]["🇯"] = {"votes": [], "description": option10}
        if anonimous is False:
            poll["options"]["🇯"] = {"votes": [], "description": option1, "voters": []}

        await msg.add_reaction("🇯")
        embed.add_field(
            name=str(option10),
            value="🇯")
    
    insert(poll, ctx.guild, Collection.polls.value)
    await msg.edit(embed=embed)

    await asyncio.sleep(secs)

    poll = query("msg_id", msg.id, ctx.guild, Collection.polls.value)
    if poll is None:
        return

    options = ""
    for key in poll["options"].keys():
        options = f"{options}{key}, {poll['options'][key]['description']}, {len(poll['options'][key]['votes'])} " \
                  f"votos, {'voto anonimo' if anonimous is True else str(poll['options'][key]['voters'])[1:-1]}\n"

    await msg.delete()
    delete("msg_id", msg.id, ctx.guild, Collection.polls.value)

    await ctx.channel.send(f"Votacion: {tittle}\n**Resultados:**\n{options}")


@slash.slash(name="rol", description="asigna o remueve el rol especificado (si no esta en la lista negra)",
             options=[create_option(name="rol", description="mencion del rol", option_type=8, required=True)],
             connector={"rol": "role"})
async def toggle_role(ctx: SlashContext, role: discord.Role):
    """Asigna o remueve el rol especificado (SlashCommand)

            Args:
                    ctx (SlashContext): Context de discord
                    role (discord.Role): Rol a asignar o remover
    """

    for _role in query_all(ctx.guild, Collection.role_black_list.value):
        if _role["id"] == role.id:
            await ctx.send(f"el rol {role.mention} se encuentra en la lista negra")
            return

    if not(role in ctx.author.roles):
        await ctx.author.add_roles(role)
        await ctx.send(f"se te ha asignado el rol {role.mention}")
    else:
        await ctx.author.remove_roles(role)
        await ctx.send(f"se te ha removido el rol {role.mention}")


@slash.slash(name="rolpara", description="asigna o remueve el rol especificado en el usuario especificado",
             options=[create_option(name="rol", description="mencion del rol", option_type=8, required=True),
                      create_option(name="usuario", description="mencion del usuario", option_type=6, required=True)],
             connector={"rol": "role", "usuario": "user"})
@commands.has_permissions(administrator=True)
async def toggle_role_to(ctx: SlashContext, role: discord.Role, user: discord.Member):
    """Asigna o remueve el rol especificado al usuario especificado (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    role (discord.Role): Rol a asignar o remover
                    user (discord.Member): Usuario a asignar o remover rol
    """

    if not role in user.roles:
        await user.add_roles(role)
        await ctx.send(f"se le ha asignado el rol {role.mention} a {user.mention}")
    else:
        await user.remove_roles(role)
        await ctx.send(f"se le ha removido el rol {role.mention} a {user.mention}")


@slash.slash(name="arolesnegros", description="asigna o remueve un rol de la lista negra",
             options=[create_option(name="rol", description="mencion del rol", option_type=8, required=True)],
             connector={"rol": "role"})
@commands.has_permissions(administrator=True)
async def toggle_role_black_list(ctx: SlashContext, role: discord.Role):
    """Ingresa o elimina un rol de la lista negra (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    role (discord.Role): Rol a ingresar o remover
    """

    if exists("id", role.id, ctx.guild, Collection.role_black_list.value) is False:
        insert({"name": role.name, "id": role.id}, ctx.guild, Collection.role_black_list.value)
        await ctx.send(f"rol {role.mention} ha sido añadido a la lista negra de los roles")
    else:
        delete("id", role.id, ctx.guild, Collection.role_black_list.value)
        await ctx.send(f"rol {role.mention} ha sido removido a la lista negra de los roles")


@slash.slash(name="rolesnegros", description="lista de roles en la lista negra")
async def get_roles_black_list(ctx: SlashContext):
    """Devuelve la lista de roles en la lista negra (SlashCommand)

            Args:
                    ctx (SlashContext): Context de discord
    """

    role_black_list = query_all(ctx.guild, Collection.role_black_list.value)

    if role_black_list.count() == 0:
        await send_message(ctx, "no hay ningun rol en la lista negra")
    else:
        embed = discord.Embed(title=f"lista Nera de Roles", colour=discord.colour.Color.gold())

        for role in role_black_list:
            embed.add_field(
                name=role["name"],
                value=f"id: {role['id']}",
            )

        await ctx.send(embed=embed)


@slash.slash(name="rolselec", description="crea un selector de roles",
             options=[create_option(name="titulo", description="titulo unico del selector", option_type=3, required=True),
                      create_option(name="descripcion", description="descripcion del selector", option_type=3,
                                    required=True)],
             connector={"titulo": "tittle", "descripcion": "description"})
@commands.has_permissions(administrator=True)
async def role_selector(ctx: SlashContext, tittle: str, description: str):
    """Genera un selector de roles (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    tittle (str): Titulo del selector
                    description (str): Descripcion del selector
    """

    await ctx.defer()

    if exists("name", tittle, ctx.guild, Collection.selectors.value) is True:
        await ctx.author.send(f"el titulo {tittle} ya existe")
        return

    msg = await ctx.send(embed=discord.Embed(title=tittle, description=description))
    await msg.add_reaction("❌")

    selector = {
        "msg_id": msg.id,
        "name": tittle,
        "description": description,
        "emoji_role": {}
    }
    _insert = insert(selector, ctx.guild, Collection.selectors.value)
    await ctx.author.send(f"id del selector: {_insert.inserted_id}")
    await ctx.send("selector creado", delete_after=2)


@slash.slash(name="editrolselec", description="edita un selector de roles",
             options=[create_option(name="id", description="id del selector", option_type=3, required=True),
                      create_option(name="titulo", description="nuevo titulo ('_' para dejar el que ya esta)",
                                    option_type=3, required=False),
                      create_option(name="descripcion", description="nueva descripcion ('_' para dejar el que ya esta)",
                                    option_type=3, required=False)],
             connector={"id": "_id", "titulo": "tittle", "descripcion": "description"})
@commands.has_permissions(administrator=True)
async def edit_role_selector(ctx: SlashContext, _id: str, tittle="", description=""):
    """Edita titulo o descripcion en un selector de roles (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    _id (str): Identificador del selector a modificar
                    tittle (str): Nuevo titulo
                    description (str): Nueva descripcion
    """

    await ctx.defer()

    for selector in query_all(ctx.guild, Collection.selectors.value):
        if selector["name"] == tittle and selector["_id"] != _id and tittle != "":
            await ctx.author.send(f"el nombre {tittle} ya existe")
            return

    selector = query_id(_id, ctx.guild, Collection.selectors.value)

    if selector is None:
        await ctx.author.send("id invalido")
        return

    if tittle != "_":
        modify("msg_id", selector["msg_id"], "name", tittle, ctx.guild, Collection.selectors.value)
    else:
        tittle = selector["name"]

    if description != "_":
        modify("msg_id", selector["msg_id"], "description", description, ctx.guild, Collection.selectors.value)
    else:
        description = selector["description"]

    selector = query_id(_id, ctx.guild, Collection.selectors.value)
    msg = await ctx.channel.fetch_message(selector["msg_id"])
    embed = discord.Embed(title=tittle, description=description)

    for key in selector["emoji_role"].keys():
        embed.add_field(name=f"Rol: {discord.utils.get(ctx.guild.roles, id=selector['emoji_role'][key]).name}",
                        value=f"Emoji: {key}")

    await msg.edit(embed=embed)
    await ctx.author.send("edicion realizada")
    await ctx.send("editado", delete_after=2)


@slash.slash(name="rolaselec", description="agrega o remueve un emoji-rol a un selector de roles",
             options=[create_option(name="id", description="id del selector", option_type=3, required=True),
                      create_option(name="emoji", description="emoji representativo del rol", option_type=3,
                                    required=True),
                      create_option(name="rol", description="mencion del rol", option_type=8, required=True)],
             connector={"id": "_id", "emoji": "emoji", "rol": "role"})
@commands.has_permissions(administrator=True)
async def toggle_role_to_selector(ctx: SlashContext, _id, emoji, role: discord.Role):
    """Añade o remueve un emoji-rol a un selector de roles (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    _id (str): Idenficador del selector
                    emoji (str): Emoji representativo del rol
                    role (float): Rol a añadir o remover
    """

    await ctx.defer()
    selector = query_id(_id, ctx.guild, Collection.selectors.value)

    if selector is None:
        await ctx.author.send("id inalido")
        return

    if emoji == "❌":
        await ctx.author.send("el emoji no puede ser ❌, ya que esta en uso por el selector")
        return

    msg = await ctx.channel.fetch_message(selector["msg_id"])
    action = ""

    if emoji in selector["emoji_role"].keys() and role.id == selector["emoji_role"][emoji]:
        del selector["emoji_role"][emoji]
        await msg.remove_reaction(emoji, client.user)
        action = "eliminado"
    else:
        for _emoji in selector["emoji_role"].keys():
            if emoji == _emoji:
                await ctx.author.send(f"el emoji {emoji} ya esta en uso")
                return
            if role.id == selector["emoji_role"][_emoji]:
                await ctx.author.send(f"el rol {role.mention} ya esta en uso")
                return
        selector["emoji_role"][emoji] = role.id
        action = "agregado"
        await msg.add_reaction(emoji)

    embed = discord.Embed(colour=discord.colour.Color.gold(), title=selector["name"], 
                          description=selector["description"])
    for key in selector["emoji_role"].keys():
        embed.add_field(name=f"Rol: {discord.utils.get(ctx.guild.roles, id=selector['emoji_role'][key]).name}",
                        value=f"Emoji: {key}")

    await msg.edit(embed=embed, content="")
    replace("msg_id", selector["msg_id"], selector, ctx.guild, Collection.selectors.value)
    await ctx.author.send(f"rol {role.mention}, emoji: {emoji} {action}")
    await ctx.send("añadido", delete_after=2)


@slash.slash(name="delrolselec", description="elimina un selector de roles",
             options=[create_option(name="id", description="id del selector", option_type=3, required=True)],
             connector={"id": "_id"})
@commands.has_permissions(administrator=True)
async def delete_role_selector(ctx: SlashContext, _id):
    """Elimina un selector de roles (SlashCommand, Admin)

            Args:
                    ctx (SlashContext): Context de discord
                    _id (str): Identificador del selector
    """

    await ctx.defer()
    selector = query_id(_id, ctx.guild, Collection.selectors.value)

    if selector is False:
        await ctx.author.send("id invalido", "", 0, True)
        return

    try:
        msg = await ctx.channel.fetch_message(selector["msg_id"])
        await msg.delete()
    except:
        pass

    delete("msg_id", selector["msg_id"], ctx.guild, Collection.selectors.value)
    await ctx.author.send(f"selector de roles {_id} eliminado")
    await ctx.send("eliminado", delete_after=2)
