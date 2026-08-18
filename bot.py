import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db, has_caught, add_catch


load_dotenv()
Token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

db = init_db()


@bot.command()
async def catch(ctx, pokemon_id: int, pokemon_name: str):
    if has_caught(db, ctx.author.id, pokemon_id):
        await ctx.send(f"You've already caught {pokemon_name}!")
    else:
        add_catch(db, ctx.author.id, pokemon_id, pokemon_name)
        await ctx.send(f"You caught {pokemon_name}!")


bot.run(Token)