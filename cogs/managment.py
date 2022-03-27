import os

from discord.ext import commands

from variables import connection, bot_tasks  # pylint: disable=import-error
from functions import send_message  # pylint: disable=import-error


def is_owner(ctx):
    return ctx.message.author.id == 269226420452982785


class CogManagment(commands.Cog):
    """
    Commands related to Managing cogs.
    """
    def __init__(self, client):
        self.client = client

    @commands.check(is_owner)
    @commands.command(brief="Loads an extension.")
    async def load(self, ctx, extension):
        """
        Loads an extension.
        """
        try:
            self.client.load_extension(f"cogs.{extension.lower()}")
        except commands.ExtensionAlreadyLoaded:
            await send_message(ctx, "Extension is already loaded.")
        except commands.ExtensionNotFound:
            await send_message(ctx, "Extension doesn't exist.")
        else:
            await send_message(ctx, f"Loaded extension {extension.lower()}.")

    @commands.check(is_owner)
    @commands.command(brief="Unloads an extension.")
    async def unload(self, ctx, extension):
        """
        Unloads an extension.
        """
        bot_tasks.delete_tasks(extension)

        try:
            self.client.unload_extension(f"cogs.{extension.lower()}")
        except commands.ExtensionNotLoaded:
            await send_message(ctx, "Extension is already unloaded.")
        else:
            await send_message(ctx, f"Unloaded extension {extension.lower()}.")

    @commands.check(is_owner)
    @commands.command(brief="Reloads an extension.")
    async def reload(self, ctx, extension):
        """
        Reloads an extension.
        """
        bot_tasks.delete_tasks(extension)

        try:
            self.client.unload_extension(f"cogs.{extension.lower()}")
        except commands.ExtensionNotLoaded:
            pass

        try:
            self.client.load_extension(f"cogs.{extension.lower()}")
        except commands.ExtensionNotFound:
            await send_message(ctx, "Extension doesn't exist.")
        else:
            await send_message(ctx, f"Reloaded extension {extension.lower()}.")

    @commands.check(is_owner)
    @commands.command(brief="Private command.")
    async def shutdown(self, ctx):
        """
        Private command.
        """
        connection.commit()
        await send_message(ctx, "Shutting down.")
        os._exit(1)

    @commands.check(is_owner)
    @commands.command(brief="Private command.")
    async def servers(self, ctx):
        """
        Private command.
        """
        members = 0
        for guild in self.client.guilds:
            members += guild.member_count

        await send_message(ctx, f"{len(self.client.guilds)} servers in total. "
                           f"{members} users in total.")

    @commands.check(is_owner)
    @commands.command(brief="Private command.")
    async def parserlogs(self, ctx):
        """
        Private command.
        """
        with open("parser_logs.txt", "r") as f:
            await send_message(ctx, "\n".join(map(lambda x: x.strip(),
                                                  f.readlines()[-1:-4:-1])))


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(CogManagment(client))
