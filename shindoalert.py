"""
Shindo Life Sub Ability & Ninja Tool Scroll Alert Bot
Real spawn times (PST) from official wiki data.
Pings @everyone on spawn. !next ability / !next weapon commands.
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import pytz
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("shindo_bot")

# ─── CONFIG ───────────────────────────────────────────────────────────────────

import os
BOT_TOKEN        = os.environ["BOT_TOKEN"]
ALERT_CHANNEL_ID = 1532804518339936338

PST = pytz.timezone("US/Pacific")

# ─── SPAWN DATA ───────────────────────────────────────────────────────────────
# All times in PST. Each item spawns AM and PM (same clock time, twice a day).
# type: "ability" | "weapon"

SCROLLS = [
    # ── SUB ABILITIES ──────────────────────────────────────────────────────
    {"name": "Air Style: Odama Spirit Bomb",    "type": "ability", "location": "Training Fields",       "time": (10, 30)},
    {"name": "Akuma Eternal Hand",              "type": "ability", "location": "Ember",                 "time": (9,  20)},
    {"name": "Bat Cursed Spirit",               "type": "ability", "location": "Forest of Embers",      "time": (11, 15)},
    {"name": "Captain Jokei",                   "type": "ability", "location": "Obelisk",               "time": (2,  30)},
    {"name": "Chu Tailed Spirit Gen 2",         "type": "ability", "location": "Dunes Village",         "time": (4,  10)},
    {"name": "Cobra Spirit Awaken",             "type": "ability", "location": "Obelisk",               "time": (11, 35)},
    {"name": "Cobra Stretch Mode",              "type": "ability", "location": "Tempest",               "time": (4,  45)},
    {"name": "Confusion Illusion Technique",    "type": "ability", "location": "Blaze",                 "time": (5,  10)},
    {"name": "Demon Gate Spirit",               "type": "ability", "location": "Ember",                 "time": (12, 30)},
    {"name": "Demon Warp",                      "type": "ability", "location": "Forest of Embers",      "time": (11, 45)},
    {"name": "Demonic Spirit",                  "type": "ability", "location": "Haze",                  "time": (11, 45)},
    {"name": "Divination Spirit",               "type": "ability", "location": "Blaze",                 "time": (11, 20)},
    {"name": "Dunes Fate Spirit",               "type": "ability", "location": "Dunes",                 "time": (1,  30)},
    {"name": "Eagle Companion",                 "type": "ability", "location": "Nimbus",                "time": (6,  15)},
    {"name": "Ember Fate Spirit",               "type": "ability", "location": "Ember",                 "time": (2,  25)},
    {"name": "Exploding Vanishing Image",       "type": "ability", "location": "Forest of Embers",      "time": (3,  30)},
    {"name": "Finite Strength Spirit",          "type": "ability", "location": "Training Fields",       "time": (11, 45)},
    {"name": "Fire Shurikens",                  "type": "ability", "location": "Forest of Embers",      "time": (6,  30)},
    {"name": "Gai Tailed Spirit Gen 2",         "type": "ability", "location": "Nimbus",                "time": (5,  25)},
    {"name": "Great Spiraling Spirit Bomb",     "type": "ability", "location": "Great Narumaki Bridge", "time": (9,  15)},
    {"name": "Haze Fate Spirit",                "type": "ability", "location": "Haze",                  "time": (3,  20)},
    {"name": "Heavenly Spirit",                 "type": "ability", "location": "Dunes",                 "time": (3,  45)},
    {"name": "Heavenly Wall",                   "type": "ability", "location": "Obelisk",               "time": (12, 10)},
    {"name": "Isu Tailed Spirit Gen 2",         "type": "ability", "location": "Haze",                  "time": (6,  30)},
    {"name": "Jayramaki Frog Spirit",           "type": "ability", "location": "Ember",                 "time": (11, 45)},
    {"name": "Kor Tailed Spirit Gen 2",         "type": "ability", "location": "Ember",                 "time": (3,  10)},
    {"name": "Ku Tailed Spirit Gen 2",          "type": "ability", "location": "Obelisk",               "time": (9,  10)},
    {"name": "Lightning Shurikens",             "type": "ability", "location": "Training Fields",       "time": (7,  10)},
    {"name": "Mao Tailed Spirit Gen 2",         "type": "ability", "location": "Nimbus",                "time": (12, 10)},
    {"name": "Medical Mode-Transfer",           "type": "ability", "location": "Ember",                 "time": (8,  35)},
    {"name": "Multi-Vanishing Clones",          "type": "ability", "location": "Ember",                 "time": (9,  25)},
    {"name": "Narumaki Barrage",                "type": "ability", "location": "Great Narumaki Bridge", "time": (10, 15)},
    {"name": "Narumaki Toad Spirit",            "type": "ability", "location": "Ember",                 "time": (11, 45)},
    {"name": "Narumaki Vanishing Clone",        "type": "ability", "location": "Great Narumaki Bridge", "time": (11, 10)},
    {"name": "Narumaki Vanishing Multi-Clone",  "type": "ability", "location": "Great Narumaki Bridge", "time": (12, 25)},
    {"name": "Nimbus Fate Spirit",              "type": "ability", "location": "Nimbus",                "time": (5,  10)},
    {"name": "Obelisk Fate Spirit",             "type": "ability", "location": "Obelisk",               "time": (4,  30)},
    {"name": "Peekaboo Jutsu",                  "type": "ability", "location": "Training Fields",       "time": (8,  20)},
    {"name": "Reality Style: Warp",             "type": "ability", "location": "Ember",                 "time": (9,  45)},
    {"name": "Reality Talk",                    "type": "ability", "location": "Blaze",                 "time": (2,  35)},
    {"name": "Reaper Spirit",                   "type": "ability", "location": "Forest of Embers",      "time": (5,  25)},
    {"name": "Reaper Spirit (SL2)",             "type": "ability", "location": "Forest of Embers",      "time": (4,  25)},
    {"name": "Reptile Cursed Spirit",           "type": "ability", "location": "Blaze",                 "time": (9,  20)},
    {"name": "Saberu Surprise",                 "type": "ability", "location": "Training Fields",       "time": (10, 50)},
    {"name": "Sei Tailed Spirit Gen 2",         "type": "ability", "location": "Haze",                  "time": (7,  10)},
    {"name": "Senko: Spirit Bomb",              "type": "ability", "location": "Ember",                 "time": (1,  15)},
    {"name": "Senko: Storm",                    "type": "ability", "location": "Obelisk",               "time": (2,  40)},
    {"name": "Shock Cloak",                     "type": "ability", "location": "Nimbus",                "time": (4,  35)},
    {"name": "Shock Style: Dual Electro",       "type": "ability", "location": "Forest of Embers",      "time": (11, 45)},
    {"name": "Shock Style: Electro Blade",      "type": "ability", "location": "Ember",                 "time": (12, 55)},
    {"name": "Shockslam Technique",             "type": "ability", "location": "Obelisk",               "time": (12, 35)},
    {"name": "Snail Spirit Awaken",             "type": "ability", "location": "Obelisk",               "time": (2,  20)},
    {"name": "Snake Summon",                    "type": "ability", "location": "Tempest",               "time": (12, 35)},
    {"name": "Specialist Spirit",               "type": "ability", "location": "Ember",                 "time": (2,  35)},
    {"name": "Spider Cursed Spirit",            "type": "ability", "location": "Training Fields",       "time": (11, 20)},
    {"name": "Spirit Bomb-Shuriken Rush",       "type": "ability", "location": "Ember",                 "time": (11, 45)},
    {"name": "Spirit Bomb-Shuriken Toss",       "type": "ability", "location": "Nimbus",                "time": (11, 45)},
    {"name": "Spirit Spear",                    "type": "ability", "location": "Training Fields",       "time": (10, 30)},
    {"name": "Su Tailed Spirit Gen 2",          "type": "ability", "location": "Dunes",                 "time": (12, 30)},
    {"name": "Sun Tailed Spirit Gen 2",         "type": "ability", "location": "Obelisk",               "time": (8,  30)},
    {"name": "Super Odama Spirit Bomb",         "type": "ability", "location": "Forest of Embers",      "time": (11, 45)},
    {"name": "Toad Cursed Spirit",              "type": "ability", "location": "Tempest",               "time": (10, 20)},
    {"name": "Toad Summon",                     "type": "ability", "location": "Tempest",               "time": (8,  20)},
    {"name": "Tree Illusion Technique",         "type": "ability", "location": "Ember",                 "time": (4,  15)},
    {"name": "Vanishing Clone: Barrage",        "type": "ability", "location": "Ember",                 "time": (1,  40)},
    {"name": "Vanishing Image",                 "type": "ability", "location": "Ember",                 "time": (11, 45)},
    {"name": "Vanishing Spirit Bomb",           "type": "ability", "location": "Forest of Embers",      "time": (1,  25)},
    {"name": "Water Vanishing Image",           "type": "ability", "location": "Obelisk",               "time": (2,  15)},
    {"name": "Wood Vanishing Image",            "type": "ability", "location": "Nimbus",                "time": (12, 10)},

    # ── NINJA TOOLS / WEAPONS ──────────────────────────────────────────────
    {"name": "Acrobat Style",                   "type": "weapon",  "location": "Nimbus",                "time": (6,  15)},
    {"name": "Air Style Fan",                   "type": "weapon",  "location": "Dunes",                 "time": (3,  25)},
    {"name": "Alphirama Blade",                 "type": "weapon",  "location": "Obelisk",               "time": (6,  40)},
    {"name": "Apollo Blade",                    "type": "weapon",  "location": "Great Narumaki Bridge", "time": (10, 45)},
    {"name": "Azim Dual Senko",                 "type": "weapon",  "location": "Ember",                 "time": (11, 50)},
    {"name": "Bankai Blade",                    "type": "weapon",  "location": "Training Fields",       "time": (12, 25)},
    {"name": "Bomb Blade",                      "type": "weapon",  "location": "Haze",                  "time": (9,  10)},
    {"name": "Bubble Flute",                    "type": "weapon",  "location": "Haze",                  "time": (10, 40)},
    {"name": "Chi Kunai",                       "type": "weapon",  "location": "Ember",                 "time": (11, 45)},
    {"name": "Chi Rod Toss",                    "type": "weapon",  "location": "Blaze",                 "time": (10, 25)},
    {"name": "Dagai Sword",                     "type": "weapon",  "location": "Dunes",                 "time": (3,  40)},
    {"name": "Demon Toss",                      "type": "weapon",  "location": "Haze",                  "time": (11, 40)},
    {"name": "Demon-Scythe",                    "type": "weapon",  "location": "Dawn Hideout",          "time": (9,  40)},
    {"name": "Dio Senko Blade",                 "type": "weapon",  "location": "Ember",                 "time": (12, 35)},
    {"name": "Dual Chi Rods",                   "type": "weapon",  "location": "Blaze",                 "time": (3,  20)},
    {"name": "Dual Lightning",                  "type": "weapon",  "location": "Haze",                  "time": (6,  20)},
    {"name": "Dual-Bladed Scythe",              "type": "weapon",  "location": "Haze",                  "time": (6,  45)},
    {"name": "Dunes Chi Blade",                 "type": "weapon",  "location": "Dunes",                 "time": (10, 25)},
    {"name": "Electro Blade",                   "type": "weapon",  "location": "Dunes",                 "time": (2,  50)},
    {"name": "Ember Chi Blade",                 "type": "weapon",  "location": "Ember",                 "time": (9,  25)},
    {"name": "Forged Umpire Fan",               "type": "weapon",  "location": "Dawn Hideout",          "time": (9,  0 )},
    {"name": "Grass Tanto",                     "type": "weapon",  "location": "Dawn Hideout",          "time": (8,  20)},
    {"name": "Hamaxe",                          "type": "weapon",  "location": "Haze",                  "time": (6,  10)},
    {"name": "Haze Chi Blade",                  "type": "weapon",  "location": "Haze",                  "time": (12, 25)},
    {"name": "Heaven Blade",                    "type": "weapon",  "location": "Tempest",               "time": (1,  15)},
    {"name": "Kokotsu Blade",                   "type": "weapon",  "location": "Obelisk",               "time": (1,  10)},
    {"name": "Moon Staff",                      "type": "weapon",  "location": "Forest of Embers",      "time": (10, 30)},
    {"name": "Nimbus Chi Blade",                "type": "weapon",  "location": "Nimbus",                "time": (11, 25)},
    {"name": "Nimbus Sword",                    "type": "weapon",  "location": "Nimbus",                "time": (4,  25)},
    {"name": "Obelisk Chi Blade",               "type": "weapon",  "location": "Obelisk",               "time": (8,  25)},
    {"name": "Pika Blade",                      "type": "weapon",  "location": "Tempest",               "time": (5,  32)},
    {"name": "Raion Blade",                     "type": "weapon",  "location": "Obelisk",               "time": (2,  25)},
    {"name": "Riser Akuma Blade",               "type": "weapon",  "location": "Tempest",               "time": (4,  44)},
    {"name": "Riserdawn",                       "type": "weapon",  "location": "Haze",                  "time": (5,  55)},
    {"name": "Rykan Blade",                     "type": "weapon",  "location": "Haze",                  "time": (2,  10)},
    {"name": "Saberu Tanto",                    "type": "weapon",  "location": "Training Fields",       "time": (11, 20)},
    {"name": "Samurai Tanto",                   "type": "weapon",  "location": "Nimbus",                "time": (4,  45)},
    {"name": "Satori Blade",                    "type": "weapon",  "location": "Ember",                 "time": (2,  10)},
    {"name": "Savage Blade",                    "type": "weapon",  "location": "Obelisk",               "time": (8,  25)},
    {"name": "Senko Kunai",                     "type": "weapon",  "location": "Ember",                 "time": (12, 10)},
    {"name": "Shark Sword",                     "type": "weapon",  "location": "Dawn Hideout",          "time": (10, 10)},
    {"name": "Shindai Prime Blade",             "type": "weapon",  "location": "Shindai Valley",        "time": (1,  25)},
    {"name": "Shindai Umpire Fan",              "type": "weapon",  "location": "Dawn Hideout",          "time": (1,  15)},
    {"name": "Shindo Blade",                    "type": "weapon",  "location": "Nimbus",                "time": (4,  55)},
    {"name": "Shiver Tanto",                    "type": "weapon",  "location": "Forest of Embers",      "time": (2,  45)},
    {"name": "Shizen Raijin",                   "type": "weapon",  "location": "Ember",                 "time": (3,  15)},
    {"name": "SL2 Bomb Blade",                  "type": "weapon",  "location": "Dunes",                 "time": (11, 15)},
    {"name": "SL2 Chi Kunai",                   "type": "weapon",  "location": "Ember",                 "time": (8,  15)},
    {"name": "SL2 Dual Lightning",              "type": "weapon",  "location": "Haze",                  "time": (2,  15)},
    {"name": "SL2 Grass Tanto",                 "type": "weapon",  "location": "Obelisk",               "time": (4,  15)},
    {"name": "SL2 Heaven Blade",                "type": "weapon",  "location": "Dawn Hideout",          "time": (5,  15)},
    {"name": "SL2 Nimbus Sword",                "type": "weapon",  "location": "Nimbus",                "time": (9,  15)},
    {"name": "SL2 Senko Kunai",                 "type": "weapon",  "location": "Ember",                 "time": (12, 15)},
    {"name": "SL2 Shindai Prime Blade",         "type": "weapon",  "location": "Dawn Hideout",          "time": (1,  15)},
    {"name": "SL2 Slayer Blade",                "type": "weapon",  "location": "Dawn Hideout",          "time": (10, 15)},
    {"name": "SL2 Thread Blade",                "type": "weapon",  "location": "Haze",                  "time": (3,  15)},
    {"name": "Slayer Blade",                    "type": "weapon",  "location": "Haze",                  "time": (5,  40)},
    {"name": "Sound Flute",                     "type": "weapon",  "location": "Obelisk",               "time": (4,  40)},
    {"name": "Stone Buster",                    "type": "weapon",  "location": "Obelisk",               "time": (7,  40)},
    {"name": "Sun Staff",                       "type": "weapon",  "location": "Training Fields",       "time": (12, 15)},
    {"name": "Thread Blade",                    "type": "weapon",  "location": "Haze",                  "time": (6,  30)},
    {"name": "Triple Cobalt Blade",             "type": "weapon",  "location": "Obelisk",               "time": (7,  25)},
    {"name": "Two Bladed Scythe",               "type": "weapon",  "location": "Obelisk",               "time": (8,  40)},
    {"name": "Umpire Guitar",                   "type": "weapon",  "location": "Obelisk",               "time": (8,  10)},
]

# ─── TIME HELPERS ─────────────────────────────────────────────────────────────

def next_spawn_dt(hour: int, minute: int) -> datetime:
    """
    Returns the next datetime (PST-aware) when this spawn fires.
    Each scroll spawns twice: AM (as listed) and PM (hour + 12, mod 24).
    Picks whichever of the two upcoming windows is soonest.
    """
    now_pst = datetime.now(PST)
    candidates = []
    for h in [hour, (hour + 12) % 24]:
        candidate = now_pst.replace(hour=h, minute=minute, second=0, microsecond=0)
        if candidate <= now_pst:
            candidate += timedelta(days=1)
        candidates.append(candidate)
    return min(candidates)


def seconds_until(hour: int, minute: int) -> float:
    return (next_spawn_dt(hour, minute) - datetime.now(PST)).total_seconds()


def format_countdown(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def format_pst(dt: datetime) -> str:
    return dt.strftime("%I:%M %p PST")

# ─── BOT ──────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Track which (name, am_or_pm) pairs have already alerted this cycle
# key: (scroll_name, "am"|"pm"), value: True
_alerted: dict[tuple[str, str], bool] = {}


def am_pm_key(hour: int) -> str:
    return "am" if hour < 12 else "pm"


def alert_key(scroll: dict) -> tuple[str, str]:
    h, _ = scroll["time"]
    return (scroll["name"], am_pm_key(h))

# ─── SPAWN CHECKER ────────────────────────────────────────────────────────────

@tasks.loop(seconds=15)
async def spawn_checker() -> None:
    channel = bot.get_channel(ALERT_CHANNEL_ID)
    if channel is None:
        log.warning("Channel %d not found.", ALERT_CHANNEL_ID)
        return

    now_pst = datetime.now(PST)
    fired: list[dict] = []

    for scroll in SCROLLS:
        h, m = scroll["time"]
        # Check both AM and PM windows
        for spawn_h in [h, (h + 12) % 24]:
            key = (scroll["name"], am_pm_key(spawn_h))
            # Within 15-second fire window
            spawn_time = now_pst.replace(hour=spawn_h, minute=m, second=0, microsecond=0)
            delta = abs((now_pst - spawn_time).total_seconds())
            if delta <= 15 and not _alerted.get(key):
                _alerted[key] = True
                fired.append({**scroll, "_spawn_dt": spawn_time})
                log.info("SPAWNED: %s @ %s (%s)", scroll["name"], scroll["location"], format_pst(spawn_time))
            elif delta > 60:
                # Reset alert flag once the window has safely passed
                _alerted.pop(key, None)

    if not fired:
        return

    now_str = format_pst(datetime.now(PST))

    if len(fired) == 1:
        s = fired[0]
        color = 0xFF4500 if s["type"] == "ability" else 0x1E90FF
        icon  = "🔴" if s["type"] == "ability" else "🔵"
        embed = discord.Embed(
            title=f"{icon}  SCROLL SPAWNED  {icon}",
            color=color,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📜 Scroll",   value=f"**{s['name']}**",         inline=True)
        embed.add_field(name="🏷️ Type",    value=s["type"].capitalize(),      inline=True)
        embed.add_field(name="📍 Location", value=s["location"],               inline=True)
        embed.add_field(name="🕐 Time",     value=now_str,                     inline=False)
        embed.set_footer(text="Shindo Life Scroll Tracker • Despawns in ~25 min")
        await channel.send("@everyone", embed=embed)
    else:
        embed = discord.Embed(
            title=f"🌟  {len(fired)} SCROLLS SPAWNED AT ONCE  🌟",
            color=0xFFD700,
            timestamp=datetime.utcnow()
        )
        for s in fired:
            icon = "🔴" if s["type"] == "ability" else "🔵"
            embed.add_field(
                name=f"{icon} {s['name']}",
                value=f"**Type:** {s['type'].capitalize()}\n**Map:** {s['location']}",
                inline=True
            )
        embed.add_field(name="🕐 Time", value=now_str, inline=False)
        embed.set_footer(text="Shindo Life Scroll Tracker • Despawns in ~25 min")
        await channel.send("@everyone", embed=embed)


@spawn_checker.before_loop
async def before_checker():
    await bot.wait_until_ready()

# ─── COMMANDS ─────────────────────────────────────────────────────────────────

def sorted_by_next(scroll_type: str) -> list[tuple[dict, float]]:
    results = []
    for s in SCROLLS:
        if s["type"] != scroll_type:
            continue
        h, m = s["time"]
        secs = seconds_until(h, m)
        results.append((s, secs))
    results.sort(key=lambda x: x[1])
    return results


@bot.command(name="next")
async def cmd_next(ctx: commands.Context, scroll_type: str = "") -> None:
    scroll_type = scroll_type.lower().strip()
    if scroll_type not in ("ability", "weapon"):
        embed = discord.Embed(
            title="❌ Invalid Usage",
            description="Use `!next ability` or `!next weapon`",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return

    pairs = sorted_by_next(scroll_type)
    if not pairs:
        await ctx.send("No scrolls found.")
        return

    # Group all scrolls that spawn within 30 seconds of the soonest
    soonest_secs = pairs[0][1]
    simultaneous = [(s, secs) for s, secs in pairs if abs(secs - soonest_secs) <= 30]
    upcoming     = [(s, secs) for s, secs in pairs if (s, secs) not in simultaneous][:5]

    color = 0xFF4500 if scroll_type == "ability" else 0x1E90FF
    icon  = "🔴" if scroll_type == "ability" else "🔵"

    embed = discord.Embed(
        title=f"{icon} Next {scroll_type.capitalize()} Scroll{'s' if len(simultaneous) > 1 else ''}",
        color=color,
        timestamp=datetime.utcnow()
    )

    if len(simultaneous) == 1:
        s, secs = simultaneous[0]
        h, m = s["time"]
        spawn_dt = next_spawn_dt(h, m)
        embed.add_field(name="📜 Scroll",    value=f"**{s['name']}**",          inline=True)
        embed.add_field(name="📍 Map",       value=s["location"],                inline=True)
        embed.add_field(name="⏱️ In",        value=format_countdown(secs),       inline=True)
        embed.add_field(name="🕐 Spawns At", value=format_pst(spawn_dt),         inline=False)
    else:
        embed.description = f"**{len(simultaneous)} scrolls spawn at the same time!**"
        for s, secs in simultaneous:
            h, m = s["time"]
            spawn_dt = next_spawn_dt(h, m)
            embed.add_field(
                name=f"📜 {s['name']}",
                value=f"📍 {s['location']}\n⏱️ {format_countdown(secs)}\n🕐 {format_pst(spawn_dt)}",
                inline=True
            )

    if upcoming:
        lines = []
        for s, secs in upcoming:
            lines.append(f"• **{s['name']}** — {s['location']} — {format_countdown(secs)}")
        embed.add_field(name="📅 Up Next", value="\n".join(lines), inline=False)

    embed.set_footer(text="Times in PST • Each scroll spawns AM + PM")
    await ctx.send(embed=embed)


@bot.command(name="schedule")
async def cmd_schedule(ctx: commands.Context, scroll_type: str = "all") -> None:
    scroll_type = scroll_type.lower().strip()
    if scroll_type not in ("ability", "weapon", "all"):
        scroll_type = "all"

    pool = SCROLLS if scroll_type == "all" else [s for s in SCROLLS if s["type"] == scroll_type]
    pairs = sorted(
        [(s, seconds_until(*s["time"])) for s in pool],
        key=lambda x: x[1]
    )[:15]

    color = 0xFFD700
    embed = discord.Embed(
        title=f"📅 Upcoming Spawns — {scroll_type.capitalize()}",
        color=color,
        timestamp=datetime.utcnow()
    )
    lines = []
    for s, secs in pairs:
        icon = "🔴" if s["type"] == "ability" else "🔵"
        lines.append(f"{icon} **{s['name']}** — {s['location']} — {format_countdown(secs)}")
    embed.description = "\n".join(lines)
    embed.set_footer(text="Times in PST • !next ability | !next weapon")
    await ctx.send(embed=embed)


@bot.command(name="find")
async def cmd_find(ctx: commands.Context, *, name: str = "") -> None:
    if not name:
        await ctx.send("Usage: `!find Air Style Fan`")
        return
    match = next((s for s in SCROLLS if s["name"].lower() == name.lower()), None)
    if match is None:
        # Fuzzy partial match
        matches = [s for s in SCROLLS if name.lower() in s["name"].lower()]
        if not matches:
            await ctx.send(f"❌ No scroll found matching **{name}**.")
            return
        if len(matches) > 1:
            names = "\n".join(f"• {s['name']}" for s in matches[:10])
            await ctx.send(f"Multiple matches — be more specific:\n{names}")
            return
        match = matches[0]

    h, m = match["time"]
    secs = seconds_until(h, m)
    spawn_dt = next_spawn_dt(h, m)
    color = 0xFF4500 if match["type"] == "ability" else 0x1E90FF
    icon  = "🔴" if match["type"] == "ability" else "🔵"

    embed = discord.Embed(title=f"{icon} {match['name']}", color=color, timestamp=datetime.utcnow())
    embed.add_field(name="🏷️ Type",       value=match["type"].capitalize(),           inline=True)
    embed.add_field(name="📍 Map",        value=match["location"],                     inline=True)
    embed.add_field(name="🕐 Spawn Time", value=f"{h:02d}:{m:02d} & {(h+12)%24:02d}:{m:02d} PST", inline=True)
    embed.add_field(name="⏱️ Time Until", value=format_countdown(secs),                inline=True)
    embed.add_field(name="🗓️ Next Spawn", value=format_pst(spawn_dt),                  inline=True)
    embed.set_footer(text="Shindo Life Scroll Tracker")
    await ctx.send(embed=embed)


@bot.command(name="help")
async def cmd_help(ctx: commands.Context) -> None:
    embed = discord.Embed(
        title="🌀 Shindo Scroll Bot",
        color=0x9B59B6,
        description="Tracks all Sub Ability and Ninja Tool scroll spawns. Pings @everyone on spawn."
    )
    embed.add_field(name="!next ability",         value="Next sub ability scroll(s). Lists all if simultaneous.", inline=False)
    embed.add_field(name="!next weapon",          value="Next ninja tool/weapon scroll(s). Same multi-spawn handling.", inline=False)
    embed.add_field(name="!schedule [type]",      value="`ability`, `weapon`, or `all`. Shows next 15 spawns by time.", inline=False)
    embed.add_field(name="!find <scroll name>",   value="Lookup any scroll by name. Partial match supported.", inline=False)
    embed.set_footer(text="All times PST • Scrolls spawn AM + PM • Despawn ~25 min")
    await ctx.send(embed=embed)

# ─── EVENTS ───────────────────────────────────────────────────────────────────

@bot.event
async def on_ready() -> None:
    log.info("Online as %s (%s)", bot.user, bot.user.id)
    spawn_checker.start()
    log.info("Spawn checker running. %d scrolls tracked.", len(SCROLLS))


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    log.error("Error in %s: %s", ctx.command, error)

# ─── ENTRY ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(BOT_TOKEN)