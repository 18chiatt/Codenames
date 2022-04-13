
from cmath import e
from threading import Timer
import wikipediaapi as wapi
import requests
import json
import urllib.parse
import numpy as np
import os
import re
import random
import io
import pickle

##This code is not optimized, but it is fun

BASE_PATH = 'https://en.wikipedia.org/w/api.php'
api = wapi.Wikipedia('en')
NUM_RESULTS = 2
punc_regex = r'[^\w ]'


def pickleOrDict(name:str):
    try:
        with open(name, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(e, 'read')
        return {}

def saveObj(obj, name: str ):
    with open(name, 'wb') as file:
        try:
            pickle.dump(obj, file)
        except Exception as e:
            print(e)

pagecache = pickleOrDict('pageCache')
searchCache = pickleOrDict('searchCache')
relatedCache = pickleOrDict('relatedCache')
table = None

def saveCache():
    saveObj(pagecache, 'pageCache')
    saveObj(searchCache, 'searchCache')
    saveObj(relatedCache, 'relatedCache')

def instructions():
    print("Please get the word list by running the following commands")
    print("wget http://nlp.stanford.edu/data/glove.42B.300d.zip")
    print('unzip glove.42B.300d.zip')
    print('head -n 500000 glove.42B.300d.txt > glove_vectors.txt')
    exit()



def default():
    with open('defaultWords.txt', 'r') as file:
        words = list(map(lambda x : x.replace(' ','-').strip().lower(), file.readlines()))
        return random.sample(words,25)

def getPageNames(name: str) -> list[str]:
    if searchCache.get(name, None):
        return searchCache.get(name)
    searchParaams = {'action':'query', 'list':'search', 'srsearch': urllib.parse.quote(name), 'utf8':'1', 'format':'json', 'srlimit': NUM_RESULTS}
    r = requests.get(BASE_PATH,searchParaams)
    obj = json.loads(r.text)
    result = [curr.get('title') for curr in obj.get('query').get('search')][:NUM_RESULTS]
    searchCache[name] = result
    return result

def getPage(title: str) -> wapi.WikipediaPage:
    if pagecache.get(title, None):
        return pagecache.get(title)
    page = api.page(title)
    pagecache[title] = page
    return page

def getRelated(word: str) -> dict:
    if word in relatedCache:
        return relatedCache.get(word)
    wordPageNames = getPageNames(word)
    frequency = {}
    pages = [getPage(name) for name in wordPageNames]
    newPages = []
    for page in pages:
        noPunc = re.sub(punc_regex, ' ', page.text.encode('ascii',errors='ignore').decode('utf8')).lower().split(' ')
        for word in noPunc:
            if not word:
                continue
            frequency[word] = frequency.get(word, 0) + 1
        newPages.extend(page.links.values())
    relatedCache[word] = frequency

    return frequency

def getWordLinks(word: str) -> set[str]:
    pageNames = getPageNames(word)
    pages = [getPage(page) for page in pageNames]
    links = []
    for page in pages:
        keys = page.links.keys()
        links.extend(filter(lambda x : ':' not in x, page.links.keys()))
    return set(links)



def createFastData() -> dict:
    wfile = open('words.txt', 'w', encoding='utf8')
    matrix = []
    try:
        lines = open('./glove_vectors.txt', 'r', encoding='utf8').readlines()
    except Exception:
        instructions()
    for line in lines:
        entries = line.split(' ')
        word = entries[0].encode('ascii',errors='ignore').decode('utf8')
        wfile.write(word + "\n")
        values = np.array(entries[1:], dtype='float32')
        matrix.append(values)
    wfile.close()
    np.save('matrix', np.array(matrix))

def hasFastData() -> bool:
    return os.path.exists('./matrix.npy') and os.path.exists('./words.txt')

def getFastData() -> dict:
    lookup = {}
    nums = np.load('./matrix.npy')
    with open('./words.txt', 'r', encoding='utf8') as wordFile:
        words = wordFile.readlines()
        for index, word in enumerate(words):
            lookup[word[:-1]] = nums[index]
    return lookup

def dist(arr1, arr2) -> float:
    return np.linalg.norm(arr1 - arr2)

def wordDist(w1, w2)-> float:
    return dist(table[w1], table[w2])

def confidencePercent(confidence):
    # Sigmoid activation functoin
    return 1- (1 / (1 + pow(e, -(confidence-8.5))))

def scaledWordSimilarity(w1, w2):
    distance = wordDist(w1,w2)
    return 1.0 - (1.0 / (1.0 + pow(e,-(distance*.8 - 6) )))

def wikipediaSimilarity(count):
    return 1.0 / (1.0 + pow(e,-count*.3))

def rawSigmoid(score):
    return 1.0/(1.0 + pow(e,-(score-1)))

class Game:
    def __init__(self, words=None) -> None:
        self.wordsInPlay = words or []
        self.ready = False
        for word in words:
            if not (word in table):
                print(f"{word} not in dictionary :(")
            getRelated(word)
        self.ready = True

    def printTableSuggestions(self, hint: str, guesses: int) -> list[str]:
        goal = table[hint]
        distances = [(dist(goal,table[word] ), word) for word in self.wordsInPlay]
        distances.sort()
        predictions = distances[:guesses+1]
        self.printPredictionConfidence(predictions)
        return

    def printPredictionConfidence(self, predictions):
        print("\n====Semantic similarity====\n", file=self.stream)
        for confidence, word in predictions:
            perecent = confidencePercent(confidence) * 100
            print(f'{word} {perecent:.2f}%', file=self.stream)


    def getAndDisplayWikipediaSuggestions(self, hint: str, guesses: int)-> list[str]:
        hintMentions = getRelated(hint)
        score = [(0,word, '') for word in self.wordsInPlay]

        for index, wordInPlay in enumerate(self.wordsInPlay):
            if wordInPlay in hintMentions: 
                score[index] = (hintMentions.get(wordInPlay) * 2, wordInPlay, f"{hint} directly mentioned {wordInPlay} {hintMentions.get(wordInPlay)} times")
        for mentionedWord in hintMentions.keys():
            if not (mentionedWord in table):
                continue
            for index, wordInPlay in enumerate(self.wordsInPlay):
                similarityScore = scaledWordSimilarity(mentionedWord,wordInPlay)
                if similarityScore > score[index][0]:
                    score[index] = (similarityScore, wordInPlay, f"{hint} mentioned '{mentionedWord}', which may be similar to '{wordInPlay}', a total of {hintMentions.get(mentionedWord)} times")    

        for index, wordInPlay in enumerate(self.wordsInPlay):
            mentioned = getRelated(wordInPlay) #all words related to a given goal
            if hint in mentioned:
                score[index] = (mentioned.get(hint) * 2,wordInPlay, f"{wordInPlay} directly mentioned {hint} {mentioned.get(hint)} times")
            if not (hint in table):
                continue
            for word in mentioned.keys():
                if not (word in table):
                    continue
                similarityScore = scaledWordSimilarity(word,hint)
                if similarityScore > score[index][0]:
                    score[index] = (similarityScore, wordInPlay, f"{wordInPlay} mentioned '{word}', which may be similar to '{hint}' a total of {mentioned.get(word)} times")
        
        targetLinks = set(getWordLinks(hint))

        for index, wordInPlay in enumerate(self.wordsInPlay):
            #Build a case
            shared = []
            links = getWordLinks(wordInPlay)
            for link in links:
                if link in targetLinks:
                    shared.append(link)
            if not shared:
                continue
            if len(shared) / len(links) < .05:
                continue
            currScore = len(shared)
            explain = f"{hint} and {wordInPlay} Link to {(len(shared)/len(links)) * 100:.2f}% of the same articles"
            if currScore > score[index][0]:
                score[index] = (currScore, wordInPlay, explain)
        
        self.displayWikipediaSuggestions(score, guesses)

    def displayWikipediaSuggestions(self, matches: list, guesses: int):
        print("\n====Wikipedia similarity====\n", file=self.stream)
        matches.sort(reverse=True)
        for score, word, reason  in matches[:guesses+1]:
            print(f'{word} {(rawSigmoid(score) )*100:.2f}% {reason}', file=self.stream)
        print('', file=self.stream)

    def setWords(self, words):
        self.wordsInPlay = words

    def turn(self,  hint, guesses):
        self.stream = io.StringIO('')
        if not self.ready:
            print("Not done initializing", file=self.stream)
            return
        
        if table.get(hint, None) is not None:
                self.printTableSuggestions(hint, guesses)
        else:
            print("Unable to find semantic similarities, did you use a very uncommon word?", file=self.stream)
        self.getAndDisplayWikipediaSuggestions(hint, guesses)
        self.stream.seek(0)
        return self.stream

if not hasFastData():
    print("Initializing data")
    createFastData()
table = getFastData()


#Get words in play
def getWords():
    wordsInPlay = input("Please enter the words available to be chosen with a space between them (i.e. cheese house skyscraper)").split(' ')
    if len(wordsInPlay) == 1:
        wordsInPlay = default()
        print("No Words entered, here are the options")
        print(" ".join(wordsInPlay), '\n')
    return  list(map(lambda x : x.lower(), wordsInPlay) )


def filterWords(words):
    toElim = set(map(lambda x : x.lower(), input('Enter any already selected words (separated by spaces): ').split(' ')))
    return list(filter(lambda x : x not in toElim, words))


if __name__ =="__main__":
    words = getWords()
    game = Game(words)
    while True:
        words = filterWords(words)
        hint = input("Enter the hint: ").lower()
        guesses = int(input("Enter the number of guesses:"))
        game.setWords(words)
        stream = game.turn(hint, guesses)
        for row in stream:
            print(row)

##Update the caches every two hours
def save():
    Timer(7200, save).start()
    saveCache()

save()
