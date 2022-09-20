import discord
from discord.ext import commands
import youtube_dl
import pafy

loop = False


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.client.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx, song):
        if loop:
            return await self.play_song(ctx, song)
        if len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx, song)))
        ctx.voice_client.source.volume = 0.5

    async def search_song(self, amount, song, get_url=False):
        info = await self.client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0:
            return None
        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Not currently in a channel. Please join.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            if not ctx.message.author.guild_permissions.administrator:
                return await ctx.send("You do not have sufficient permissions.")
            else:
                await ctx.voice_client.pause()
                await ctx.voice_client.move_to(voice_channel)
                await ctx.voice_client.resume()
                return await ctx.send("Moved to your channel.")

    @commands.command()
    async def connect(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("Not currently in a channel. Please join.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            return await voice_channel.connect()
        else:
            if not ctx.message.author.guild_permissions.administrator:
                return await ctx.send("You do not have sufficient permissions.")
            else:
                await ctx.voice_client.pause()
                await ctx.voice_client.move_to(voice_channel)
                await ctx.voice_client.resume()
                return await ctx.send("Moved to your channel.")

    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("I am not currently in a channel.")
        if ctx.author.voice is None:
            return await ctx.send('Nice try idiot.')
        else:
            self.song_queue[ctx.guild.id] = []
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            return await ctx.send('Goodbye.')

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send('Not currently in a channel. Please join.')
        if ctx.author.voice is None:
            return await ctx.send('Nice try idiot.')
        else:
            self.song_queue[ctx.guild.id] = []
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            return await ctx.send('Goodbye.')

    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Please enter a link.")
        if ctx.voice_client is None:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("searching")
            result = await self.search_song(1, song, get_url=True)
            if result is None:
                return await ctx.send("Song not found.")
            song = result[0]
        queue_len = len(self.song_queue[ctx.guild.id])
        if ctx.voice_client.source is not None:
            self.song_queue[ctx.guild.id].append(song)
            return await ctx.send(f"queued at position {queue_len + 1}")
        await self.play_song(ctx, song)
        await ctx.send(f"Now playing: {song}")

    @commands.command()
    async def queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("Queue is empty.")

        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description += f"{i}) {url}\n"

            i += 1

        embed.set_footer(text="Try to remember next time.")
        await ctx.send(embed=embed)

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send('Currently paused.')
        if ctx.author.voice is None:
            return await ctx.send("Not currently connected to your channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Not currently present in your channel. Nice try.")
        else:
            await ctx.send('Pausing...')
        ctx.voice_client.pause()

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send('Currently paused.')
        if ctx.author.voice is None:
            return await ctx.send("Not currently connected to your channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Not currently present in your channel. Nice try.")
        else:
            await ctx.send('Pausing...')
            ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if not ctx.voice_client.is_paused():
            return await ctx.send('Not paused currently.')
        if ctx.author.voice is None:
            return await ctx.send("Not currently connected to your channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Not currently present in your channel. Nice try.")
        else:
            await ctx.send('Resuming...')
            ctx.voice_client.resume()

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Nothing is playing...")
        if ctx.author.voice is None:
            return await ctx.send("Not currently connected to your channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Not currently present in your channel. Nice try.")
        else:
            ctx.voice_client.stop()
            return await ctx.send("Skipped.")

    @commands.command()
    async def fs(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Nothing is playing...")
        if ctx.author.voice is None:
            return await ctx.send("Not currently connected to your channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Not currently present in your channel. Nice try.")
        if not ctx.message.author.guild_permissions.administrator:
            return await ctx.send("You do not have sufficient permissions.")
        else:
            ctx.voice_client.stop()
            return await ctx.send('Force-skipped.')

    @commands.command()
    async def forceskip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Nothing is playing...")
        if ctx.author.voice is None:
            return await ctx.send("Not currently connected to your channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Not currently present in your channel. Nice try.")
        if not ctx.message.author.guild_permissions.administrator:
            return await ctx.send("You do not have sufficient permissions.")
        else:
            ctx.voice_client.stop()
            return await ctx.send('Force-skipped.')

    @commands.command()
    async def clear(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send('The queue is empty.')
        if ctx.voice_client is None:
            return await ctx.send("Nothing is currently playing.")
        if ctx.author.voice is None:
            return await ctx.send("I am not connected to a channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am in a different channel.")
        else:
            self.song_queue[ctx.guild.id] = []
            return await ctx.send('Queue cleared.')

    @commands.command()
    async def queueclear(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send('The queue is empty.')
        if ctx.voice_client is None:
            return await ctx.send("Nothing is currently playing.")
        if ctx.author.voice is None:
            return await ctx.send("I am not connected to a channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am in a different channel.")
        else:
            self.song_queue[ctx.guild.id] = []
            return await ctx.send('Queue cleared.')

    @commands.command()
    async def clearqueue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send('The queue is empty.')
        if ctx.voice_client is None:
            return await ctx.send("Nothing is currently playing.")
        if ctx.author.voice is None:
            return await ctx.send("I am not connected to a channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am in a different channel.")
        else:
            self.song_queue[ctx.guild.id] = []
            return await ctx.send('Queue cleared.')

    @commands.command()
    async def qc(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send('The queue is empty.')
        if ctx.voice_client is None:
            return await ctx.send("Nothing is currently playing.")
        if ctx.author.voice is None:
            return await ctx.send("I am not connected to a channel.")
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("I am in a different channel.")
        else:
            self.song_queue[ctx.guild.id] = []
            return await ctx.send('Queue cleared.')

    @commands.command()
    async def remove(self, ctx, number):
        if int(number) > len(self.song_queue[ctx.guild.id]):
            return await ctx.send('There are not that many songs in the queue.')
        else:
            self.song_queue[ctx.guild.id].pop(int(number)-1)
            return await ctx.send('Song successfully removed from queue.')

    @commands.command()
    async def loop(self, ctx):
        global loop
        if loop:
            await ctx.send('Loop disabled')
            loop = False
            return loop
        else:
            await ctx.send('Loop enabled')
            loop = True
            return loop
