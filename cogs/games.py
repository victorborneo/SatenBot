import random

from discord.ext import commands

from functions import send_message  # pylint: disable=import-error
from variables import responses  # pylint: disable=import-error


class Games(commands.Cog):
    """
    Commands related to Games.
    """
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(brief="Uh... A dice... I guess?")
    async def dice(self, ctx, sides):
        """
        Randomly picks a number between 1 and <sides> inclusive.
        """
        try:
            sides = int(sides)
        except ValueError:
            await send_message(ctx, f"'{sides}' is not a valid argument.")
            return

        if sides > 100000:
            await send_message(ctx, "Please, Keep <sides> upto 100,000.")
            return

        await send_message(ctx, f"{random.randint(1, int(sides))}")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="8ball", brief="Ask a question to the magic ball!")
    async def _8ball(self, ctx, *, question):
        """
        Answers a <question> randomly.
        """
        await send_message(ctx,
                           f"Q: {question}\nA: {random.choice(responses)}")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(brief="Flip a coin!", aliases=["fp"])
    async def flipcoin(self, ctx):
        """
        Randomly chooses between heads or tails.
        """
        await send_message(ctx, f"{random.choice(('Heads', 'Tails'))}!")


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(Games(client))
