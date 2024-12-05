# discord-bot 🤖

Welcome to the `discord-bot` repository!
This project aims to build a versatile music bot for the Discord server `Wixoss Gaming`, enabling users to enjoy their favorite YouTube tunes directly within voice channels.

## Features 🎶

Our bot currently supports the following commands:

| Commands      |                                                                  |
| :------------ | ---------------------------------------------------------------- |
| !add          | Adds an audio source (YouTube URL) to the playlist.              |
| !help         | Shows the list of commands.                                      |
| !id           | Shows role or text channel IDs.                                  |
| !join         | Joins the voice channel of the author.                           |
| !leave        | Leaves the voice channel.                                        |
| !pause        | Pauses the currently played audio source.                        |
| !permission   | Shows which roles or text channels can use each command.         |
| !play         | Starts playing the audio source from the playlist.               |
| !reset        | Stops the currently played audio source and clears the playlist. |
| !role         | Whitelist the specified roles for the command.                   |
| !show         | Shows the audio sources from the playlist.                       |
| !skip         | Skips the currently played audio source in the playlist.         |
| !text_channel | Whitelist the specified text channels for the command.           |
| !timeout      | Changes the timeout of the bot.                                  |
| !volume       | Changes the volume of the audio source.                          |

## Run the Bot on a Linux Server with `screen` 💻

This guide explains how to run the discord bot even after closing your SSH connection using the `screen` package from Linux.

1. Ensure `screen` is installed on your server:

```bash
sudo apt install screen
```

2. Launch a `screen` session:

```bash
screen
```

3. Within the screen session, run the Python script to start the bot:

```bash
python main.py
```

4. You can now safely close your SSH connection.
   The bot will continue running in the background within the screen session.
   To reconnect later use `screen -ls` to see a list of active `screen` sessions.
   Identify the session ID (e.g. `14760.pts-2.raspberrypi`) and reattach using:

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
