import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
cys = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents)


async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Added {filename[:-3]}")

@bot.command()
async def shutdown(ctx):
    await ctx.send("Shutting down...")
    await ctx.bot.close()

@bot.event
async def on_ready():
    try:
        print(f"Bot active as {bot.user}")
        bot.tree.clear_commands(guild=discord.Object(id=1338965034616881263))
        await load_cogs()
        await bot.tree.sync(guild=discord.Object(id=1338965034616881263))
        print("Loaded all cogs")
        print("Registered commands:")
        for cmd in bot.tree.get_commands(guild=discord.Object(id=1338965034616881263)):
            print(f"- {cmd.name}")
    except Exception as e:
        print(f"❌ Error in on_ready: {e}")



bot.run("") #replace