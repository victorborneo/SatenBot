from datetime import datetime, timedelta

import dbl
from discord.ext import commands

from variables import connection  # pylint: disable=import-error
from variables import topgg_token  # pylint: disable=import-error
from variables import webhook_auth  # pylint: disable=import-error
from variables import webhook_port  # pylint: disable=import-error


class TopGG(commands.Cog):
    """
    Top.gg listener.
    """

    def __init__(self, client):
        self.client = client
        self.token = topgg_token
        self.dblpy = dbl.DBLClient(self.client, self.token,
                                   webhook_path="/dblwebhook",
                                   webhook_auth=webhook_auth,
                                   webhook_port=webhook_port)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        """
        Gives user rewards for voting for the bot.
        """
        next_vote = datetime.now() + timedelta(hours=12)
        user = await self.client.fetch_user(data["user"])

        cursor = connection.cursor()
        with connection:
            cursor.execute("""
                INSERT INTO user (id, username, next_vote)
                VALUES (:uid, :name, :nvote)
                ON CONFLICT(id) DO UPDATE SET
                next_vote=:nvote WHERE id=:uid
            """, {"uid": data["user"],
                  "name": str(user),
                  "nvote": str(next_vote)})
        cursor.close()


def setup(client):
    """
    Setup the Cog.
    """
    client.add_cog(TopGG(client))
