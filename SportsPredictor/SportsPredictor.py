from lxml import html
import requests
import pandas as pd
from collections import defaultdict
from collections import OrderedDict
import datetime
import os
import json




#converts position to number
position_number_dict = { ", PG" : 1,
        ", SG" : 2,
        ", SF" : 3,
        ", PF" : 4,
        ", C" : 5,
    }

#converts team name to number
team_dict = {
        "Boston Celtics" : 1,
        "Brooklyn Nets" : 2,
        "New York Knicks" : 3,
        "Philadelphia 76ers" : 4,
        "Toronto Raptors" : 5,
        "Chicago Bulls" : 6,
        "Cleveland Cavaliers" : 7,
        "Detroit Pistons" : 8,
        "Indiana Pacers" : 9,
        "Milwaukee Bucks" : 10,
        "Atlanta Hawks" : 11,
        "Charlotte Hornets" : 12,
        "Miami Heat" : 13,
        "Orlando Magic" : 14,
        "Washington Wizards" : 15,
        "Golden State Warriors" : 16,
        "Los Angeles Clippers" : 17, 
        "Los Angeles Lakers" : 18,
        "Phoenix Suns" : 19,
        "Sacramento Kings" : 20,
        "Dallas Mavericks" : 21,
        "Houston Rockets" : 22,
        "Memphis Grizzlies" : 23,
        "New Orleans Pelicans" : 24,
        "San Antonio Spurs" : 25,
        "Denver Nuggets" : 26,
        "Minnesota Timberwolves" : 27,
        "Oklahoma City Thunder" : 28,
        "Portland Trail Blazers" : 29,
        "Utah Jazz" : 30
    }

#converts month name to number
#has full months and also abbreviated months for months during the NBA season
monthdict = {
        "January": 1,
        "Jan" : 1,
        "February" : 2,
        "Feb" : 2,
        "March" : 3,
        "Mar" : 3,
        "April" : 4,
        "Apr" : 4,
        "May" : 5,
        "June" : 6,
        "July" : 7,
        "August" : 8,
        "September" : 9,
        "October" : 10,
        "Oct" : 10,
        "November" : 11,
        "Nov" : 11,
        "December" : 12,
        "Dec" : 12
    }






#read the file and extract the json/defaultdict
f = open("PlayerStats.txt","r")
lastModifiedStr = f.readline()

#checks if file is how it should be formatted
# (Last Modified: ... \n playerStats Dictionary)
# if not formatted properly, it will overwrite whole file with stats from whole season
if(not "Last Modified:" in lastModifiedStr):
    currentMap = defaultdict(OrderedDict)
    #before the season started so it will get all the data from this season
    lastModifiedDate = datetime.date(2015, 10, 1)
else:
    #print(lastModifiedStr)
    [_,dateString] = lastModifiedStr.split(": ")
    [month, day, year] = dateString.split("/")
    lastModifiedDate = datetime.date(int(year),int(month),int(day))
    #print(lastModifiedDate)

    currentMap = json.loads(f.readline())
    #print(currentMap)

f.close()

#today's date to label when writing the json
today = datetime.date.today()
todayStr = str(today.month) + "/" + str(today.day) + "/" + str(today.year)

lastModifiedDate = datetime.date(2015,11,1)

def extractNewGameIDs(gameidsList,dateList):
    #print(lastModifiedDate)
    i=0
    for i in range(0,len(dateList)):
        
        dateStr = dateList[i]
        [_,monthAbbrStr,dayStr] = dateStr.split(" ")
        monthInt = monthdict[monthAbbrStr]
        dayInt = int(dayStr)
        #FIND BETTER SOLUTION FOR THIS
        if(monthInt > 6):
            yearInt = 2015
        else:
            yearInt = 2016
        #print(datetime.date(yearInt,monthInt,dayInt))
        date = datetime.date(yearInt,monthInt,dayInt)
        if(lastModifiedDate <= date):
            break
    #print(str(i))
    return gameidsList[i:]

#use teamURLs to access their schedules
#use team schedules 
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
    gameDateList = scheduleTree.xpath("//tr[td/ul/li/@class='score']/td[position() = 1]/text()")
    newGameIDs = extractNewGameIDs(teamGameidList,gameDateList)
    #print(newGameIDs)
    gameids |= set(newGameIDs)





#takes list of string statistics and converts to numbers
def playerStatsConvert(statsList):
    
    positionNum = position_number_dict[statsList[0]]

    if("DNP" in statsList[1]):
        return [positionNum, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    #strings #make-#attempted split into 2 int categories
    mins = int(statsList[1])
    [fgmstr,fgastr] = statsList[2].split("-")
    fgm = int(fgmstr)
    fga = int(fgastr)

    [tpmstr,tpastr] = statsList[3].split("-")
    tpm = int(tpmstr)
    tpa = int(tpastr)

    [ftmstr,ftastr] = statsList[4].split("-")
    ftm = int(fgmstr)
    fta = int(fgastr)

    restOfList = []
    for i in range(5,15):
        restOfList.append(int(statsList[i]))


    return [positionNum, mins, fgm, fga, tpm, tpa, ftm, fta] + restOfList

#takes string with date and time game info and returns this info in int categories
def date_time_convert(str):
    [a,b] = str.split(":")
    time = int(a) + float(b[0:2])/60
    
    [_,dateStr] = str.split("ET, ")
    [monthDayStr,yearStr] = dateStr.split(", ")
    [monthStr,dayStr] = monthDayStr.split(" ")
    return [monthdict[monthStr], int(dayStr), int(yearStr), time]


#use defaultdict to map playerids to game stats
playerMap = defaultdict(OrderedDict)
#playerMap = OrderedDict()


for gameid in sorted(gameids):
    gameBoxScoreURL = "http://espn.go.com/nba/boxscore?gameId=" + gameid;
    boxScorePage = requests.get(gameBoxScoreURL)
    boxScoreTree = html.fromstring(boxScorePage.content)


    #first get game data not specific to each player (time,date,score,team numbers etc)
    gameDataList = []
    game_time_info = boxScoreTree.xpath("//div[@class='game-time-location']/p/text()")[0]
    #print(game_time_info)

    [awayName,awayScore] = boxScoreTree.xpath("//div[@class='team away']/div/h3/*/text()")
    [homeName,homeScore] = boxScoreTree.xpath("//div[@class='team home']/div/h3/*/text()")
    scoreDifference = int(awayScore) - int(homeScore)
    #print(scoreDifference)
    #print(awayName)


    #keep track of which players were on the away team and which were on the home team
    [awayTeam] = boxScoreTree.xpath("//table/thead[position()=1]/tr[@class='team-color-strip']/th/text()")
    awayTeamNum = team_dict[awayTeam]
    awayPlayeridList = boxScoreTree.xpath("//table/tbody[position()=1 or position()=2]/tr[contains(@class,'player-46')]/@class")
    awayPlayeridList = [x.split("player-46-")[1] for x in awayPlayeridList]
    #print(awayPlayeridList)

    [homeTeam] = boxScoreTree.xpath("//table/thead[position()=4]/tr[@class='team-color-strip']/th/text()")
    homeTeamNum = team_dict[homeTeam]
    homePlayeridList = boxScoreTree.xpath("//table/tbody[position()=4 or position()=5]/tr[contains(@class,'player-46')]/@class")
    homePlayeridList = [x.split("player-46-")[1] for x in homePlayeridList]
    #print(homePlayeridList)


    #gets player stats for away players and appends that to the game stats
    for playerid in awayPlayeridList:
        xPathString = "//tr[contains(@class,'player-46-" + playerid + "')]/*/text()"

        gameStatsList = []
        # stores own team's number and also the opposing team's number
        # 0 for away team and score difference is calc away score - home score
        gameStatsList += date_time_convert(game_time_info) + [awayTeamNum, homeTeamNum] + [0,scoreDifference] 
        

        playerStatsList = boxScoreTree.xpath(xPathString)
        playerStatsList = playerStatsConvert(playerStatsList)
       # print(playerStatsList)
       # playerMap[playerid].append(gameid)
       # print(gameStatsList+playerStatsList)
        
        playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
        #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})
        

    #gets player stats for home players and appends that to the game stats
    for playerid in homePlayeridList:
        xPathString = "//tr[contains(@class,'player-46-" + playerid + "')]/*/text()"

        gameStatsList = []
        
        # stores own team's number and also the opposing team's number
        # 1 for home team and score difference is calc away score - home score
        gameStatsList += date_time_convert(game_time_info) + [homeTeamNum, awayTeamNum] + [1, -1 * scoreDifference]

        playerStatsList = boxScoreTree.xpath(xPathString)
        playerStatsList = playerStatsConvert(playerStatsList)
       # print(playerStatsList)
       # playerMap[playerid].append(gameid)

        playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
        #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})



#need to UNION currentMap(defaultdict in file) and playerMap(recent games)
for playerid,orderedDict in playerMap.items():

    for gameid,statList in orderedDict.items():
        #TODO: look to make this more efficient
        if(not gameid in currentMap[playerid]):
            currentMap[playerid][gameid] = statList

print(json.dumps(currentMap))

#write default dict into file -- default dict in json format
f = open("PlayerStats.txt","w")
f.write("Last Modified: " + todayStr + "\n")
f.write(json.dumps(currentMap))
f.close()
#print(playerMap)
#f = open(playerDataFilePath, "w")
#for playerid in playerMap.keys():

    #f.writeline(playerMap[playerid])
    #print(playerid)
    #print(playerMap[playerid])

#f.close()