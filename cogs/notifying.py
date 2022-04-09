import datetime

import discord
from discord.ext import tasks
from discord.ext import commands

from variables import bot_tasks  # pylint: disable=import-error
from variables import connection  # pylint: disable=import-error
from variables import emoji_linker  # pylint: disable=import-error
from functions import format_anime_embed  # pylint: disable=import-error
from functions import paginator  # pylint: disable=import-error
from functions import send_message  # pylint: disable=import-error
from functions import multiple_choices  # pylint: disable=import-error


@tasks.loop(hours=1)
async def notify_users(client):
    jst = datetime.datetime.today() + datetime.timedelta(hours=13)

    cursor = connection.cursor()
    cursor.execute("""
        SELECT notifies.user_id, anime.* FROM notifies, anime
        WHERE notifies.anime_id IN (SELECT id FROM anime
        WHERE broadcast LIKE :time
        AND airing IN ('Currently Airing', 'About to air'))
        AND anime.id=notifies.anime_id
    """, {"time": f"{jst.strftime('%A')}s "
          f"at {jst.strftime('%H')}%"})

    for row in cursor.fetchall():
        user = await client.fetch_user(row["user_id"])
        await send_message(user,
                           "An anime you requested me to notify you "
                           "is about to release a new episode!"
                           )
        await format_anime_embed(user, row)
    cursor.close()


@tasks.loop(hours=48)
async def wipe_finished_airing():
    cursor = connection.cursor()
    with connection:
        cursor.execute("""
            DELETE FROM notifies
            WHERE notifies.anime_id IN
            (SELECT notifies.anime_id FROM notifies
            JOIN anime ON (anime.id=notifies.anime_id)
            WHERE anime.airing='Finished Airing')
        """)
    cursor.close()


class Notifying(commands.Cog):
    """
    Commands related to Anime notification.
    """

    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(brief="Notifies new episodes from airing animes.", aliases=['n'])
    async def notify(self, ctx, *, name):
        """
        Notifies you whenever an airing anime has a new episode.
        """
        cursor = connection.cursor()
        results = cursor.execute("""
            SELECT id, name,
            IFNULL(broadcast, 'Unknown') broadcast, airing
            FROM anime
            WHERE (name LIKE :name
            OR alt_name LIKE :name)
            AND airing!='Finished Airing'
            AND NOT EXISTS
            (SELECT * FROM notifies
            WHERE user_id=:uid
            AND anime_id=anime.id)
            ORDER BY rank LIMIT 10
        """, {"name": f"%{name}%", "uid": ctx.message.author.id}).fetchall()

        if not len(results):
            await send_message(ctx, "No results. Maybe you are already being "
                               "notified by the anime with that name, or the "
                               "anime has already finished airing.")
            cursor.close()
            return

        text = "\n".join([f"{count} -> {anime['name']} at {anime['broadcast']} "
                          f"({anime['airing']})"
                          for count, anime in enumerate(results)])

        confirm = await multiple_choices(ctx, self.client, f"```{text}```")
        confirm = results[emoji_linker[str(confirm.emoji)]]

        cursor.execute("""
            INSERT OR IGNORE INTO user (id, username)
            VALUES (:uid, :name)
        """, {"uid": ctx.message.author.id,
              "name": f"{ctx.message.author.name}"
              f"#{ctx.message.author.discriminator}"})

        cursor.execute("""
            INSERT OR IGNORE INTO notifies
            VALUES (:uid, :aid)
        """, {"uid": ctx.message.author.id,
              "aid": confirm["id"]})

        connection.commit()
        cursor.close()

        await send_message(ctx, f"{ctx.message.author.mention}, "
                           "You'll be notified whenever a new episode of "
                           f"**{confirm['name']}** releases!\n"
                           "Make sure to leave your DMs open!")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(brief="Stops notifying new episodes from airing animes.",
                      aliases=["un"])
    async def unnotify(self, ctx, *, name):
        """
        Stops notifying new episodes from airing animes.
        """
        cursor = connection.cursor()
        results = cursor.execute("""
            SELECT id, name,
            IFNULL(broadcast, 'Unknown') broadcast, airing
            FROM anime
            WHERE (name LIKE :name
            OR alt_name LIKE :name)
            AND airing!='Finished Airing'
            AND EXISTS
            (SELECT * FROM notifies
            WHERE user_id=:uid
            AND anime_id=anime.id)
            ORDER BY rank LIMIT 10
        """, {"name": f"%{name}%", "uid": ctx.message.author.id}).fetchall()

        if not len(results):
            await send_message(ctx, "You aren't being notified "
                               "by any anime with that name")
            cursor.close()
            return

        text = "\n".join([f"{count} -> {anime['name']} at {anime['broadcast']} "
                          f"({anime['airing']})"
                          for count, anime in enumerate(results)])

        confirm = await multiple_choices(ctx, self.client, f"```{text}```")
        confirm = results[emoji_linker[str(confirm.emoji)]]

        cursor.execute("""
            DELETE FROM notifies
            WHERE user_id=:uid
            AND anime_id=:aid
        """, {"uid": ctx.message.author.id,
              "aid": confirm["id"]})

        connection.commit()
        cursor.close()

        await send_message(ctx, f"{ctx.message.author.mention}, "
                           "You will no longer be notified whenever a "
                           f"new episode of **{confirm['name']}** releases!")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="List of animes on notify.",
                      aliases=["nlist", "nl"])
    @commands.guild_only()
    async def notifylist(self, ctx, member: discord.Member = None):
        """
        List of animes on notify
        You can see other people's lists by tagging them.
        """

        if member is None:
            member = ctx.message.author

        cursor = connection.cursor()
        results = cursor.execute("""
            SELECT anime.name, anime.broadcast, anime.airing
            FROM anime, notifies
            WHERE notifies.user_id=:uid
            AND notifies.anime_id=anime.id
        """, {"uid": member.id}).fetchall()
        cursor.close()

        if not len(results):
            await send_message(ctx, "No animes on the notify list!")
            return

        await paginator(ctx, self.client, [discord.Embed(
            title=f"{member} Notify List Page {(i + 10) // 10}",
            description="\n".join(
                map(lambda x: f"{x['name']} - **{x['broadcast']}** "
                    f"({x['airing']})",
                    results[i:i+10])),
            color=0x00ff00
        ) for i in range(0, len(results), 10)])


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(Notifying(client))
    notify_users.start(client)
    wipe_finished_airing.start()
    bot_tasks.add_task("notifying", notify_users)
    bot_tasks.add_task("notifying", wipe_finished_airing)
