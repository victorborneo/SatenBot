from discord.ext import commands

from functions import send_picture  # pylint: disable=import-error


class PicturesNSFW(commands.Cog):
    """
    Commands related to NSFW pictures.
    """
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="🔞")
    async def bondage(self, ctx):
        """
        🔞
        """
        await send_picture(ctx, "nsfw/bondage", "", True)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="🔞")
    async def hentai(self, ctx):
        """
        🔞
        """
        await send_picture(ctx, "nsfw/hentai", "", True)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="🔞")
    async def thighs(self, ctx):
        """
        🔞
        """
        await send_picture(ctx, "nsfw/thighs", "", True)


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(PicturesNSFW(client))
