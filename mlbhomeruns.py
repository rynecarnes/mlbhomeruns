import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.espn.com/mlb/scoreboard'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

# BS4 element that stores every script tag on the page
allScriptTags = soup.find_all('script')

# Takes the 13th script tag, which is the one with data we want, and turns it into a string so we can perform string operations on it.
scriptContainingGameIds = str(allScriptTags[13])

# The character position of the first {. Should signify the beginning of the JSON object
firstIndex = scriptContainingGameIds.find('{')

# The character position of a string that should signify the end of the JSON object.
lastIndex = scriptContainingGameIds.rindex(';window.espn.scoreboardSettings')

# The string of the script tag we want and cutting of the beginning and end which should leave only JSON
gameIdsJson = scriptContainingGameIds[firstIndex:lastIndex]

# Loads the data into a Dict so that we can get the data more easily
scriptJsonDict = json.loads(gameIdsJson)

# Create new list to store gameIds
listOfGameIds = []
listOfEachTeamsHomeRuns = []

# Loop through all the events in the dict. eachEvent is a dict itself and then eachLink is a string that stores the very first value for the links key in the eachEvent dict
# eachLink is then sliced to retrieve the the end of the string which is the actual gameId. Each gameId is then added to the list of gameIds
for eachEvent in scriptJsonDict['events']:
    eachLink = eachEvent['links'][0]
    last = len(eachLink['href'])
    first = eachLink['href'].find('=')
    gameId = eachLink['href'][first + 1:last]
    listOfGameIds.append(gameId)

for eachGameId in listOfGameIds:
    boxscoreUrl = 'https://www.espn.com/mlb/boxscore?gameId=' + eachGameId

    # HARDCODED URL FOR TESTING
    #boxscoreUrl = 'https://www.espn.com/mlb/boxscore?gameId=401226296'

    boxscorePage = requests.get(boxscoreUrl)
    boxscoreSoup = BeautifulSoup(boxscorePage.text, 'html.parser')

    homeRunDiv = boxscoreSoup.find_all("div", {"title": "Home Runs"})
    teamSpan = boxscoreSoup.find_all("span", {"class": "short-name"})

    teamNames = []

    for team in teamSpan:
        teamName = str(team.contents)
        first = teamName.rindex('[')
        teamName = teamName[first + 2: len(teamName) - 2]
        teamNames.append(teamName)

    for i, div in enumerate(homeRunDiv):
        listItemParent = div.find_parent('li')
        listItemString = str(listItemParent.contents)
        first = listItemString.rindex('</div>, ')
        listItemString = listItemString[first + 10:len(listItemString) - 2]
        listOfEachTeamsHomeRuns.append(f"{teamNames[i]}: {listItemString}")

print(*listOfEachTeamsHomeRuns, sep="\n")
