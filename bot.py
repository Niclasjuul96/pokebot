import os, discord, random, traceback
from discord.ext import commands, tasks
from dotenv import load_dotenv
from database import init_db, has_caught, add_catch, get_pokedex, get_leaderboard
from pokeapi import get_pokemon_data, get_capture_rate
import asyncio

load_dotenv()
Token = os.getenv("DISCORD_TOKEN")
owner_id = int(os.getenv("OWNER_ID"))
active_spawns = {}
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CATCH_WINDOW = 15

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    if not auto_spawn_loop.is_running():
        auto_spawn_loop.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Slow down! Try again in {error.retry_after:.1f}s.")
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

async def resolve_pool(channel, pokemon_id):
    await asyncio.sleep(CATCH_WINDOW)
    spawn = active_spawns.get(channel.id)
    if spawn is None or spawn["id"] != pokemon_id:
        return
    del active_spawns[channel.id]
    pool = spawn["pool"]
    winner_id = random.choice(pool)
    add_catch(db, winner_id, spawn["id"], spawn["name"])
    winner = await bot.fetch_user(winner_id)
    await channel.send(f"{winner.display_name} caught {spawn['name']}! ({len(pool)} qualified)")

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def catch(ctx):
    spawn = active_spawns.get(ctx.channel.id)
    if spawn is None:
        await ctx.send("No Pokèmon is currently spawned!")
        return

    pokemon_id, pokemon_name = spawn["id"], spawn["name"]

    if has_caught(db, ctx.author.id, pokemon_id):
        await ctx.send(f"You've already caught {pokemon_name}!")
        return

    if ctx.author.id in spawn["pool"]:
        await ctx.send(f"You're already in the running for {pokemon_name}!")
        return

    if random.random() < (spawn["capture_rate"] / 255):
        spawn["pool"].append(ctx.author.id)
        if len(spawn["pool"]) == 1:
            asyncio.create_task(resolve_pool(ctx.channel, pokemon_id))
            await ctx.send(f"You caught a glimpse of {pokemon_name}! Others have {CATCH_WINDOW}s to jump in!")
        else:
            await ctx.send(f"You caught a glimpse of {pokemon_name}! You're in the running — results in a bit.")
    else:
        chance = spawn["capture_rate"] / 255 * 100
        await ctx.send(f"{pokemon_name} broke free! Try again! You had a {chance:.1f}% chance.")

@bot.command()
async def pokedex(ctx, member: discord.Member = None):
    member = member or ctx.author
    entries = get_pokedex(db,member.id)
    if not entries:
        await ctx.send(f"{member.display_name} haven't caught any Pokèmon yet!")
        return
    lines = [f"#{pid} {name}" for pid, name in entries]
    await ctx.send(f"{member.display_name} Pokèdex:\n" + "\n".join(lines))

@bot.command()
async def leaderboard(ctx):
    entries = get_leaderboard(db)
    if not entries:
        await ctx.send("No one has caught any Pokèmon yet!")
        return
    lines = []
    for i, (user_id, count) in enumerate(entries, start=1):
        user = await bot.fetch_user(int(user_id))
        lines.append(f"{i}, {user.display_name} - {count}")
    await ctx.send("Leaderboard:\n" + "\n".join(lines))


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
    active_spawns[channel.id] = {"id":pokemon_id, "name": pokemon_name, "capture_rate": capture_rate, "pool": []}
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