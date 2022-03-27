import discord
from discord import message
from discord.ext import commands

from functions import send_message  # pylint: disable=import-error
from functions import send_picture  # pylint: disable=import-error


class Pictures(commands.Cog):
    """
    Commands related to self-pictures.
    """
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Sleeping anime picture")
    async def sleep(self, ctx):
        """
        Sleeping anime picture
        """
        await send_picture(ctx, "sleep",
                           f"{ctx.message.author.mention} "
                           "is asleep 💤")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Smugging anime picture")
    async def smug(self, ctx):
        """
        Smugging anime picture
        """
        await send_picture(ctx, "smug",
                           f"{ctx.message.author.mention} "
                           "smugged 😏")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Pouting anime picture")
    async def pout(self, ctx):
        """
        Pouting anime picture
        """
        await send_picture(ctx, "pout",
                           f"{ctx.message.author.mention} "
                           "pouted!")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Nomming anime picture")
    async def nom(self, ctx):
        """
        Nomming anime picture
        """
        await send_picture(ctx, "nom",
                           f"{ctx.message.author.mention} "
                           "is nomming")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Catgirls!")
    async def neko(self, ctx):
        """
        Catgirls!
        """
        await send_picture(ctx, "neko", "")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Blushing anime picture")
    async def blush(self, ctx):
        """
        Blushing anime picture
        """
        await send_picture(ctx, "blush",
                           f"{ctx.message.author.mention} "
                           "blushed 😳")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Crying anime picture")
    async def cry(self, ctx):
        """
        Crying anime picture
        """
        await send_picture(ctx, "cry",
                           f"{ctx.message.author.mention} "
                           "is crying 😢")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Random avatar anime picture")
    async def avatar(self, ctx):
        """
        Random avatar anime picture
        """
        await send_picture(ctx, "avatars", "")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Random wallpaper anime picture")
    async def wallpaper(self, ctx):
        """
        Random wallpaper anime picture
        """
        await send_picture(ctx, "wallpapers", "")


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(Pictures(client))
