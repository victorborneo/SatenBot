import discord
from discord.ext import commands

from functions import send_message  # pylint: disable=import-error


class Users(commands.Cog):
    """
    Commands related to Users.
    """
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(brief="Send avatar picture of an user.",
                      aliases=["uavatar"])
    async def useravatar(self, ctx, member: discord.Member = None):
        """
        Send avatar picture of a specified user.
        """
        member = member if member is not None else ctx.message.author
        await send_message(ctx, member.avatar_url)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(brief="Kick an user.")
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kick an user.
        """
        try:
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await send_message(ctx, "That user is too powerful...")
        else:
            await send_message(ctx, f"Kicked {member.mention}.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(brief="Ban an user.")
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Ban un user.
        """
        try:
            await member.ban(reason=reason)
        except discord.errors.Forbidden:
            await send_message(ctx, "That user is too powerful...")
        else:
            await send_message(ctx, f"Banned {member.mention}.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(brief="Unban an user.")
    async def unban(self, ctx, *, member):
        """
        Unban an user.
        Use the format username#discriminator
        """
        banned_users = await ctx.guild.bans()

        try:
            member_name, member_disc = member.split('#')
        except ValueError:
            await send_message(ctx, "Invalid format! "
                                    "Make sure to include "
                                    "the user's discriminator: User#0000")
            return
        else:
            for bans in banned_users:
                if (bans.user.name, bans.user.discriminator) == \
                        (member_name, member_disc):
                    await ctx.guild.unban(bans.user)
                    await send_message(ctx, f"Unbanned {bans.user.mention}.")
                    return

        await send_message(ctx, "User not found. Make sure to "
                                "differentiate capital letters.")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(brief="List of all banned users and reason for the ban.",
                      aliases=["bl"])
    async def banlist(self, ctx):
        """
        List of all banned users and reason for the ban, if there's one.
        """
        banned_users = await ctx.guild.bans()
        message = ""

        if len(banned_users):
            message = (f"{person.user.mention} - "
                       f"{person.user.name}#{person.user.discriminator}\n"
                       f"Reason: {person.reason}" for person in banned_users)

            await send_message(ctx, "\n".join(message))
        else:
            await send_message(ctx, "No banned users in this server!")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_guild_permissions(mute_members=True)
    @commands.bot_has_guild_permissions(mute_members=True)
    @commands.command(brief="Mute an user.")
    async def mute(self, ctx, member: discord.Member):
        """
        Mute an user microphone.
        """
        try:
            await member.edit(mute=True)
        except discord.HTTPException:
            await send_message(ctx, "Member not connected to any voice chat.")
        else:
            await send_message(ctx, f"Muted {member.mention}.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_guild_permissions(mute_members=True)
    @commands.bot_has_guild_permissions(mute_members=True)
    @commands.command(brief="Unmute an user.")
    async def unmute(self, ctx, member: discord.Member):
        """
        Unmute an user microhphone.
        """
        try:
            await member.edit(mute=False)
        except discord.HTTPException:
            await send_message(ctx, "Member not connected to any voice chat.")
        else:
            await send_message(ctx, f"Unmuted {member.mention}.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_guild_permissions(deafen_members=True)
    @commands.bot_has_guild_permissions(deafen_members=True)
    @commands.command(brief="Deafen an user.")
    async def deafen(self, ctx, member: discord.Member):
        """
        Deafen an user audio.
        """
        try:
            await member.edit(deafen=True)
        except discord.HTTPException:
            await send_message(ctx, "Member not connected to any voice chat.")
        else:
            await send_message(ctx, f"Deafened {member.mention}.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_guild_permissions(deafen_members=True)
    @commands.bot_has_guild_permissions(deafen_members=True)
    @commands.command(brief="Undeafen an user.")
    async def undeafen(self, ctx, member: discord.Member):
        """
        Undeafen an user audio.
        """
        try:
            await member.edit(deafen=False)
        except discord.HTTPException:
            await send_message(ctx, "Member not connected to any voice chat.")
        else:
            await send_message(ctx, f"Undeafened {member.mention}.")

    @kick.error
    @ban.error
    @mute.error
    @unmute.error
    @deafen.error
    @undeafen.error
    async def member_error(self, ctx, error):
        """
        Checks if member exists.
        """
        if isinstance(error, commands.BadArgument):
            await send_message(ctx, "Unknown user.")


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(Users(client))
