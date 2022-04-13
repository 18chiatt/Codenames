# Codenames Guesser and Discord bot

This repo contains the code for both a CLI Codenames guesser and a discord bot for hosting that guesser.

Code is explained in Codenames Guesser.pdf, so feel free to check that out.

To setup, download the code and run `pip install -r requirements.txt`. Make sure you are on python>=3.9

To use the CLI, simply run `python CodeNames.py`

To host the discord bot, create a .env file and populate it with your discord api key, which should look something like this

`{"discordkey": "0123456789ABCDEF0123456789ABCDEF013456789ABCDEF"}`

Then, run the bot with `python bot.py`.

The default max concurrent games is 500, but you can configure it up/down depending on your needs/ram.
