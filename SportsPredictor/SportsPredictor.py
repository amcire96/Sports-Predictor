from lxml import html
import requests
import pandas as pd
from collections import defaultdict

teamsPage = requests.get("http://espn.go.com/nba/teams")
teamsTree = html.fromstring(teamsPage.content)

teamsURLs = teamsTree.xpath("//a[@class='bi']/@href")


gameids = set([])
for teamURL in teamsURLs:
    [a,b,c] = teamURL.partition("_")
    scheduleURL = a + "schedule/" + b + c;
    schedulePage = requests.get(scheduleURL)
    scheduleTree = html.fromstring(schedulePage.content)
    gameidList = [x.split("=")[1] for x in scheduleTree.xpath("//li[@class='score']/a/@href")]
    gameids |= set(gameidList)


playerMap = defaultdict(list)

for gameid in ["400827965"]:
    gameBoxScoreURL = "http://espn.go.com/nba/boxscore?gameId=" + gameid;
    boxScorePage = requests.get(gameBoxScoreURL)
    boxScoreTree = html.fromstring(boxScorePage.content)

    playeridList = boxScoreTree.xpath("//tr[contains(@class,'player-46')]/@class")
    playeridList = [x.split("player-46-")[1] for x in playeridList]
    #print(playeridList)

    for playerid in ["2991280"]:
        className1 = "odd player-46-" + playerid
        className2 = "even player-46-" + playerid
       # print(className)
        playerStatsList = boxScoreTree.xpath("//tr[@class = className1]/@class")
        print(playerStatsList)
        playerMap[playerid].append(playerStatsList)

#print(playerMap)