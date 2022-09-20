import discord
from discord.ext import commands
from music import Music

client = commands.Bot(command_prefix='+', intents=discord.Intents.all())
intents = discord.Intents.default()
intents.members = True


@client.event
async def on_ready():
    print(f"{client.user.name} is ready.")


async def setup():
    await client.wait_until_ready()
    client.add_cog(Music(client))

client.loop.create_task(setup())
client.run("ODk0MDUwOTkwNTE5NjE1NTMw.YVkX3g.LrBIsrXGS9ZKUgRALGVxJaXDJ9Y")

