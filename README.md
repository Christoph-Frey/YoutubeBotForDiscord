#
Discord Bot that allows to check from Discord for new videos
<hr>
This is a work in progress
<hr>
Setup

1. Get Api keys for Youtube And Discord
2. Add the discord bot to your server
3. create file secret.py in the base folder with <br>discordKey="\<discordApiKey\>" <br>youtubeKey="\<youtubeApiKey\>"
4. start the bot using python -u main.py

<hr>
<pre>
Commands:
<ul>
  <li><b>!register &lt;video_url&gt;</b>: adds the channel that released the video to the watchlist
<li><b>!unregister &lt;channel_name&gt;/&lt;channel_id&gt;/&lt;uploadList_id&gt;</b>: removes the channel matching the parameter
<li><b>!watchlist</b>: returns current watched channels
<li><b>!new</b>: returns new videos or time when last checked
  </ul>
  </pre>
