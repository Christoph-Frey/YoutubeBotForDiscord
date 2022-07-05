import discord
import datetime
import asyncio
import random
import youtubeApiRequests
import json
import datetime
import os
from db.db_access import myDatabase as DB

from discord.ext import tasks, commands

from secret import discordKey as api_key

class MyBot(commands.Bot):# class MyClient(discord.Client):
    def __init__(self, database, prefix="!"):
        commands.Bot.__init__(self, command_prefix=prefix)
        self.command_prefix = prefix
        self.id = random.randint(0,100)
        self.counter = None
        self.db = database

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        print(self.guilds)

    async def on_message(self, message):
        if not message.author.bot:
            print('Processing Message from {0.author}: {0.content}'.format(message))
            await self.process_commands(message)
        if message.content:
            if message.content.startswith("!"):
                await message.delete()

class YoutubeCommands(commands.Cog):
    def __init__(self, bot, settings=None):
        self.bot = bot
        self.myWatchlist = None
        # self.loadSettings(settings)
        self.lazyWatchlist = None
        self.getLazyWatchlist()

        self.last_time_checked = self.bot.db.getOptionFromDB('last_checked')
        if self.last_time_checked is None:
            self.last_time_checked = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
            self.bot.db.addOptionToDB('last_checked', self.last_time_checked)
    
    def getLazyWatchlist(self):
        if self.lazyWatchlist is None:
            print("updating Watchlist")
            self.lazyWatchlist = self.bot.db.getWatchlist()
        return self.lazyWatchlist
    
    def updateLazyWatchlist(self, newChannel):
        # format it (upload_id, channel_id, channel_name, last_checked)
        # update the lazy list
        self.lazyWatchlist.append(newChannel)
    
    @commands.command()
    async def register(self, ctx, message=None):
        """
        store in watchlist and add to settingsfile
        add a tuple (uploadList, channelId)
        """
        # TODO: prevent duplicates -> use the db
        if message is not None:
            # print("watching {}".format(message))
            upload_id, channel_id, channel_name= watchTuple = youtubeApiRequests.getChannelAndUploadId(message, youtubeApiRequests.api_key)
            print("Found the id")
            channel = (channel_name, channel_id, upload_id, datetime.datetime.min)
            self.bot.db.addChannelToDB(channel)
            self.updateLazyWatchlist((channel[2], channel[1], channel[0], channel[3]))
            await ctx.send("Added to the Watchlist, {}".format(channel_name))
            return
            ########## old code below
            # self.myWatchlist.append(watchTuple)
            # settings = {'last_checked': str(self.last_time_checked.isoformat()), 'watchlist': self.myWatchlist}
            # saveYoutubeSettings(settings)
            # await ctx.send("Added to the Watchlist, {}".format(channel_name))
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
        # print(" ".join(message))
        identifier = " ".join(message)
        if identifier != "":
            self.bot.db.removeChannelFromDB(identifier)
            print("removed all channels matching {}".format(identifier))
        
        # #================================================= old code below
        # index, content = findNameInList(name, self.myWatchlist)
        # print("removing {} : {}".format(name, content))
        # if index is not None:
        #     removed = self.myWatchlist.pop(index)
        #     settings = {'last_checked': str(self.last_time_checked.isoformat()), 'watchlist': self.myWatchlist}
        #     saveYoutubeSettings(settings)
        
        # return
        # findNameInList(name, contentList)
        # # TODO: make this function work
        # if message is not None:
        #     print("removing {}".format(message))
        #     self.myWatchlist = list(filter(lambda x: x != message,self.myWatchlist))
        # settings = {'last_checked': str(self.last_time_checked.isoformat()), 'watchlist': self.myWatchlist}
        # saveYoutubeSettings(settings)
    
    @commands.command()
    async def new(self, ctx, message=None):
        """
        returns all new videos, of the channels from the watchlist
        save current time to the settings and update current settings
        """
        # get watchlist from db and get the last_time_checked
        # watchlist = self.bot.db.getWatchlist()
        watchlist = self.getLazyWatchlist()
        last_time_checked = self.last_time_checked

        # the watchlist from the db has the format (name, channel_id, upload_id, last_checked)

        watchlist = [(item[2], item[1], item[0], item[3]) for item in watchlist]

        # the api wrapper needs (upload_id, channel_id, channel_name, last_checked)

        # use watchlist and last time checked to get new videos
        newVideos = youtubeApiRequests.newVideos(watchlist, last_time_checked, youtubeApiRequests.api_key)
        print("finished loading new videos")
        new_check_time = datetime.datetime.now(tz=datetime.timezone.utc)

        # add new videos the the videos database as (name text, video_id text, channel_id text, uploadTime text, url text) -> make sure those are available
        # print(newVideos)

        for channel in newVideos:
            for video in channel[1]:
                # print(video)
                self.bot.db.addVideoToDB(video)
        print("stored new videos")

        # update the check time of the channels

        newTime = datetime.datetime.min

        self.bot.db.updateLastCheckedTimeDB(newTime)


        # create a list to output channel and names
        newVideos = [(key, [video[0] for video in channel]) for key,channel in newVideos]

        # sends a message to the discord server wheter new messages are available
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
        self.bot.db.addOptionToDB('last_checked', self.last_time_checked)
        # settings = {'last_checked': str(self.last_time_checked.isoformat(timespec='seconds')), 'watchlist': self.myWatchlist}
        # saveYoutubeSettings(settings)
        return

        # #################### old code below ###################
        # newVideos = youtubeApiRequests.newVideos(self.myWatchlist, self.last_time_checked, youtubeApiRequests.api_key)
        # new_check_time = datetime.datetime.now(tz=datetime.timezone.utc)
        # if len(newVideos)==0:
        #     await ctx.send("No new videos available since {}".format(self.last_time_checked))
        # else:
        #     outputString="New Videos: \n"
        #     outputStrings = []
        #     # await ctx.send("New videos since {}".format(self.last_time_checked))
        #     for videoList in newVideos:
        #         # outputString = outputString + "channel {}\n".format(videoList[0])
        #         channelString = "channel {}\n".format(videoList[0])
        #         for video in videoList[1]:
        #             channelString = channelString + "\t{}\n".format(video)
        #             # if len(outputString) + len("\t{}\n".format(video)) < 1500:
        #             #     outputString = outputString + "\t{}\n".format(video)
        #             # else:
        #             #     outputStrings.append(outputString)
        #             #     outputString = "\t{}\n".format(video)
        #         if len(outputString) + len(channelString) > 1750:
        #             outputStrings.append(outputString)
        #             outputString = channelString
        #         else:
        #             outputString = outputString + channelString
        #     outputStrings.append(outputString)
        #     for s in outputStrings:
        #         await ctx.send(s)

        # self.last_time_checked = new_check_time
        # settings = {'last_checked': str(self.last_time_checked.isoformat(timespec='seconds')), 'watchlist': self.myWatchlist}
        # saveYoutubeSettings(settings)
    
    @commands.command()
    async def watchlist(self, ctx, message=None):
        # displayedList = [channel_name for _,_, channel_name in self.myWatchlist]
        # watchlist = self.bot.db.getWatchlist()
        watchlist = self.getLazyWatchlist()
        await ctx.send("The watchlist is {}.".format(watchlist))
    
    @commands.command()
    async def resetTime(self, ctx, message=None):
        self.last_time_checked = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        print("Reset the time to {}".format(self.last_time_checked.isoformat(timespec='seconds')))
        self.bot.db.addOptionToDB('last_checked', self.last_time_checked)
        # settings = {'last_checked': str(self.last_time_checked.isoformat(timespec='seconds')), 'watchlist': self.myWatchlist}
        # saveYoutubeSettings(settings)

        self.bot.db.addOptionToDB('last_checked', self.last_time_checked)
    
    @commands.command()
    async def saveAllUploads(self, ctx, message=None):
        pass
    
    @commands.command()
    async def getUploads(self, ctx, *message):
        identifier = " ".join(message)

        await ctx.send("Getting updated is not yet implemented.".format(watchlist))
    
    @commands.command()
    async def listCommands(self, ctx, *message):
        identifier = " ".join(message)

        await ctx.send("Help is not yet implemented.".format(watchlist)) 
    
    @commands.command()
    async def shutdown(self, ctx, *message):
        self.bot.close()




def loadYoutubeSettings():
    # load last_checked and watchlist from settings file
    if os.path.isfile("settings.json"):
        with open("settings.json") as outFile:
            settings = json.load(outFile)
            # print("Settings loaded : {}".format(settings))
            if 'last_checked' in settings:
                settings["last_checked"] = datetime.datetime.fromisoformat(settings["last_checked"]).replace(tzinfo=datetime.timezone.utc)
            print(settings)
        return settings
    else:
        return {'last_checked': datetime.datetime.min, 'watchlist': []}

def saveYoutubeSettings(settings):
    with open("settings.json", "w") as outFile:
        json.dump(settings, outFile)

def saveToFile(content, fileName):
    with open(fileName, "w") as file:
        file.write(content)

def findNameInList(name, contentList):
    """
    finda the element in list that contains Name

    returns:
    index and first element that contains the name
    """
    assert(type(contentList)==list)
    for index in range(len(contentList)):
        if type(contentList[index]) is list or type(contentList[index]) is tuple:
            for item in contentList[index]:
                # match item to 
                if matchNameAndItem(name, item):
                    return index, contentList[index]
        if type(contentList[index]) is dict:
            for key in contentList[index]:
                # match item to 
                if matchNameAndItem(name, contentList[index][key]):
                    return index, contentList[index][key]
        if type(contentList[index]) is str:
            if matchNameAndItem(name, contentList[index]):
                return index, contentList[index]
    
    return None, None

def matchNameAndItem(name, item):
    if name == item:
        return True
    else:
        return False

def writeWatchlistToDB(db, settings):
    """
    only supposed to use for initial filling of db from the settings
    """

    new_list = [(item[0], item[1], item[2], datetime.datetime.min) for item in settings['watchlist']]
    # print(new_list)
    db.writeChannelsToDB(new_list)
    pass

async def runBot(bot):
    bot.start()

def main():
    # get the database
    db = DB('db/base.db')
    db.open()

    # set up the bot
    # settings = loadYoutubeSettings()
    # writeWatchlistToDB(db, settings)

    bot  = MyBot(database=db)
    bot.add_cog(YoutubeCommands(bot))
    bot.run(api_key)
    # bot.start()
    # await runBot(bot)

    # await bot.start()
    db.close()

        # try:
        #     loop.run_until_complete(start(*args, **kwargs))
        # except KeyboardInterrupt:
        #     loop.run_until_complete(close())
        #     # cancel all tasks lingering
        # finally:
        #     loop.close()

if __name__ == "__main__":
    # zero = datetime.datetime.min
    # print(zero)
    main()
