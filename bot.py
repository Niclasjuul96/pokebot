import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db, has_caught, add_catch, get_pokedex
from pokeapi import get_pokemon_name


load_dotenv()
Token = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
active_spawns = {}
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

db = init_db()

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

@bot.command()
async def spawn(ctx):
    if not is_owner(ctx):
        return
    pokemon_id = random.randint(1,151)
    pokemon_name = get_pokemon_name(pokemon_id)
    active_spawns[ctx.channel.id] = {"id": pokemon_id, "name": pokemon_name}
    await ctx.send(f"A wild {pokemon_name} appeared! Type !catch to try catch it.")

@bot.command()
async def skip(ctx):
    if not is_owner(ctx):
        return
    if ctx.channel.id in active_spawns:
        del active_spawns[ctx.channel.id]
        await ctx.send("Spawn skipped.")
    else:
        await ctx.send("Nothing is spawned right now.")

@bot.command()
async def catch(ctx):
    spawn = active_spawns.get(ctx.channel.id)
    if spawn is None:
        await ctx.send("No Pokèmon is currently spawned!")
        return

    pokemon_id, pokemon_name = spawn["id"], spawn["name"]

    if has_caught(db, ctx.author.id, pokemon_id):
        await ctx.send(f"You've already caught {pokemon_name}!")
        return

    if random.random() < 0.5:
        add_catch(db, ctx.author.id, pokemon_id, pokemon_name)
        del active_spawns[ctx.channel.id]
        await ctx.send(f"You caught {pokemon_name}!")
    else:
        await ctx.send(f"{pokemon_name} broke free! Try again!")

@bot.command()
async def pokedex(ctx):
    entries = get_pokedex(db,ctx.author.id)
    if not entries:
        await ctx.send("You haven't caught any Pokèmon yet!")
        return
    lines = [f"#{pid} {name}" for pid, name in entries]
    await ctx.send("Your Pokèdex:\n" + "\n".join(lines))

bot.run(Token)