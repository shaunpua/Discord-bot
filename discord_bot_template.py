#project bot 
#imported youtube_dl for playing audio from youtube
import discord
from discord.ext import commands
from discord.ext.commands import bot
import asyncio
from itertools import cycle
import time
import youtube_dl
import praw
import random

my_token = 'insert discord token here'

client = commands.Bot(command_prefix = '!')
#used to remove the default help command so we can create our own later into the code
client.remove_command('help')
status = ['!help for commands', 'Honkai Impact 3', "\'Faded\', by Allan Walker"]

players = {}
queues = {}

def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()

#cycles the bot status from the status list
async def change_status():
    await client.wait_until_ready()
    msgs = cycle(status)

    while not client.is_closed:
        current_status = next(msgs)
        await client.change_presence(game=discord.Game(name =current_status))
        await asyncio.sleep(60)

reddit = praw.Reddit(client_id= 'w-huDRWsfeDZQw',
                     client_secret= 'J61x_1WKUuU2Ga-J8tb5dW9TdbA',
                     user_agent= 'bot kencho by /u/	yonhyakuniju_doge')


@client.event
async def on_ready():
    print('The bot is online and is connected to discord')

#automatically sets a role upon entering a server
@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name='Newcomer')
    await client.add_roles(member, role)


@client.event
async def on_message(message):
    #checks if the msg is a command which allows it not tobe overwritten by prioritzed on_messgae commands
    await client.process_commands(message)
    if message.content.startswith('!kentai'):
        userID = message.author.id
        await client.send_message(message.channel, '<@%s> sup' % (userID))

@client.command(pass_context =True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(Colour = discord.Colour.blue())
    embed.set_author(name = 'Help Commands')
    embed.add_field(name ='!say', value ='Returns what the user says.', inline=False)
    embed.add_field(name ='!clear', value ='Deletes certain amount of messages, default amount is 10', inline=False)
    embed.add_field(name ='!serverinfo', value ='Gives the server information on the selected user', inline=False)
    embed.add_field(name ='!join', value ='The bot joins the current voice channel and displays voice channel commands, the user must be in a voice channel to use this comand', inline=False)
    embed.add_field(name ='!leave', value ='The bot leaves the current voice channel.', inline=False)
    embed.add_field(name ='!play', value ='Plays the audio from a youtube url', inline=False)
    embed.add_field(name ='!kentai', value ='Kincho says sup XD', inline=False)
    embed.add_field(name ='!reddithelp', value ='show commands on certain subreddits', inline=False)

    await client.send_message(author, embed=embed)

#command used to delete messages in discord chat
@client.command(pass_context = True)
async def clear(ctx, amount = 10):
    channel = ctx.message.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount) +1):
        messages.append(message)
    await client.delete_messages(messages)
    await client.say(str(amount) + ' messages were deleted')

#command for bot to join voice channel
@client.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    embed = discord.Embed(
        title = 'Voice channel',
        description = 'commands for the voice channel.',
        colour = discord.Colour.blue()
    )

    embed.add_field(name = '!play', value = 'Play youtube audio with url', inline = False)
    embed.add_field(name = '!queue', value = 'Adds another youtube audio url in the queue ', inline = False)
    embed.add_field(name = '!pause', value = 'pauses audio', inline = False)
    embed.add_field(name = '!resume', value = 'resumes audio', inline = False)
    embed.add_field(name = '!leave', value = 'leave voice channel', inline = False)

    await client.say(embed=embed)
    await client.join_voice_channel(channel)

#command for bot to leave voice channel and discorp.py is requried for thos to work
@client.command(pass_context = True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

#install youtube_dl and ffmpeg to play video using irl
@client.command(pass_context = True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    players[server.id] = player
    player.start()


@client.command(pass_context = True)
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url)

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    await client.say('The video is queued.')


@client.command(pass_context = True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()

@client.command(pass_context = True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

@client.command(pass_context = True)
async def stop(ctx):
    id = ctx.message.server.id
    players[id].stop()


# say  is the command which uses the prefix "!"" when typed in discord chat
@client.command()
async def say(*args):
        output = ''
        for word in args:
            output += word
            output += ' '
        await client.say(output)

#embed format the output in an enclosed area
@client.command(pass_context=True)
async def serverinfo(ctx, user: discord.Member):
    embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0x00ff00)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True)
    embed.add_field(name="Highest role", value=user.top_role)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.set_thumbnail(url=user.avatar_url)
    await client.say(embed=embed)

@client.command(pass_context =True)
async def reddithelp(ctx):
    author = ctx.message.author
    embed = discord.Embed(Colour = discord.Colour.orange())
    embed.set_author(name = 'Subreddit commands')
    embed.add_field(name ='!dankmeme', value ='Sends dankmemes.', inline=False)
    embed.add_field(name ='!wot', value ='Sends world of tanks related posts.', inline=False)
    embed.add_field(name ='!anime', value ='Sends anime related posts.', inline=False)
    embed.add_field(name ='!dota2', value ='Sends dota2 related posts..', inline=False)
    embed.add_field(name ='!worldnews', value ='Sends international news.', inline=False)
    embed.add_field(name ='!news', value ='Sends international news.', inline=False)
    

    await client.send_message(author, embed=embed)

#uses praw to acces reddit api dev options 

@client.command(pass_context=True)
async def dankmeme():
    dankmemes_submissions = reddit.subreddit('dankmemes').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in dankmemes_submissions if not x.stickied)

    await client.say(submission.url)

async def bossfight():
    bossfight_submissions = reddit.subreddit('Bossfight').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in bossfight_submissions if not x.stickied)

    await client.say(submission.url)

async def iamverysmart():
    iamverysmart_submissions = reddit.subreddit('iamverysmart').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in iamverysmart_submissions if not x.stickied)

    await client.say(submission.url)

async def dankmeme():
    dankmemes_submissions = reddit.subreddit('dankmemes').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in dankmemes_submissions if not x.stickied)

    await client.say(submission.url)




@client.command(pass_context=True)
async def anime():
    anime_submissions = reddit.subreddit('anime').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in anime_submissions if not x.stickied)

    await client.say(submission.url)

@client.command(pass_context=True)
async def wot():
    WorldofTanks_submissions = reddit.subreddit('WorldofTanks').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in WorldofTanks_submissions if not x.stickied)

    await client.say(submission.url)

@client.command(pass_context=True)
async def dota2():
    DotA2_submissions = reddit.subreddit('DotA2').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in DotA2_submissions if not x.stickied)

    await client.say(submission.url)

@client.command(pass_context=True)
async def science():
    science_submissions = reddit.subreddit('science').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in science_submissions if not x.stickied)

    await client.say(submission.url)

@client.command(pass_context=True)
async def worldnews():
    worldnews_submissions = reddit.subreddit('worldnews').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in worldnews_submissions if not x.stickied)

    await client.say(submission.url)

@client.command(pass_context=True)
async def news():
    news_submissions = reddit.subreddit('news').hot()
    post_to_pick = random.randint(1, 20)
    for i in range(0, post_to_pick):
        submission = next(x for x in news_submissions if not x.stickied)

    await client.say(submission.url)



client.loop.create_task(change_status())
client.run(my_token)

#using version 0.16.12 BELOW IS THE DOCUMENTATION
# https://discordpy.readthedocs.io/en/latest/api.html#utility-functions for documentation
#https://discordpy.readthedocs.io/en/latest/
# praw documentation https://praw.readthedocs.io/en/latest/getting_started/quick_start.html