import discord
from discord.ext import commands

from functions import send_picture  # pylint: disable=import-error
from functions import send_message  # pylint: disable=import-error


class PicturesCouple(commands.Cog):
    """
    Commands related to couple pictures.
    """
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Hug someone 🤗")
    @commands.guild_only()
    async def hug(self, ctx, member: discord.Member):
        """
        Hug someone!
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "hug", f"{ctx.message.author.mention} "
                           f"hugged {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Kiss someone 💋")
    @commands.guild_only()
    async def kiss(self, ctx, member: discord.Member):
        """
        Kiss someone!
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "kiss", f"{ctx.message.author.mention} "
                           f"kissed {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Lick someone 💦")
    @commands.guild_only()
    async def lick(self, ctx, member: discord.Member):
        """
        Lick someone :S
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "lick", f"{ctx.message.author.mention} "
                           f"licked {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Pat someone C:")
    @commands.guild_only()
    async def pat(self, ctx, member: discord.Member):
        """
        Pat someone c:
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "pat", f"{ctx.message.author.mention} "
                           f"patted {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Poke someone🤏")
    @commands.guild_only()
    async def poke(self, ctx, member: discord.Member):
        """
        Poke someone!
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "poke", f"{ctx.message.author.mention} "
                           f"poked {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Punch someone 👊")
    @commands.guild_only()
    async def punch(self, ctx, member: discord.Member):
        """
        Punch someone >:)
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "punch", f"{ctx.message.author.mention} "
                           f"punched {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Slap someone 👋")
    @commands.guild_only()
    async def slap(self, ctx, member: discord.Member):
        """
        Slap someone :O
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "slap", f"{ctx.message.author.mention} "
                           f"slapped {tagged}")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(brief="Tickle someone 😂")
    @commands.guild_only()
    async def tickle(self, ctx, member: discord.Member):
        """
        Tickle someone 😂
        """
        if member.id == ctx.message.author.id:
            await send_message(ctx, "Can't do that to yourself!")
            return

        tagged = f"{member.mention}!"
        if member.id == self.client.user.id:
            tagged = "Me?! 😳"

        await send_picture(ctx, "tickle", f"{ctx.message.author.mention} "
                           f"tickled {tagged}")

    @hug.error
    @kiss.error
    @lick.error
    @pat.error
    @poke.error
    @punch.error
    @slap.error
    @tickle.error
    async def member_error(self, ctx, error):
        """
        Checks if member exists.
        """
        if isinstance(error, commands.BadArgument):
            await send_message(ctx, "You need to tag a "
                               "user for this command!")


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(PicturesCouple(client))
