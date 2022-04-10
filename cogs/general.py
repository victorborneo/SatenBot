from discord.ext import commands

from functions import send_message  # pylint: disable=import-error
from functions import confirm  # pylint: disable=import-error
from functions import get_next_vote  # pylint: disable=import-error
from variables import connection  # pylint: disable=import-error


class General(commands.Cog):
    """
    Generic commands.
    """

    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(brief="Sends Saten's invite link!",
                      aliases=["inv"])
    async def invite(self, ctx):
        """
        DMs Saten's invite link!
        """
        await send_message(ctx, "Here's my invite link!\n"
                           "https://discord.com/api/oauth2/"
                           "authorize?client_id=798341045607071814&"
                           "permissions=301214790&scope=bot")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(brief="Sends Saten's official support "
                      "server invite link!")
    async def support(self, ctx):
        """
        DMs Saten's official support server invite link!
        """
        await send_message(ctx,
                           "https://discord.gg/abAUn6hY4j")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(brief="Sends Saten's Patreon!")
    async def patreon(self, ctx):
        """
        DMs Saten's Patreon!
        """
        await send_message(ctx,
                           "Thanks for considering supporting me on Patreon!"
                           "\nhttps://www.patreon.com/SatenBot")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(brief="Sends Saten's Top.gg page!")
    async def vote(self, ctx):
        """
        DMs Saten's Patreon!
        """
        cursor = connection.cursor()
        nvote = cursor.execute("""
            SELECT next_vote
            FROM user
            WHERE id=:uid
        """, {"uid": ctx.message.author.id}).fetchone()
        cursor.close()

        nvote = None if nvote is None else nvote["next_vote"]
        await send_message(ctx,
                           f"Vote for Saten on top.gg!\n"
                           f"Next vote: **{get_next_vote(nvote)}\n**"
                           "https://top.gg/bot/798341045607071814/vote")

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(brief="Wipe all your data from Saten's database")
    async def blackhole(self, ctx):
        """
        Wipe all your data from Saten's database.
        This will also delete all your entries like notifiers, stickers,
        balance, bonuses, etc.
        This command has an 1 hour cooldown to prevent rerolling exploiting.
        """
        check = await confirm(ctx, self.client,
                              f"{ctx.message.author.mention}, "
                              "Are you sure you want to wipe all your data?")

        if str(check.emoji) == "✅":
            cursor = connection.cursor()
            with connection:
                cursor.execute("""
                    DELETE FROM user
                    WHERE id=:uid
                """, {"uid": ctx.message.author.id})
            cursor.close()

            await send_message(ctx, "Data wiped successfully")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(brief="Check Saten's source code on Github!")
    async def github(self, ctx):
        """
            Check Saten's source code on Github!
        """
        await send_message(ctx,
                           "Hello, fellow coder! Here's my source code!\n"
                           "https://github.com/victorborneo/SatenBot")


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(General(client))
