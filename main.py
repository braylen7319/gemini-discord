import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Configure Discord bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if the bot was mentioned or replied to
    mentioned = bot.user in message.mentions
    replied = (
        message.reference and 
        isinstance(message.reference.resolved, discord.Message) and 
        message.reference.resolved.author == bot.user
    )

    if mentioned or replied:
        await message.channel.typing()
        try:
            cleaned = message.content.replace(f"<@{bot.user.id}>", "").strip()
            response = model.generate_content(cleaned)
            await message.reply(response.text)
        except Exception as e:
            await message.reply(f"Error: {e}")
    else:
        await bot.process_commands(message)

@bot.command()
async def ask(ctx, *, message):
    await ctx.trigger_typing()
    try:
        response = model.generate_content(message)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
