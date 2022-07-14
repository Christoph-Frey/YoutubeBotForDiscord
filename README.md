#
Discord Bot that allows to check from Discord for new videos
<hr>
Setup

1. Get Api keys for Youtube And Discord
2. Add the discord bot to your server
3. create file secret.py if foler with
  discordKey="<discordApiKey>"
  youtubeKey="<youtubeApiKey>"
4. start the bot using python -u main.py

<hr>
Usage:
  !register <video_url>: adds the channel that released the video to the watchlist
  !unregister <channel_name>/<channel_id>/<uploadList_id>: removes the channel matching the parameter
  !watchlist: returns current watched channels
  !new: returns new videos or time when last checked
