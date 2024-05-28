import discord
from discord.ext import commands
from discord.ui import Select

import requests

from config import API_URL

class QueueForView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.games = [(game.game_name, game.game_id) for game in self.bot.games]
    
    @discord.ui.select(
        placeholder="I want to play... (select one or more games)",
        options=self.games
    )
    


class UserSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command()
    @discord.option(
        "handle",
        description="Your YouTube handle",
        required=True,
    )
    @discord.option(
        "url",
        description="Your YouTube URL",
        required=False,
    )
    async def youtube(self, ctx, handle, url):
        def extract_id_from_url(url):
            things_before_id = ["youtube.com/watch?v=", "youtu.be/"]
            for thing in things_before_id:
                if thing in url:
                    return url.split(thing)[1].split("&")[0]

            raise Exception("Invalid YouTube URL")

        discord_id = ctx.author.id

        try:
            youtube = {}

            if handle:
                youtube["handle"] = handle

            if url:
                video_id = extract_id_from_url(url)
                youtube["video_id"] = video_id

            res = requests.post(
                API_URL + f"/player/{discord_id}",
                json={
                    "discord_id": discord_id,
                    "username": ctx.author.name,
                    "youtube": youtube,
                },
            )

            if not res.ok:
                print(res.status_code)
                raise Exception(res.text)

            await ctx.respond(
                f"Successfully linked YouTube account: @{handle}", ephemeral=True
            )

            if res.status_code == 201:
                await ctx.respond(
                    f"{res.json()['username']} is now a WiiGolfQ user: you can now queue for matches. Make sure you're streaming before you join a queue",
                    ephemeral=True,
                )

        except Exception as e:
            await ctx.respond(f"Failed to link YouTube account: {e}", ephemeral=True)

        # TODO: fix
        # # change the yt username for any match this player is in
        # for match in self.bot.active_matches:

        #     if discord_id == match['p1']['discord_id']:
        #         match['p1']['yt_username'] = yt_username
        #         break # theoretically someone should only be in one match at a time

        #     if discord_id == match['p2']['discord_id']:
        #         match['p2']['yt_username'] = yt_username
        #         break # theoretically someone should only be in one match at a time
    


def setup(bot):
    bot.add_cog(UserSettings(bot))
