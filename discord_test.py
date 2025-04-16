import discord
from discord.ext import commands
import speedtest
import time

def sptest():
    st = speedtest.Speedtest()
    st.get_best_server()
    k = "current speed test: download speed:"+str(st.download/1_000_000)+"Mbps, upload speed: "+str(st.upload()/) 1_000_000)+"Mbps, ping: "+str(st.results.ping)
    return k
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Needed to fetch users by ID

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    user_id = 123456789012345678  # Replace with the actual user ID
    try:
        user = await bot.fetch_user(user_id)
        while True:
            await user.send(sptest())
            time.sleep(100)
        #await user.send("Hello! This is an automated message.")
        print(f"Sent message to {user.name}")
    except Exception as e:
        print(f"Could not send message: {e}")

bot.run("YOUR_BOT_TOKEN")

