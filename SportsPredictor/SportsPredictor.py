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
    teamGameidList = [x.split("=")[1] for x in scheduleTree.xpath("//li[@class='score']/a/@href")]
    gameids |= set(teamGameidList)


playerMap = defaultdict(list)

position_number_dict = { ", PG" : 1,
        ", SG" : 2,
        ", SF" : 3,
        ", PF" : 4,
        ", C" : 5,
    }

def position_convert(str):
    return position_number_dict[str]

def date_time_convert(str):
    [a,b] = str.split(":")
    time = int(a) + float(b[0:2])/60
    
    [_,date] = str.split("ET, ")
    return [date,time]

for gameid in gameids:
    gameBoxScoreURL = "http://espn.go.com/nba/boxscore?gameId=" + gameid;
    boxScorePage = requests.get(gameBoxScoreURL)
    boxScoreTree = html.fromstring(boxScorePage.content)



    gameDataList = []
    game_time_info = boxScoreTree.xpath("//div[@class='game-time-location']/p/text()")[0]
    #print(game_time_info)

    [awayName,awayScore] = boxScoreTree.xpath("//div[@class='team away']/div/h3/*/text()")
    [homeName,homeScore] = boxScoreTree.xpath("//div[@class='team home']/div/h3/*/text()")
    scoreDifference = int(awayScore) - int(homeScore)
    #print(scoreDifference)
    #print(awayName)


    #awayTeamTRPositionXPath = "//table/thead/tr[contains(th/text(),'" + awayName + "')]/preceding-sibling::*"
    #awayTeamTRPosition = len(boxScoreTree.xpath(awayTeamTRPositionXPath))
    #print(boxScoreTree.xpath(awayTeamTRPositionXPath))
    #print(awayTeamTRPosition)

    #homeTeamTRPositionXPath = "//table/thead/tr[contains(th/text(),'" + awayName + "')]/preceding-sibling::*"
    #homeTeamTRPosition = len(boxScoreTree.xpath(homeTeamTRPositionXPath))
    #print(boxScoreTree.xpath(homeTeamTRPositionXPath))
    #print(homeTeamTRPosition)

    awayPlayeridList = boxScoreTree.xpath("//table/tbody[position()=1 or position()=2]/tr[contains(@class,'player-46')]/@class")
    awayPlayeridList = [x.split("player-46-")[1] for x in awayPlayeridList]
    #print(awayPlayeridList)


    homePlayeridList = boxScoreTree.xpath("//table/tbody[position()=4 or position()=5]/tr[contains(@class,'player-46')]/@class")
    homePlayeridList = [x.split("player-46-")[1] for x in homePlayeridList]
    #print(homePlayeridList)






    for playerid in awayPlayeridList:
        xPathString = "//tr[contains(@class,'player-46-" + playerid + "')]/*/text()"

        gameStatsList = []
        gameStatsList += date_time_convert(game_time_info) + [0,scoreDifference] # 0 for away team and score difference is calc away score - home score

        playerStatsList = boxScoreTree.xpath(xPathString)
        playerStatsList[0] = position_convert(playerStatsList[0])
       # print(playerStatsList)
       # playerMap[playerid].append(gameid)

        playerMap[playerid].append(gameStatsList+playerStatsList)

    
    for playerid in homePlayeridList:
        xPathString = "//tr[contains(@class,'player-46-" + playerid + "')]/*/text()"

        gameStatsList = []
        
        gameStatsList += date_time_convert(game_time_info) + [1, -1 * scoreDifference] # 1 for home team and score difference is calc away score - home score

        playerStatsList = boxScoreTree.xpath(xPathString)
        playerStatsList[0] = position_convert(playerStatsList[0])
       # print(playerStatsList)
       # playerMap[playerid].append(gameid)

        playerMap[playerid].append(gameStatsList+playerStatsList)

#print(playerMap)
for playerid in playerMap.keys():
    print(playerid)
    print(playerMap[playerid])