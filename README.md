# discord-bot 🤖

Welcome to the ``discord-bot`` repository!
This project aims to build a versatile music bot for the Discord server ``Wixoss Gaming``, enabling users to enjoy their favorite YouTube tunes directly within voice channels.


## Features 🎶
Our bot currently supports the following commands:

| Commands |                                                                                     |
|:---------|-------------------------------------------------------------------------------------|
| !add     | Adds a song (YouTube URL) to the playlist.                                          |
| !join    | Joins the current voice channel of the command author.                              |
| !leave   | Leaves the voice channel.                                                           |
| !pause   | Pauses the currently playing song.                                                  |
| !play    | Starts playing the next song in the playlist.                                       |
| !remove  | Removes the first n songs from the playlist (excluding the currently playing song). |
| !reset   | Stops the current song and clears the entire playlist.                              |
| !show    | Displays the songs in the playlist (including the currently playing song).          |
| !skip    | Skips the current song.                                                             |
| !volume  | Adjusts the volume of the audio playback.                                           |

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