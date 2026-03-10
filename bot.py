import discord
import requests

TOKEN = "MTQ4MTA3MTY3NjY2MDkxMjI5Mw.G4eis5.i5EZHWz2iGwKNdwnmbCwu8FUIJoMw19lMVDmr0"
API = "https://tsg-production.up.railway.app"
ADMIN = "SUPERSECRETADMINKEY"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print("Bot ready")

@bot.event
async def on_message(msg):

    if msg.author.bot:
        return

    if msg.content.startswith("!genkey"):

        days = msg.content.split()[1]

        r = requests.get(f"{API}/generate?admin={ADMIN}&days={days}")
        data = r.json()

        await msg.channel.send(f"Key:\n`{data['key']}`")

    if msg.content.startswith("!bulkkeys"):

        args = msg.content.split()

        amount = args[1]
        days = args[2]

        r = requests.get(f"{API}/generatebulk?admin={ADMIN}&amount={amount}&days={days}")
        data = r.json()

        keys = "\n".join(data["keys"])

        await msg.channel.send(f"```\n{keys}\n```")

bot.run(TOKEN)
