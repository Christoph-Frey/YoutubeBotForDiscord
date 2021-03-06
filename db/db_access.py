import sqlite3
import datetime

db_name = 'base.db'


def connectionToDB(db_name):
    return sqlite3.connect(db_name)


def resetTables(db_conn):
    cur = db_conn.cursor()
    out = cur.execute('''DROP TABLE channels''')
    out = cur.execute('''DROP TABLE videos''')
    cur.close()


def checkForTables(db_conn):
    cur = db_conn.cursor()
    out = cur.execute('''SELECT name FROM sqlite_master WHERE type='table';''')

    channels_flag = False
    videos_flag = False
    options_flag = False
    for table_name in out:
        if table_name == ("channels",):
            channels_flag = True
        if table_name == ("videos",):
            videos_flag = True
        if table_name == ("options",):
            options_flag = True

    if not channels_flag:
        createChannelTable(db_conn)

    if not videos_flag:
        createVideoTable(db_conn)

    if not options_flag:
        createOptionTable(db_conn)

    return


def clearVideoTable(db_conn):
    cur = db_conn.cursor()
    cur.execute('''DROP TABLE videos''')
    db_conn.commit()
    cur.close()


# CREATE TABLES
def createChannelTable(db_conn):
    cur = db_conn.cursor()
    cur.execute('''CREATE TABLE channels
                (name text, channel_id text, upload_id text, last_checked text)
    ''')
    db_conn.commit()
    cur.close()


def createVideoTable(db_conn, reset=False):
    cur = db_conn.cursor()
    if reset:
        cur.execute('''DROP TABLE videos
                ''')
    cur.execute('''CREATE TABLE videos
                (name text, video_id text, channel_id text, uploadTime text, url text)
    ''')
    db_conn.commit()
    cur.close()


def createOptionTable(db_conn, reset=False):
    cur = db_conn.cursor()
    if reset:
        cur.execute('''DROP TABLE options
                ''')
    cur.execute('''CREATE TABLE options
                (name text, value text)
    ''')
    db_conn.commit()
    cur.close()


############################# CHANNEL FUNCTIONS
def addChannel(db_conn, name, channel_id, upload_id, last_checked, unique=True):
    cur = db_conn.cursor()
    # print('''INSERT INTO channels
    #                     SELECT ('{name}', '{channel_id}', '{upload_id}', '{last_checked}')
    #                     WHERE NOT EXISTS (SELECT * FROM channels WHERE name = {name} and channel_id = {channel_id} and upload_id = {upload_id} )'''
    # ,(name=name, channel_id=channel_id, upload_id=upload_id, last_checked=last_checked))
    if unique:
        out = cur.execute('''INSERT INTO channels (name, channel_id, upload_id, last_checked)
                            SELECT :name, :channel_id, :upload_id, :last_checked
                            WHERE NOT EXISTS (SELECT * FROM channels WHERE channel_id= :channel_id or upload_id = :upload_id) ''',
                          {"name": name, "channel_id": channel_id, "upload_id": upload_id, "last_checked": last_checked}
                          )
    else:
        out = cur.execute('''INSERT INTO channels Values(:name, :channel_id, :upload_id, :last_checked)''',
                          {"name": name, "channel_id": channel_id, "upload_id": upload_id,
                           "last_checked": last_checked})

    db_conn.commit()
    cur.close()
    print("channel added")


def deleteChannelsExact(db_conn, name=None, channel_id=None, upload_id=None, DELETEALL=False):
    """
    deletes a channel that contains any of its attributes,
    or EVERYTHING IN THE TABLE IF DELETE ALL IS ACTIVE
    """
    values = []
    conditional = None
    if not (name is None and channel_id is None and upload_id is None):
        conditional = " WHERE"
    if name is not None:
        conditional = conditional + " name = ?"
        values.append(name)
    if channel_id is not None:
        if conditional != " WHERE":
            conditional = conditional + " AND"
        conditional = conditional + " channel_id = ?"
        values.append(channel_id)
    if upload_id is not None:
        if conditional != " WHERE":
            conditional = conditional + " AND"
        conditional = conditional + " upload_id = ?"
        values.append(upload_id)
    cur = db_conn.cursor()
    if conditional and not DELETEALL:
        # print('''DELETE from channels'''+conditional)
        out = cur.execute('''DELETE from channels''' + conditional, values)
    # [print(item) for item in out]

    if name is None and channel_id is None and upload_id is None and DELETEALL:
        out = cur.execute('''DELETE from channels''')
    cur.close()
    conn.commit()


def deleteChannels(db_conn, name=None, channel_id=None, upload_id=None):
    """
    deletes any channel that contains ANY of the given attributes
    """
    conditional = None
    values = []
    assert (not (name is None and channel_id is None and upload_id is None))
    conditional = " WHERE"
    if name is not None:
        conditional = conditional + " name = ?"
        values.append(name)
    if channel_id is not None:
        if conditional != " WHERE":
            conditional = conditional + " OR"
        conditional = conditional + " channel_id = ?"
        values.append(channel_id)
    if upload_id is not None:
        if conditional != " WHERE":
            conditional = conditional + " OR"
        conditional = conditional + " upload_id = ?"
        values.append(upload_id)
    cur = db_conn.cursor()
    if conditional:
        # print('''DELETE from channels'''+conditional)
        out = cur.execute('''DELETE from channels''' + conditional, values)
    # [print(item) for item in out]
    cur.close()
    db_conn.commit()


def findContent(db_conn, name=None, channel_id=None, upload_id=None):
    """
    deletes any channel that contains ANY of the given attributes
    """
    conditional = None
    values = []
    assert (not (name is None and channel_id is None and upload_id is None))
    conditional = " WHERE"
    if name is not None:
        conditional = conditional + " name LIKE ?"
        values.append("%" + name + "%")
    if channel_id is not None:
        if conditional != " WHERE":
            conditional = conditional + " OR"
        conditional = conditional + " channel_id LIKE ?"
        values.append("%" + channel_id + "%")
    if upload_id is not None:
        if conditional != " WHERE":
            conditional = conditional + " OR"
        conditional = conditional + " upload_id LIKE ?"
        values.append("%" + upload_id + "%")
    cur = db_conn.cursor()
    out = []
    if conditional:
        # print('''DELETE from channels'''+conditional)
        out = cur.execute('''Select * from channels''' + conditional, values)
    # [print(item) for item in out]

    results = list(out)
    cur.close()
    db_conn.commit()

    return results


def getChannels(db_conn):
    cur = db_conn.cursor()
    out = cur.execute('''Select name, channel_id, upload_id, last_checked from channels
                    ''')
    out = [item for item in out]
    # print(out)
    cur.close()
    db_conn.commit()
    return out


def updateChannelCheckTimes(db_conn, time):
    # print(time)
    # return
    cur = db_conn.cursor()
    cur.execute('''UPDATE channels
                    SET last_checked = ? ''', (str(time),))
    db_conn.commit()
    cur.close()


################### FUNCTIONS FOR OPTIONS TABLE
def insertOption(db_conn, key, value):
    # insert or update the option value
    cur = db_conn.cursor()
    # insert pair if it does not exist
    cur.execute('''
    INSERT INTO options (name, value)
    SELECT ?, ?
    WHERE NOT EXISTS( SELECT * FROM options WHERE name=? )
    ''', (key, value, key,))

    # try to update the option
    cur.execute('''
    UPDATE options
    SET value = ? 
    WHERE name= ?
    ''', (value, key,))  #

    db_conn.commit()
    cur.close()


def selectOptions(db_conn):
    cur = db_conn.cursor()
    options = cur.execute('''SELECT name, value FROM options
                ''')
    options = {key: value for key, value in options}
    db_conn.commit()
    cur.close()
    return options


def selectOption(db_conn, key):
    print(key)
    cur = db_conn.cursor()
    options = cur.execute('''SELECT name, value FROM options
                            where name = ?
                ''', (key,))
    options = {key: value for key, value in options}
    db_conn.commit()
    cur.close()

    if key in options:
        return options[key]
    else:
        return None


########## FUNCTIONS FOR VIDEOS TABLE
def addVideo(db_conn, name, video_id, channel_id, uploadTime, url):
    cur = db_conn.cursor()
    # escape all single quotes in the name
    name = name.replace("'", "''")

    # cur.execute('''INSERT INTO videos VALUES({name}, {video_id}, {channel_id}, {uploadTime}, {url})
    # ''', (name=name, video_id=video_id, channel_id=channel_id, uploadTime=uploadTime, url=url))
    # print('''INSERT INTO videos (name, video_id, channel_id, uploadTime, url)
    #                         SELECT '{name}', '{video_id}', '{channel_id}', '{uploadTime}', '{url}'
    #                         WHERE NOT EXISTS (SELECT * FROM videos WHERE video_id = '{video_id}') '''
    #     , (name=name, video_id=video_id, channel_id=channel_id, uploadTime=uploadTime, url=url))

    # out = cur.execute('''INSERT INTO videos Values('{name}', '{video_id}', '{channel_id}', '{uploadTime}', '{url}')'''
    #     , (name=name, video_id=video_id, channel_id=channel_id, uploadTime=uploadTime, url=url))

    out = cur.execute('''INSERT INTO videos (name, video_id, channel_id, uploadTime, url)
                            SELECT ?, ?, ?, ?, ?
                            WHERE NOT EXISTS (SELECT * FROM videos WHERE video_id = ?) ''',
                      (name, video_id, channel_id, uploadTime, url, video_id,))
    db_conn.commit()
    cur.close()


def nop(db_conn):
    cur = db_conn.cursor()
    cur.execute('''''')
    db_conn.commit()
    cur.close()


class myDatabase:
    def __init__(self, location):
        self.location = location
        self.opened = False
        self.db_connection = None

    def testAndSetup(self, conn):
        checkForTables(conn)

    def open(self):
        """
        connect to the table and make sure it is properly setup with
        the two tables "channels" and "videos"
        """
        if not self.opened:
            self.opened = True
            self.db_connection = connectionToDB(self.location)
            self.testAndSetup(self.db_connection)
            return self.db_connection

    def close(self):
        if self.opened:
            self.db_connection.close()
            self.opened = False

    def writeChannelsToDB(self, listOfChannels):
        """
        given list of tuples(or lists): (uploadlist_id,  channel_id, name, lastchecked)
        adds those that are not already in the db to the db
        """
        for channel in listOfChannels:
            addChannel(self.db_connection, channel[2], channel[1], channel[0], channel[3])

    def getWatchlist(self):
        """

        """
        if self.opened:
            watchlist = getChannels(self.db_connection)
            return watchlist

    def addChannelToDB(self, channel):
        """
        takes a channel in the form name, channel_id, upload_id, last_checked and puts it into the db
        """
        # addChannel(db_conn, name, channel_id, upload_id, last_checked, unique=True):
        if self.opened:
            name, channel_id, upload_id, last_checked = channel
            addChannel(self.db_connection, name, channel_id, upload_id, last_checked, unique=True)

    def removeChannelFromDB(self, identifier):
        """
        remove all channels that fit the identifier !!!! should be exactly one of name, channel_id, upload_id which are UNIQUE
        """
        if self.opened:
            deleteChannels(self.db_connection, name=identifier, channel_id=identifier, upload_id=identifier)

    def updateLastCheckedTimeDB(self, newTime):
        """
        updates all channels last_checked to newTime
        """
        updateChannelCheckTimes(self.db_connection, newTime)

    def addVideoToDB(self, video):
        """
        hands a video. ?->(of youtube api response (snippet part))
        saves it to a entry
        (name text, video_id text, channel_id text, uploadTime text, url text)

        video_id has to be unique
        """
        name, video_id, channel_id, uploadTime, url = video
        addVideo(self.db_connection, name, video_id, channel_id, uploadTime, url)

    def getOptionsFromDB(self):
        """
        returns a dict of all options stored in the option table
        """

        """
        list of options:
            last_check - string -> datetime -> TODO: implement the conversion
        """

        return selectOptions(self.db_connection)

    def getOptionFromDB(self, key):
        """
        returns a dict of all options stored in the option table
        """

        """
        list of options:
            last_checked - string -> datetime
        """
        option = selectOption(self.db_connection, key)
        if key == 'last_checked' and option is not None:
            option = datetime.datetime.fromisoformat(option).replace(tzinfo=datetime.timezone.utc)
            print(option)
        return option

    def addOptionToDB(self, option, value):
        """
        adds option to the table or 
        updates it to the new value
        """

        """
        current options:
            last_checked
        """
        if option == 'last_checked':
            value = value.isoformat(timespec='seconds')
        insertOption(self.db_connection, option, value)

    def findMatch(self, identifier):
        if self.opened:
            return findContent(self.db_connection, name=identifier, channel_id=identifier, upload_id=identifier)


if __name__ == "__main__":
    conn = connectionToDB(db_name)
    # resetTables(conn)
    checkForTables(conn)
    # createVideoTable(conn, reset=True)
    # tschannel = ["Tom Scott", "UCBa659QWEk1AI4Tg--mrJ2A", "UUBa659QWEk1AI4Tg--mrJ2A"]
    # addChannel(conn, tschannel[0], tschannel[1], tschannel[2], '', unique=False)
    # getChannels(conn)
    # deleteChannels(conn, all=True)

    insertOption(conn, "a", "b")
    insertOption(conn, "b", "b")
    insertOption(conn, "a", "c")
    options = selectOption(conn, 'c')
    print(options)

    # print(options)

    conn.close()