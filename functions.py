import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

import aiohttp
import discord
from discord.ext import commands

from variables import emoji_linker, connection
from variables import hentai_nsfw, ecchi_nsfw
from variables import odds, money_odds


logging.getLogger("aiohttp.server").setLevel(logging.CRITICAL)


async def send_message(ctx: object, message: str, dm: bool = False) -> None:
    try:
        if dm:
            return await ctx.message.author.send(message)
        return await ctx.send(message)
    except discord.errors.Forbidden:
        raise commands.BadArgument("Can't send message")


async def send_embed(ctx: object, embed: object,
                     file: object = None, dm: bool = False) -> None:
    try:
        if dm:
            return await ctx.message.author.send(embed=embed, file=file)
        return await ctx.send(embed=embed, file=file)
    except discord.errors.Forbidden:
        raise commands.BadArgument("Can't send embed")


async def send_picture(ctx: object, endpoint: str,
                       message: str = None, nsfw: bool = False) -> None:
    if nsfw and not ctx.message.channel.is_nsfw():
        await send_message(ctx, "NSFW channel required!")
        return

    link = f"https://api.dbot.dev/images/{endpoint}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(link) as response:
                if response.status == 200:
                    html = json.loads(await response.text())
                else:
                    await send_message(ctx, "An error has occurred "
                                       "while trying to contact Shiro.gg. "
                                       "The API is probably offline at "
                                       "the moment."
                                       f"\nHTTPError: {response.status}")
                    return
        except aiohttp.ClientConnectorError:
            await send_message(ctx, "An error ocurred while trying to "
                               "connect to Shiro.gg's API.")
            return

    embed = discord.Embed(description=message, color=0x00ff00)
    embed.set_image(url=html["url"])

    await send_embed(ctx, embed)


async def multiple_choices(ctx: object, client: object, text: str) -> object:
    msg = await send_message(ctx, text)

    for emoji, _ in zip(emoji_linker.keys(), range(len(text.split("\n")))):
        await msg.add_reaction(emoji)

    def check(payload):
        return payload.message_id == msg.id and \
            payload.user_id == ctx.message.author.id and \
            str(payload.emoji) in (emoji_linker.keys())

    try:
        confirm = await client.wait_for(
            "raw_reaction_add", timeout=15, check=check)
    except asyncio.TimeoutError:
        await msg.add_reaction("⏲️")
        raise commands.BadArgument("Reaction timeout.")

    await msg.delete()
    return confirm


async def paginator(ctx: object, client: object, embeds: List[discord.Embed],
                    jump_when_timeout: bool = False) -> None:
    msg = await send_embed(ctx, embeds[0])

    await msg.add_reaction("⏮")
    await msg.add_reaction("⏪")
    await msg.add_reaction("⏩")
    await msg.add_reaction("⏭")

    def check(payload):
        return payload.message_id == msg.id and \
            payload.user_id == ctx.message.author.id and \
            str(payload.emoji) in ("⏮", "⏪", "⏩", "⏭")

    page = 0
    while True:
        try:
            confirm = await client.wait_for(
                "raw_reaction_add", timeout=15, check=check)
        except asyncio.TimeoutError:
            if jump_when_timeout:
                await msg.edit(embed=embeds[-1])
            await msg.add_reaction("⏲️")
            raise commands.BadArgument("Reaction timeout.")

        emoji = str(confirm.emoji)

        if emoji == "⏮":
            page = 0
        elif emoji == "⏪":
            page -= 1
        elif emoji == "⏩":
            page += 1
        else:
            page = -1

        if page < 0:
            page = len(embeds) - 1
        elif page >= len(embeds):
            page = 0

        await msg.edit(embed=embeds[page])

        try:
            await msg.remove_reaction(emoji, confirm.member)
        except discord.errors.Forbidden:
            pass


async def confirm(ctx: object, client: object, text: str) -> object:
    msg = await send_message(ctx, text)

    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(payload):
        return payload.message_id == msg.id and \
            payload.user_id == ctx.message.author.id and \
            str(payload.emoji) in ("✅", "❌")

    try:
        confirm = await client.wait_for(
            "raw_reaction_add", timeout=15, check=check)
    except asyncio.TimeoutError:
        await msg.add_reaction("⏲️")
        raise commands.BadArgument("Reaction timeout.")

    await msg.delete()
    return confirm


async def format_anime_embed(ctx: object, anime: object) -> None:
    cursor = connection.cursor()
    genres_n_studios = cursor.execute("""
        SELECT 'genre' as type, genre.name FROM genre, has
        WHERE has.anime_id=:anime_id
        AND has.genre_id=genre.id
        UNION
        SELECT 'studio' as type, studio.name FROM studio, produced
        WHERE produced.anime_id=:anime_id
        AND produced.studio_id=studio.id
    """, {"anime_id": anime["id"]}).fetchall()
    cursor.close()

    title = f"{anime['name']} ({anime['alt_name']})"
    if anime["alt_name"] is None:
        title = anime["name"]

    genres = ", ".join((x["name"]
                       for x in genres_n_studios if x["type"] == "genre"))
    studios = ", ".join((x["name"]
                        for x in genres_n_studios if x["type"] == "studio"))
    del genres_n_studios

    if not studios:
        studios = "Unknown"

    embed = discord.Embed(title=title,
                          description=genres,
                          color=0xf0ff0f
                          )

    file = None
    if anime["image"] is not None:
        embed.set_thumbnail(url=anime["image"])

        try:
            if not ctx.message.channel.is_nsfw():
                if "Hentai" in genres:
                    file = hentai_nsfw
                    embed.set_thumbnail(url="attachment://hentai_nsfw.png")
                elif "Ecchi" in genres:
                    file = ecchi_nsfw
                    embed.set_thumbnail(url="attachment://ecchi_nsfw.png")
        except AttributeError:
            pass

    embed.add_field(name="Score", value=f"🌟 {anime['score']}", inline=True)
    embed.add_field(name="Type", value=anime["type"], inline=True)
    embed.add_field(name="Premiere", value=anime["premiere"], inline=True)
    embed.add_field(name="Rank", value=f"🏅 {anime['rank']}", inline=True)
    embed.add_field(name="Studio(s)", value=studios, inline=True)
    embed.add_field(name="Broadcast", value=anime["broadcast"], inline=True)
    embed.add_field(name="Episodes",
                    value=f"🎞️ {anime['episodes']}", inline=True)
    embed.add_field(name="Status", value=anime["airing"], inline=True)
    embed.add_field(name="MAL Page",
                    value=f"https://myanimelist.net/anime/{anime['id']}",
                    inline=True)
    embed.add_field(name="Value",
                    value=f"💰{anime['value']}",
                    inline=True)

    await send_embed(ctx, embed=embed, file=file)


def get_next_vote(next_vote: str):
    if next_vote is None:
        return "Unknown"

    now = datetime.now()
    next_vote = datetime.strptime(
        next_vote, "%Y-%m-%d %H:%M:%S.%f"
    )

    if now >= next_vote:
        return "You can vote now!"
    return str(next_vote - now)[:-7]


def get_info_by_odd(odd: float) -> Dict:
    for key in odds.keys():
        if odd <= key:
            return odds[key]
    return {"mult": 0}


def get_info_by_rank(rank: int) -> Dict:
    for value in odds.values():
        if rank <= value["end"]:
            return value
    return {"mult": 0}


def get_money_info(odd: float) -> Dict:
    for key in money_odds.keys():
        if odd <= key:
            return money_odds[key]
