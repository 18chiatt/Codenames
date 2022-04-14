from cachetools import LRUCache
import discord
import json

from CodeNames import Game
from CodeNames import save
MAX_CONCURENT_GAMES = 500

class MyClient(discord.Client):
    
    def __init__(self):
        super(). __init__()
        self.games = LRUCache(MAX_CONCURENT_GAMES)

    
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: discord.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        user = message.author
        if not message.content.startswith('#'):
            return
        text :str = message.content.lower()
        if text.startswith("#about"):
            responseLines = ["Start a new game with the #init command, for example: ",
                       "```#init cheese broccoli shoe glove hand steak```",
                       "Remove words from your current game using #remove, for example:",
                       "```#remove glove hand```",
                       "Get predictions of a guess using the #guess command, for example:",
                       "```#guess food 2```"]
            await message.channel.send("\n".join(responseLines))

        if text.startswith('#init'):
            words = text.split(' ')[1:]
            if len(words) < 4:
                await message.channel.send("Sorry, please enter at least 5 words for analysis")
                return
            if len(words) > 50:
                await message.channel.send("Sorry, max game size is 50")
                return
            game = Game(words)
            if game.initErrors:
                await message.channel.send(f"Warning: {','.join(game.initErrors)}" )
            self.games[str(user)] = game
            await message.channel.send('Inited')
        
        if text.startswith("#guess"):
            try:
                segments = text.split(' ')
                count = None
                if not self.games.get(str(user) ):
                    await message.channel.send("Please start a game first")
                    return
                game: Game = self.games.get(str(user))
                if len(segments) != 3:
                    await message.channel.send("Usage: #guess {hint} {quantity}")
                try:
                    count = int(segments[2],10)
                except:
                    await message.channel.send("Usage: #guess {hint} {quantity}")
                retVal = game.turn(segments[1],count)
                strs = "".join([g for g in retVal])
                await message.channel.send(strs)
            except Exception as e:
                await message.channel.send(f"An error occured while processing your request: {e.with_traceback}")
        
        if text.startswith("#reduce"):
            game = self.games.get(str(user))
            if not game:
                await message.channel.send("Please start a game first")
                return
            toReduce = set(map(lambda x : x.lower(), text.split(" ")[1:]))
            newwords = list(filter(lambda x : x not in toReduce, game.wordsInPlay))
            game.setWords(newwords)
            await message.channel.send(f"@{str(user)}\nReduced successfully, new word list: {' '.join(newwords)}"  )

def envSetup():
    print("Please create JSON file .env with contents similar to\n", json.dumps({"discordkey":"1234123412341234"}))

client = MyClient()
save()
secrets = None
try:
    with open('.env') as file:
        secrets = json.loads(file.read())
except Exception as e:
    envSetup()
    quit()

if secrets.get('discordkey', None) is None:
    envSetup()
    quit()
client.run(secrets["discordkey"])

