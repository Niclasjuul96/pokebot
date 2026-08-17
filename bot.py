import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
Token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! You are {ctx.author.name}, your ID is {ctx.author.id}")

bot.run(Token)