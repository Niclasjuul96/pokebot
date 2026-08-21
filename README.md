# Pokebot

A Discord bot where Pokémon spawn on a timer and users try to catch them. Catches are tracked per-user in Firebase Firestore, with catch odds based on each Pokémon's real in-game rarity (via [PokeAPI](https://pokeapi.co/)).

## Commands

| Command | Who | Description |
|---|---|---|
| `!spawn` | Owner only | Manually spawn a random Pokémon in the current channel |
| `!skip` | Owner only | Despawn the current Pokémon without catching it |
| `!catch` | Everyone | Attempt to catch the currently spawned Pokémon (10s cooldown per user) |
| `!pokedex [@user]` | Everyone | List your catches, or someone else's if you mention them |
| `!leaderboard` | Everyone | Show the top catchers server-wide by total catches |
| `!start` | Owner only | Enable auto-spawning in the current channel (spawns automatically every 60s when nothing is currently spawned) |
| `!stop` | Owner only | Disable auto-spawning |

"Owner" means whoever's Discord user ID is set as `OWNER_ID` — there's no role-based permission system yet.

## Setup

### 1. Install Python

Requires Python 3. Check what you have:

```bash
python3 --version
```

### 2. Create a virtual environment and install dependencies

```bash
cd pokebot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

(On Windows: `.venv\Scripts\activate` instead of `source .venv/bin/activate`.)

> If you're on macOS with a python.org-installed Python and hit an `SSLCertVerificationError` when the bot tries to connect to Discord, run the `Install Certificates.command` script that ships in `/Applications/Python 3.x/`.

### 3. Discord bot setup

1. Create an application and bot at the [Discord Developer Portal](https://discord.com/developers/applications).
2. Under the **Bot** tab, enable the **Message Content** privileged intent.
3. Copy the bot token.
4. Get your own Discord user ID (enable Developer Mode in Discord settings, then right-click your name → Copy User ID) — this becomes the bot "owner."

### 4. Firebase setup

1. Create a Firebase project with Firestore enabled.
2. Generate a service account key: Project Settings → Service Accounts → Generate New Private Key.
3. Save it as `firebase-key.json` in this folder (see `firebase-key.example.json` for the expected shape).

### 5. Environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
DISCORD_TOKEN=your_discord_bot_token
OWNER_ID=your_discord_user_id
```

### 6. Run it

```bash
source .venv/bin/activate
python bot.py
```

## Notes

- `active_spawns` and `active_channel_id` live in memory only — they reset on every restart. After restarting, you'll need to run `!start` again to re-enable auto-spawning.
- Not every Pokémon has an animated sprite; the bot falls back to static official artwork when one isn't available (mostly recent Gen 9 Pokémon).
</content>
