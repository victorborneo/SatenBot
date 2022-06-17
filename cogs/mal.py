import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from functions import send_embed  # pylint: disable=import-error
from functions import paginator  # pylint: disable=import-error
from functions import send_message  # pylint: disable=import-error
from functions import multiple_choices  # pylint: disable=import-error
from functions import format_anime_embed  # pylint: disable=import-error
from variables import connection  # pylint: disable=import-error
from variables import emoji_linker  # pylint: disable=import-error


class MyAnimeList(commands.Cog):
    """
    Commands related to MAL.
    """

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name='test',
        guild_ids=[798335764555366411]
    )
    async def _test(self, ctx: SlashContext):
        await ctx.send('worked!')

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(brief="Checks MAL's top animes.",
                      aliases=["t"])
    @commands.guild_only()
    async def top(self, ctx):
        """
        List of top 1000 anime on MAL.
        """
        cursor = connection.cursor()
        animes = cursor.execute("""
            SELECT rank, name, score FROM anime
            ORDER BY rank LIMIT 1000
        """).fetchall()
        cursor.close()

        await paginator(ctx, self.client, [discord.Embed(
            title=f"Top 1000 Anime Page {(i + 10) // 10}/100",
            description="\n".join(
                map(lambda x: f"**{x['rank']}** - {x['name']} "
                        f"🌟**{x['score']}**", animes[i:i + 10])),
            color=0x0000ff
        ) for i in range(0, 1000, 10)])

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(bried="Checks MAL'S top airing anime.",
                      aliases=["ta"])
    @commands.guild_only()
    async def topairing(self, ctx):
        """
        Checks MAL'S top airing anime.
        This command does not consider animes with
        an N/A rank or score.
        """
        cursor = connection.cursor()
        animes = cursor.execute("""
            SELECT rank, name, score, IFNULL(broadcast, 'Unknown') broadcast
            FROM anime
            WHERE airing='Currently Airing'
            AND rank!='N/A' AND score!='N/A'
            ORDER BY rank LIMIT 1000
        """).fetchall()
        cursor.close()

        await paginator(ctx, self.client, [discord.Embed(
            title=f"Top Airing Anime Page {(i + 10) // 10}",
            description="\n".join(
                map(lambda x: f"**{x['rank']}** - {x['name']} "
                        f"at **{x['broadcast']}** 🌟**{x['score']}**",
                        animes[i:i + 10])),
            color=0x0000ff
        ) for i in range(0, len(animes), 10)])

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(bried="Checks MAL'S top anime with an specific genre.",
                      aliases=["tg"])
    @commands.guild_only()
    async def topgenre(self, ctx, *, genre):
        """
        Checks MAL'S top anime with an specific genre
        """
        cursor = connection.cursor()
        animes = cursor.execute("""
            SELECT anime.rank, anime.name, anime.score
            FROM anime
            JOIN has ON anime.id=has.anime_id
            JOIN genre ON has.genre_id=genre.id
            WHERE genre.name=:genre COLLATE NOCASE
            ORDER BY rank
            LIMIT 1000
        """, {"genre": genre}).fetchall()
        cursor.close()

        if not len(animes):
            await send_message(ctx, "Nothing found, maybe you typed "
                               "the wrong genre? Use ';genres' to see "
                               "all available genres!")
            return

        await paginator(ctx, self.client, [discord.Embed(
            title=f"Top {genre.capitalize()} Anime Page {(i + 10) // 10}",
            description="\n".join(
                map(lambda x: f"**{x['rank']}** - {x['name']} "
                    f"🌟**{x['score']}**", animes[i:i + 10])),
            color=0x0000ff
        ) for i in range(0, len(animes), 10)])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(brief="Searches an anime.", aliases=["s"])
    async def search(self, ctx, *, name):
        """
        Searches an anime by its name
        """
        cursor = connection.cursor()
        results = cursor.execute("""
            SELECT * FROM anime
            WHERE name LIKE :name
            OR alt_name LIKE :name
            ORDER BY rank LIMIT 10
        """, {"name": f"%{name}%"}).fetchall()
        cursor.close()

        if not len(results):
            await send_message(ctx, "No results with such name")
            return

        text = "\n".join([f"{count} -> {anime['name']}" for count,
                          anime in enumerate(results)])

        confirm = await multiple_choices(ctx, self.client, f"```{text}```")
        await format_anime_embed(ctx,
                                 results[emoji_linker[str(confirm.emoji)]]
                                 )

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(brief="List of all genres and how many animes each.")
    async def genres(self, ctx):
        """
        List of all genres and how many animes each has.
        """
        cursor = connection.cursor()
        genres = cursor.execute("""
            SELECT genre.name, COUNT(*) AS c FROM has, genre
            WHERE has.genre_id=genre.id
            GROUP BY genre.name
            ORDER BY c DESC
        """).fetchall()
        cursor.close()

        embed = discord.Embed(title="Genres",
                              color=0xff00ff)

        for row in genres:
            embed.add_field(name=row["name"], value=row["c"], inline=True)

        await send_embed(ctx, embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(bried="Checks animes releasing in the next 6 days.",
                      aliases=["r"])
    @commands.guild_only()
    async def releases(self, ctx):
        """
        Checks animes releasing in the next 6 days.
        """
        cursor = connection.cursor()
        animes = cursor.execute("""
            SELECT name, premiere
            FROM anime
            WHERE airing='About to air'
            ORDER BY premiere
            LIMIT 1000
        """).fetchall()
        cursor.close()

        if not len(animes):
            await send_message(ctx, "No animes releasing soon!")
            return

        await paginator(ctx, self.client, [discord.Embed(
            title=f"Anime Page {(i + 10) // 10}",
            description="\n".join(
                map(
                    lambda x: f"{x['name']} **{x['premiere']}**",
                    animes[i:i + 10])
                ),
            color=0x0000ff
        ) for i in range(0, len(animes), 10)])


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(MyAnimeList(client))
