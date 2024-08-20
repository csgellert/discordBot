import discord
from discord.ext import commands
from datetime import timedelta
import asyncio
with open('token.txt', 'r') as f:
    BOT_TOKEN = f.readline()
print(BOT_TOKEN)
# Replace these with your actual IDs and token
SOURCE_CHANNEL_ID = 1274758710387806222  # ID of the source channel
TARGET_CHANNEL_ID = 1274758763194351752  # ID of the target channel
#BOT_TOKEN = 'your_bot_token_here'  # Your bot token

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enables message content intent

# Set up bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(help="Copies messages from the source channel to the target channel (The chanels shall be preset in the code)")
async def copymessages(ctx):

    COPY_BOT_MESSEGAES = False
    print("Starting copying messages...")
    # Check if the command was issued in the correct channel
    if ctx.channel.id == SOURCE_CHANNEL_ID:
        source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        
        if source_channel and target_channel:
            messages = []
            
            # Fetch messages from the source channel
            async for message in source_channel.history(limit=None,oldest_first=True):
                # Avoid reposting messages sent by the bot itself
                if message.author != bot.user or COPY_BOT_MESSEGAES:
                    messages.append(message)

            # Send messages to the target channel in the correct order
            previous_message = None
            for message in messages:
                try:
                    files = []
                    for attachment in message.attachments:
                        # Download the attachment
                        file = await attachment.to_file()
                        files.append(file)
                    if previous_message is not None and previous_message.author == message.author and timedelta(seconds=5)>message.created_at - previous_message.created_at:
                        new_message = await target_channel.send(f'    {message.content}',files=files)
                    else:
                        new_message = await target_channel.send(f'**{message.author.display_name}** [*{message.created_at.strftime("%Y-%m-%d")}*]: {message.content}',files=files)
                    if message.thread:
                    # Create a corresponding thread in the target channel
                        new_thread = await new_message.create_thread(name=message.thread.name)

                        # Fetch all messages from the original thread
                        async for thread_message in message.thread.history(limit=None):
                            thread_content = f'{thread_message.author.display_name}: {thread_message.content}'
                            
                            # Prepare files for uploading
                            thread_files = []
                            for attachment in thread_message.attachments:
                                file = await attachment.to_file()
                                thread_files.append(file)

                            # Send the thread message to the new thread
                            await new_thread.send(thread_content, files=thread_files)
                except:
                    await target_channel.send(f'WARNING: Could not copy message...')
                previous_message = message
                await asyncio.sleep(1)
            print(f'Finished copying messages from {source_channel.name} to {target_channel.name}.')
            #await ctx.send(f'Finished copying messages from {source_channel.name} to {target_channel.name} in order.')
        else:
            await ctx.send("Could not find the source or target channel.")
            print("Could not find the source or target channel.")
    else:
        await ctx.send("This command can only be used in the source channel.")
        print("This command can only be used in the source channel.")


#! Test commands
@bot.command(help="For testing purposes only, it starts a counting on the given channel to generate messages for it")
async def counting(ctx):
    # Check if the command was issued in the correct channel
    #! This function is only for testing purposes, it generates messages for a channel 
    for i in range(120):
        await ctx.send(f'{i}')
@bot.command(help="Deletes all messeges from the target channel sent by the bot (target channel shall be preset in the code)")
async def deletebotmessages(ctx):
    print("Start deleting messages sent by the bot...")
    # Check if the command was issued in the target channel
    if ctx.channel.id == TARGET_CHANNEL_ID:
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        
        if target_channel:
            deleted_count = 0
            
            # Fetch all messages from the target channel
            async for message in target_channel.history(limit=None):
                # Check if the message was sent by the bot
                if message.author == bot.user:
                    await message.delete()
                    deleted_count += 1
                    
                    # Optionally, add a delay to avoid rate limits
                    await asyncio.sleep(0.1)  # Adjust the delay as needed
            
            await ctx.send(f'Deleted {deleted_count} messages sent by the bot from {target_channel.name}.')
            print(f'Deleted {deleted_count} messages sent by the bot from {target_channel.name}.')
        else:
            await ctx.send("Could not find the target channel.")
            print("Could not find the target channel.")
    else:
        await ctx.send("This command can only be used in the target channel.")
        print("This command can only be used in the target channel.")

# Run the bot
bot.run(BOT_TOKEN)
