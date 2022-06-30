import discord
import datetime
import asyncio
import random
import youtubeApiRequests
import json
import datetime
import os

from discord.ext import tasks, commands

from secret import discordKey as api_key

class MyBot(commands.Bot):# class MyClient(discord.Client):
    def __init__(self, prefix="!"):
        commands.Bot.__init__(self, command_prefix=prefix)
        self.command_prefix = prefix
        self.id = random.randint(0,100)
        self.counter = None

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        print(self.guilds)

    async def on_message(self, message):
        print('Processing Message from {0.author}: {0.content}'.format(message))
        await self.process_commands(message)
        if message.content:
            if message.content.startswith("!"):
                await message.delete()

class YoutubeCommands(commands.Cog):
    def __init__(self, bot, settings=None):
        self.bot = bot
        self.myWatchlist = []
        self.last_time_checked = None
        # self.loadSettings(settings)
        if settings is not None:
            self.myWatchlist = settings['watchlist']
            self.last_time_checked = settings['last_checked']
        # self.command_prefix = "!" #  TODO: Check wheter i need this line
    
    @commands.command()
    async def register(self, ctx, message=None):
        """
        store in watchlist and add to settingsfile
        add a tuple (uploadList, channelId)
        """
        # TODO: prevent duplicates
        if message is not None:
            # print("watching {}".format(message))
            upload_id, channel_id, channel_name= watchTuple = youtubeApiRequests.getChannelAndUploadId(message, youtubeApiRequests.api_key)
            print("Found the id")
            self.myWatchlist.append(watchTuple)
            settings = {'last_checked': str(self.last_time_checked.isoformat()), 'watchlist': self.myWatchlist}
            saveYoutubeSettings(settings)
            await ctx.send("Added to the Watchlist, {}".format(channel_name))
            # try:
            #     upload_id, channel_id, channel_name= watchTuple = youtubeApiRequests.getChannelAndUploadId(message, youtubeApiRequests.api_key)
            #     print("Found the id")
            #     self.myWatchlist.append(watchTuple)
            #     self.saveSettings()
            # except :
            #     await ctx.send("Failed adding to the watchlist")
            # else:
            #     await ctx.send("Added to the Watchlist, {}".format(channel_name))
            # upload_id, channel_id, channel_name = youtubeApiRequests.getChannelAndUploadId(message, youtubeApiRequests.api_key)
    
    @commands.command()
    async def unregister(self, ctx, *message):
        """
        remove from watchlist and settings file
        """
        # TODO: make this function work
        if message is not None:
            print("removing {}".format(message))
            self.myWatchlist = list(filter(lambda x: x != message,self.myWatchlist))
        settings = {'last_checked': str(self.last_time_checked.isoformat()), 'watchlist': self.myWatchlist}
        saveYoutubeSettings(settings)
    
    @commands.command()
    async def new(self, ctx, message=None):
        """
        returns all new videos, of the channels from the watchlist
        save current time to the settings and update current settings
        """
        newVideos = youtubeApiRequests.newVideos(self.myWatchlist, self.last_time_checked, youtubeApiRequests.api_key)
        new_check_time = datetime.datetime.now(tz=datetime.timezone.utc)
        if len(newVideos)==0:
            await ctx.send("No new videos available since {}".format(self.last_time_checked))
        else:
            outputString="New Videos: \n"
            outputStrings = []
            # await ctx.send("New videos since {}".format(self.last_time_checked))
            for videoList in newVideos:
                # outputString = outputString + "channel {}\n".format(videoList[0])
                channelString = "channel {}\n".format(videoList[0])
                for video in videoList[1]:
                    channelString = channelString + "\t{}\n".format(video)
                    # if len(outputString) + len("\t{}\n".format(video)) < 1500:
                    #     outputString = outputString + "\t{}\n".format(video)
                    # else:
                    #     outputStrings.append(outputString)
                    #     outputString = "\t{}\n".format(video)
                if len(outputString) + len(channelString) > 1750:
                    outputStrings.append(outputString)
                    outputString = channelString
                else:
                    outputString = outputString + channelString
            outputStrings.append(outputString)
            for s in outputStrings:
                await ctx.send(s)

        self.last_time_checked = new_check_time
        settings = {'last_checked': str(self.last_time_checked.isoformat(timespec='seconds')), 'watchlist': self.myWatchlist}
        saveYoutubeSettings(settings)
    
    @commands.command()
    async def watchlist(self, ctx, message=None):
        displayedList = [channel_name for _,_, channel_name in self.myWatchlist]
        await ctx.send("The watchlist is {}.".format(displayedList))
    
    @commands.command()
    async def resetTime(self, ctx, message=None):
        self.last_time_checked = datetime.datetime.min
        settings = {'last_checked': str(self.last_time_checked.isoformat(timespec='seconds')), 'watchlist': self.myWatchlist}
        saveYoutubeSettings(settings)




def loadYoutubeSettings():
    # load last_checked and watchlist from settings file
    if os.path.isfile("settings.json"):
        with open("settings.json") as outFile:
            settings = json.load(outFile)
            print("Settings loaded : {}".format(settings))
            if 'last_checked' in settings:
                settings["last_checked"] = datetime.datetime.fromisoformat(settings["last_checked"])
        return settings
    else:
        return {'last_checked': datetime.datetime.min, 'watchlist': []}

def saveYoutubeSettings(settings):
    with open("settings.json", "w") as outFile:
        json.dump(settings, outFile)

if __name__ == "__main__":
    # zero = datetime.datetime.min
    # print(zero)

    settings = loadYoutubeSettings()
    bot  = MyBot()
    bot.add_cog(YoutubeCommands(bot, settings))
    bot.run(api_key)
