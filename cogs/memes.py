import discord
from discord.ext import commands

from functions import send_embed  # pylint: disable=import-error


class Memes(commands.Cog):
    """
    Commands related to Memes.
    """
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Naisu!")
    async def naisu(self, ctx):
        """
        Naisu!
        """
        embed = discord.Embed(description=f"{ctx.message.author.mention}"
                              " said Naisu!", color=0xffd700)
        embed.set_image(
            url="https://c.tenor.com/6aysL57nX_wAAAAC/nice-joseph-joestar.gif")
        await send_embed(ctx, embed)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Noice!")
    async def noice(self, ctx):
        """
        Noice!
        """
        embed = discord.Embed(description=f"{ctx.message.author.mention}"
                              " said Noice!", color=0xffd700)
        embed.set_image(
            url="https://c.tenor.com/KMxrZ-A6ev4AAAAC/nice-smack.gif")
        await send_embed(ctx, embed)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Pizza time!", aliases=["pizza"])
    async def pizzatime(self, ctx):
        """
        Pizza time!
        """
        embed = discord.Embed(description=f"{ctx.message.author.mention}"
                              " thinks it's Pizza Time 🍕!", color=0xffd700)
        embed.set_image(
            url="https://c.tenor.com/iHLHKfvRblIAAAAC/pizza-time-its.gif")
        await send_embed(ctx, embed)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Wow!")
    async def wow(self, ctx):
        """
        Wow!
        """
        embed = discord.Embed(description=f"{ctx.message.author.mention}"
                              " said Wow!", color=0xffd700)
        embed.set_image(
            url="https://c.tenor.com/RFgnFksI6K0AAAAC/wow-wink.gif")
        await send_embed(ctx, embed)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="U serious?")
    async def userious(self, ctx):
        """
        Are you serious?
        """
        embed = discord.Embed(description=f"{ctx.message.author.mention}"
                              " can't believe what you just said...",
                              color=0xffd700)
        embed.set_image(
            url="https://c.tenor.com/zkoIACGvSEIAAAAd/are-you.gif")
        await send_embed(ctx, embed)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Uh...")
    async def chloe(self, ctx):
        """
        Uh...
        """
        embed = discord.Embed(description=f"{ctx.message.author.mention}"
                              " doesn't like where this is going...",
                              color=0xffd700)
        embed.set_image(
            url="https://c.tenor.com/Q5jOYOfpUmMAAAAC/"
            "are-you-serious-seriously.gif")
        await send_embed(ctx, embed)


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(Memes(client))
