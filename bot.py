import discord
from discord.ext import commands
import yt_dlp
import asyncio
import json

async def start_stream(search, ctx, voice_client):
  if search == '':
    search = "ac/dc back in black"
  ydl_opts = {
      "default_search": f'ytsearch:{search}',
      "format": "bestaudio",
      "extract_audio": True
    }

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
      info = ydl.extract_info(search, download=False) 
      print(search)
      sanitized_info = ydl.sanitize_info(info)
    except:
      await ctx.send('```Something went wrong```')
      return

  if sanitized_info["extractor"] == "youtube":
    # extractor is = to youtube when searching with a valid url
    source = sanitized_info["url"]
    title = sanitized_info["title"]
  elif sanitized_info["extractor"] == "youtube:search":
    # extractor is = to youtube:search for searching when the input is not a valid url
    source = sanitized_info["entries"][0]["url"]
    title = sanitized_info["entries"][0]["title"]

  audio = discord.FFmpegPCMAudio(source=source, executable="ffmpeg")
  source = discord.PCMVolumeTransformer(audio)
  voice_client.play(source, after=lambda e: print(e) if e else print("Done"))  
  
  return title
  
class Music_Bot(commands.Cog):
  def __init__(self, bot):
    self.bot = bot  

    @self.bot.event
    async def on_ready():
      print(f'Hello {self.bot.user}')

  @commands.command(brief="pong", description="pong")
  async def ping(self, ctx):
    await ctx.send('```pong```')

  @commands.command(brief="Start listening to music", descriprion="Type '!play [yt search or url]' to listen music")
  async def play(self, ctx, *search):
    if ctx.message.author.voice is not None:
      try:
        channel = ctx.message.author.voice.channel
        voice_client = await channel.connect()
      except Exception as e:
        print(e)
    else:
      await ctx.send("```Enter in a voice channel first```")
      return

    message = await ctx.send(f'```Working on it...```')

    formatted_search = ''
    for value in search:
      formatted_search += value

    song = await start_stream(formatted_search, ctx, voice_client)
    print(formatted_search)    

    if song is not None:
      await message.edit(content=f'```Currently playing {song}```')

  @commands.command(brief="Stop the current stream", descriprion="Type '!stop' to stop the current stream")
  async def stop(self, ctx):
    if (ctx.message.author.voice is not None) and ctx.voice_client.is_playing():
      ctx.voice_client.stop()

  @commands.command(brief="Pause the current stream", descriprion="Type '!pause' to pause the current stream")
  async def pause(self, ctx):
    if (ctx.message.author.voice is not None) and ctx.voice_client.is_playing():
      ctx.voice_client.pause()

  @commands.command(brief="Resume the current stream", description="Type '!resume' to resume the current stream.")
  async def resume(self, ctx):
    if (ctx.message.author.voice is not None) and ctx.voice_client.is_paused():
      ctx.voice_client.resume()

  @commands.command(brief="Leave the current vocal channel", description="Type '!leave' to make the bot leave the current vocal channel")
  async def leave(self, ctx):
    channel = ctx.voice_client
    if channel is not None:
      await channel.disconnect()

  # command used during debug, delete all the messages in a text channel
  """ @commands.command()
  async def clear(self, ctx):
    channel = ctx.message.channel
    messages = [message async for message in channel.history(limit=200)]
    await channel.delete_messages(messages) """

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

config_file = open("config.json", "r")
parsed_file = json.loads(config_file.read())

async def main():
  await bot.add_cog(Music_Bot(bot))
  await bot.start(parsed_file["token"])  

asyncio.run(main())