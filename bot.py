import os, discord, random, traceback
from discord.ext import commands, tasks
from dotenv import load_dotenv
from database import init_db, has_caught, add_catch, get_pokedex
from pokeapi import get_pokemon_data, get_capture_rate


load_dotenv()
Token = os.getenv("DISCORD_TOKEN")
owner_id = int(os.getenv("OWNER_ID"))
active_spawns = {}
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    if not auto_spawn_loop.is_running():
        auto_spawn_loop.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    traceback.print_exception(type(error), error, error.__traceback__)
    await ctx.send("Something went wrong running that command.")

db = init_db()

def is_owner(ctx):
    return ctx.author.id == owner_id

@bot.command()
async def spawn(ctx):
    if not is_owner(ctx):
        return
    if not await do_spawn(ctx.channel):
        await ctx.send("Something went wrong fetching a Pokémon, try again.")

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

    if random.random() < (spawn["capture_rate"] / 255):
        add_catch(db, ctx.author.id, pokemon_id, pokemon_name)
        del active_spawns[ctx.channel.id]
        await ctx.send(f"You caught {pokemon_name}!")
    else:
        chance = spawn["capture_rate"] / 255 * 100
        await ctx.send(f"{pokemon_name} broke free! Try again! You had a {chance:.1f}% chance.")

@bot.command()
async def pokedex(ctx):
    entries = get_pokedex(db,ctx.author.id)
    if not entries:
        await ctx.send("You haven't caught any Pokèmon yet!")
        return
    lines = [f"#{pid} {name}" for pid, name in entries]
    await ctx.send("Your Pokèdex:\n" + "\n".join(lines))


active_channel_id = None

async def do_spawn(channel):
    pokemon_id = random.randint(1, 1025)
    result = get_pokemon_data(pokemon_id)
    if result is None:
        return False
    pokemon_name, sprite_url = result
    capture_rate = get_capture_rate(pokemon_id)
    if capture_rate is None:
        return False
    active_spawns[channel.id] = {"id":pokemon_id, "name": pokemon_name, "capture_rate": capture_rate}
    await channel.send(sprite_url)
    await channel.send(f"A wild {pokemon_name} appeared! Type !catch to try to catch it.")
    return True

@bot.command()
async def start(ctx):
    if not is_owner(ctx):
        return
    global active_channel_id
    active_channel_id = ctx.channel.id
    await ctx.send("Auto-spawning enabled in this channel")

@bot.command()
async def stop(ctx):
    if not is_owner(ctx):
        return
    global active_channel_id
    active_channel_id = None
    await ctx.send("Auto-spawning disabled.")

@tasks.loop(seconds=60)
async def auto_spawn_loop():
    if active_channel_id is None or active_channel_id in active_spawns:
        return
    channel = bot.get_channel(active_channel_id)
    if channel:
        await do_spawn(channel)

@auto_spawn_loop.before_loop
async def before_auto_spawn_loop():
    await bot.wait_until_ready()

bot.run(Token)