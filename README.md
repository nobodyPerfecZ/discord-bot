# discord-bot 🤖

Welcome to the ``discord-bot`` repository!
This project aims to build a versatile music bot for the Discord server ``Wixoss Gaming``, enabling users to enjoy their favorite YouTube tunes directly within voice channels.


## Features 🎶
Our bot currently supports the following commands:

| Commands |                                                                  |
|:---------|------------------------------------------------------------------|
| !join    | Joins the voice channel of the author.                           |
| !leave   | Leaves the voice channel.                                        |
| !add     | Adds an audio source (YouTube URL) to the playlist.              |
| !play    | Starts playing the audio source from the playlist.               |
| !pause   | Pauses the currently played audio source.                        |
| !skip    | Skips the currently played audio source in the playlist.         |
| !reset   | Stops the currently played audio source and clears the playlist. |
| !show    | Shows the audio sources from the playlist.                       |
| !set     | Changes the configuration of the music player.                   |

## Run the Bot on a Linux Server with ``screen`` 💻
This guide explains how to run the discord bot even after closing your SSH connection using the ``screen`` package from Linux.
1. Ensure ``screen`` is installed on your server:
```bash
sudo apt install screen
```
2. Launch a ``screen`` session: 
```bash
screen
```
3. Within the screen session, run the Python script to start the bot:
```bash
python main.py
```
4. You can now safely close your SSH connection.
The bot will continue running in the background within the screen session.
To reconnect later use `screen -ls` to see a list of active ``screen`` sessions.
Identify the session ID (e.g. ``14760.pts-2.raspberrypi``) and reattach using:
```bash
screen -r <session_id>
```
5. To stop the bot, use the following command to quit the session entirely:
```bash
screen -XS <session-id> quit
```


## Contributing 🔧
We welcome any contribution to this project. If you found any bugs, want to change a feature or to add a new feature, 
please open an issue and submit a pull request for it.