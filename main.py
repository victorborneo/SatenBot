import os
import uuid
from datetime import datetime

import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

from functions import send_message
from variables import prefix, token, logs_channel_id
from variables import database, connection


with open(f"{database}.sql", "r") as f:
    cursor = connection.cursor()
    with connection:
        cursor.executescript(f.read())
    cursor.close()

intents = discord.Intents().default()
activity = discord.Game(name=";help")
client = commands.Bot(command_prefix=prefix, intents=intents,
                      activity=activity, case_insensitive=True)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

menu = DefaultMenu('◀️', '▶️', '❌')
client.help_command = PrettyHelp(navigation=menu,
                                 color=discord.Colour.blue(),
                                 dm_help=True)


@client.event
async def on_ready():
    cursor = connection.cursor()
    guild_ids = [guild.id for guild in client.guilds]

    for id_ in guild_ids:
        cursor.execute("""
            INSERT OR IGNORE INTO guild (id)
            VALUES (:id)
        """, {"id": id_})

    cursor.execute(f"""
        DELETE FROM guild
        WHERE id NOT IN
        ({'?, ' * (len(guild_ids) - 1)}?)
    """, guild_ids)

    connection.commit()
    cursor.close()
    print("Ready.")


@client.event
async def on_guild_join(guild):
    cursor = connection.cursor()
    with connection:
        cursor.execute("""
            INSERT INTO guild (id)
            VALUES (:id)
        """, {"id": guild.id})
    cursor.close()


@client.event
async def on_guild_remove(guild):
    cursor = connection.cursor()
    with connection:
        cursor.execute("""
            DELETE FROM guild
            WHERE id=:id
        """, {"id": guild.id})
    cursor.close()


@client.event
async def on_command_error(ctx, error):
    if ctx.message.guild is None or \
        isinstance(error, commands.CommandOnCooldown) or \
            isinstance(error, commands.CheckFailure) or \
            isinstance(error, commands.BadArgument) or \
            isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await send_message(ctx,
                           "Use ';help command_goes_here' to see its syntax.")
    elif isinstance(error, commands.MissingPermissions):
        await send_message(ctx, "You don't have permission for that!")
    elif isinstance(error, commands.BotMissingPermissions):
        await send_message(ctx, "I don't have permission for that!")
    else:
        code = uuid.uuid4()

        await send_message(ctx, "Well... This is embarrasing.\n"
                           "An error has ocurred, but it has already been "
                           "automatically logged and will be fixed as "
                           "soon as possible!\nIf you still want to get "
                           "manual support, use the command ';support' and "
                           "join the official Saten server and show this "
                           f"code to a moderator:\n**{code}**")

        log = f"{code} at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}\n" \
              f"{error}, Command was: {ctx.message.content}"
        await send_message(client.get_channel(logs_channel_id), log)
        print(log)


client.run(token)
