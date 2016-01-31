from lxml import html
import requests
import pandas as pd
from collections import defaultdict
from collections import OrderedDict
from collections import deque
import datetime
import os
import json
import numpy as np
import csv

from scipy.stats import randint as sp_randint

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score
from sklearn.linear_model import *
from sklearn.grid_search import RandomizedSearchCV

from sklearn.ensemble import AdaBoostRegressor
#from sklearn import svm






#print("hello1")

f = open("PlayerIDMap.txt","r")
playerIDDict = json.loads(f.readline())
f.close()

#converts position to number
position_number_dict = { ", PG" : 1,
        ", SG" : 2,
        ", SF" : 3,
        ", PF" : 4,
        ", C" : 5,
        ", F" : 3.5,
    }

#converts team name to number
team_dict = {
        "Boston Celtics" : 1,
        "Celtics" : 1,
        "Brooklyn Nets" : 2,
        "Nets" : 2,
        "New York Knicks" : 3,
        "Knicks" : 3,
        "Philadelphia 76ers" : 4,
        "76ers" : 4,
        "Toronto Raptors" : 5,
        "Raptors" : 5,
        "Chicago Bulls" : 6,
        "Bulls" : 6,
        "Cleveland Cavaliers" : 7,
        "Cavaliers" : 7,
        "Detroit Pistons" : 8,
        "Pistons" : 8,
        "Indiana Pacers" : 9,
        "Pacers" : 9,
        "Milwaukee Bucks" : 10,
        "Bucks" : 10,
        "Atlanta Hawks" : 11,
        "Hawks" : 11,
        "Charlotte Hornets" : 12,
        "Hornets" : 12,
        "Miami Heat" : 13,
        "Heat" : 13,
        "Orlando Magic" : 14,
        "Magic" : 14,
        "Washington Wizards" : 15,
        "Wizards" : 15,
        "Golden State Warriors" : 16,
        "Warriors" : 16,
        "Los Angeles Clippers" : 17, 
        "Clippers" : 17,
        "Los Angeles Lakers" : 18,
        "Lakers" : 18,
        "Phoenix Suns" : 19,
        "Suns" : 19,
        "Sacramento Kings" : 20,
        "Kings" : 20,
        "Dallas Mavericks" : 21,
        "Mavericks" : 21,
        "Houston Rockets" : 22,
        "Rockets" : 22,
        "Memphis Grizzlies" : 23,
        "Grizzlies" : 23,
        "New Orleans Pelicans" : 24,
        "Pelicans" : 24,
        "San Antonio Spurs" : 25,
        "Spurs" : 25,
        "Denver Nuggets" : 26,
        "Nuggets" : 26,
        "Minnesota Timberwolves" : 27,
        "Timberwolves" : 27,
        "Oklahoma City Thunder" : 28,
        "Thunder" : 28,
        "Portland Trail Blazers" : 29,
        "Trail Blazers" : 29,
        "Utah Jazz" : 30,
        "Jazz" : 30
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



def strToDate(dateStr):
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
     return date

#takes string with date and time game info and returns this info in int categories
def date_time_convert(str):
    [a,b] = str.split(":")
    time = int(a) + float(b[0:2])/60
    
    [_,dateStr] = str.split("ET, ")
    [monthDayStr,yearStr] = dateStr.split(", ")
    [monthStr,dayStr] = monthDayStr.split(" ")
    return [monthdict[monthStr], int(dayStr), int(yearStr), time]


    

def readPlayerStatsFile():

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
        #print("month %d, day %d, year %d" % (int(month),int(day),int(year)))
        lastModifiedDate = datetime.date(int(year),int(month),int(day))
        #print(lastModifiedDate)
        #mydict = lambda: defaultdict(mydict)
        #currentMap = mydict()
        currentMap = json.loads(f.readline(),object_pairs_hook=OrderedDict)
        #print(currentMap)

    f.close()
    return (lastModifiedDate,currentMap)



#lastModifiedDate = datetime.date(2015,11,1)

#print("hello2")
#print(lastModifiedDate)


#generate playerMap for today's game -> will be what we are predicting
#map with have list of m, d, y, time, ownTeam, otherTeam, away/home
def create_todays_playerMap():
    today_playerMap = defaultdict(OrderedDict)

    schedulePage = requests.get("http://espn.go.com/nba/schedule")
    scheduleTree = html.fromstring(schedulePage.content)
    [date] = scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/caption/text()")

    todaysGameIDs = [x.split("=")[1] for x in scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/tbody/tr/td[position()=3]/a/@href")]
    #print(todaysGameIDs)

    for gameid in todaysGameIDs:

        gameBoxScoreURL = "http://espn.go.com/nba/boxscore?gameId=" + gameid
        boxScorePage = requests.get(gameBoxScoreURL)
        boxScoreTree = html.fromstring(boxScorePage.content)


        #first get game data not specific to each player (time,date,score,team numbers etc)
        gameDataList = []
        game_time_info = boxScoreTree.xpath("//div[@class='game-time-location']/p/text()")[0]
        #print(game_time_info)
        [m,d,y,t] = date_time_convert(game_time_info)

    
        [awayTeamName] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=1]/div[@class='team-info']/h3/a/text()")
        [homeTeamName] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=2]/div[@class='team-info']/h3/a/text()")

        [awayTeamURL] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=1]/div[@class='team-info']/h3/a/@href")
        #print(awayTeamName)
        [a,b]=awayTeamURL.split("_")
        awayRosterURL = a + "roster/_" + b
        awayRosterPage = requests.get(awayRosterURL)
        awayRosterTree = html.fromstring(awayRosterPage.content)
        awayPlayeridList = [x.split("player-46-")[1] for x in awayRosterTree.xpath("//tr[contains(@class,'player-46')]/@class")]
        #print(awayRosterURL)

        for playerid in awayPlayeridList:
            today_playerMap[playerid][gameid] = [m,d,y,t,team_dict[awayTeamName],team_dict[homeTeamName],0]

    
        [homeTeamURL] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=2]/div[@class='team-info']/h3/a/@href")
        #print(homeTeamURL)
        [a,b]=homeTeamURL.split("_")
        homeRosterURL = a + "roster/_" + b
        #print(homeRosterURL)
        homeRosterPage = requests.get(homeRosterURL)
        homeRosterTree = html.fromstring(homeRosterPage.content)
        homePlayeridList = [x.split("player-46-")[1] for x in homeRosterTree.xpath("//tr[contains(@class,'player-46')]/@class")]
        #print(homePlayeridList)
        for playerid in homePlayeridList:
            today_playerMap[playerid][gameid] = [m,d,y,t,team_dict[homeTeamName],team_dict[awayTeamName],1]
    
    return today_playerMap


def extractNewGameIDs(gameidsList,dateList):
    #print(gameidsList)
    #print(dateList)
    #print(lastModifiedDate)
    i=0
    for i in range(0,len(dateList)):
        
        dateStr = dateList[i]
        date = strToDate(dateStr)
       # print(date)
        #print(lastModifiedDate)
        if(lastModifiedDate <= date):
            #print(date)
            break
    #print(str(i))
    #print(dateList[i:])
    return gameidsList[i:]




def getNewGameIDs():
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
    return gameids




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






#print(gameids)


def createPlayerMap(gameids,currentMap):

    #use defaultdict to map playerids to game stats
    playerMap = defaultdict(OrderedDict)
    #playerMap = OrderedDict()


    for gameid in sorted(gameids):
        #print(gameid)
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
            #if(not gameid in currentMap[playerid] or not playerid in currentMap):
            if(not playerid in currentMap):
                currentMap[playerid] = OrderedDict()
            #print(type(gameid))
            currentMap[playerid][gameid] = statList

    return currentMap







#print(json.dumps(currentMap))

#print("hello4")

def writePlayerStats(currentMap):

    #today's date to label when writing the json
    today = datetime.date.today()
    todayStr = str(today.month) + "/" + str(today.day) + "/" + str(today.year)

    #write default dict into file -- default dict in json format
    f = open("PlayerStats.txt","w")
    f.write("Last Modified: " + todayStr + "\n")
    f.write(json.dumps(currentMap,sort_keys=True))
    f.close()

#print("hello5")


#print(playerMap)


#f = open(playerDataFilePath, "w")
#for playerid in playerMap.keys():

    #f.writeline(playerMap[playerid])
    #print(playerid)
    #print(playerMap[playerid])

#f.close()


#gameStatsLists are restricted by their maxlen variables
#if size of gameStatsList < desired number of games, then just avg what you have in gameStatsList
#   e.g. when gen features for 2nd game of season, all lists will just be stats from 1st game
def avgStats(gameStatsList):
    gameCount = len(gameStatsList)
    return (np.array([sum(x) for x in zip(*gameStatsList)]) / gameCount).tolist()
    


def generate_features(stats,today_stats):
     #print(today_stats)
     #featureList = OrderedDict(list)
     trainingFeatureList = deque([])
     testingFeatureList = deque([])

     todayFeatureList = deque([])
     
     for playerid,orderedDict in currentMap.items():
         
         #prevGameIds = deque([])
         #19 stats for each game
         seasonGameStatsTotals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
         prevGameStats = []
         #use deques with max size to keep track of most recent n games
         prev2GamesStats = deque([],2)
         prev3GamesStats = deque([],3)
         prev5GamesStats = deque([],5)
         prev10GamesStats = deque([],10)
         prev20GamesStats = deque([],20)

         count = 0

         #need how many games stats each player has
         #  split 80%-20% train-test
         #  best to split by time
         #first 4/5 of (games-first) = train, rest for test
         gamesForPlayer = len(orderedDict)


         for gameid,statList in orderedDict.items():
             gameFeature = [int(playerid)] + [int(gameid)] + statList[:7]

             #don't do anything for the first game
             if (count != 0):
                 gameFeature += prevGameStats
                 gameFeature += avgStats(prev2GamesStats)
                 gameFeature += avgStats(prev3GamesStats)
                 gameFeature += avgStats(prev5GamesStats)
                 gameFeature += avgStats(prev10GamesStats)
                 gameFeature += avgStats(prev20GamesStats)
                 gameFeature += (np.array(seasonGameStatsTotals) / count).tolist()
                 
                 if(count <= 0.8 * (gamesForPlayer-1)):
                     trainingFeatureList.append(gameFeature)
                 else:
                     testingFeatureList.append(gameFeature)

             count+=1
             #prevGameIds += [gameid]     
             prevGameStats = statList[7:]    
             prev2GamesStats.append(statList[7:])
             prev3GamesStats.append(statList[7:])
             prev5GamesStats.append(statList[7:])
             prev10GamesStats.append(statList[7:])
             prev20GamesStats.append(statList[7:])
             seasonGameStatsTotals = [x + y for x, y in zip(seasonGameStatsTotals,statList[7:])]
        
         if(playerid in today_stats):
             (key,val) = today_stats[playerid].popitem()
             feature = [int(playerid)] + [int(key)] + val[:7] + prevGameStats + avgStats(prev2GamesStats) + avgStats(prev3GamesStats) + avgStats(prev5GamesStats) + avgStats(prev10GamesStats) + avgStats(prev20GamesStats) + (np.array(seasonGameStatsTotals) / count).tolist()
             todayFeatureList.append(feature)

         #print(list(todayFeatureList))

     return (list(trainingFeatureList),list(testingFeatureList), list(todayFeatureList))



#(trainingFeatures,testingFeatures, todayFeatureList) = generate_features(currentMap,create_todays_playerMap())


def writeFeaturesFiles(trainingFeatures,testingFeatures,todayFeatureList):

    with open('TodayFeatures.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["playerid","gameid","month","day","year","time","ownTeam","otherTeam","away/home",
                         "lastgame-scoreDiff","lastgame-position","lastgame-mins","lastgame-fgm","lastgame-fga",
                         "lastgame-3pm","lastgame-3pa","lastgame-ftm","lastgame-fta","lastgame-dreb","lastgame-oreb","lastgame-reb",
                         "lastgame-ast","lastgame-stl","lastgame-blk","lastgame-to","lastgame-pf","lastgame+/-","lastgame-pts",                     
                        "last2games-scoreDiff","last2games-position","last2games-mins","last2games-fgm","last2games-fga","last2games-3pm",
                         "last2games-3pa","last2games-ftm","last2games-fta","last2games-dreb","last2games-oreb","last2games-reb",
                         "last2games-ast","last2games-stl","last2games-blk","last2games-to","last2games-pf","last2games+/-","last2games-pts",                     
                         "last3games-scoreDiff","last3games-position","last3games-mins","last3games-fgm","last3games-fga","last3games-3pm",
                         "last3games-3pa","last3games-ftm","last3games-fta","last3games-dreb","last3games-oreb","last3games-reb",
                         "last3games-ast","last3games-stl","last3games-blk","last3games-to","last3games-pf","last3games+/-","last3games-pts",
                         "last5games-scoreDiff","last5games-position","last5games-mins","last5games-fgm","last5games-fga","last5games-3pm",
                         "last5games-3pa","last5games-ftm","last5games-fta","last5games-dreb","last5games-oreb","last5games-reb",
                         "last5games-ast","last5games-stl","last5games-blk","last5games-to","last5games-pf","last5games+/-","last5games-pts",
                         "last10games-scoreDiff","last10games-position","last10games-mins","last10games-fgm","last10games-fga","last10games-3pm",
                         "last10games-3pa","last10games-ftm","last10games-fta","last10games-dreb","last10games-oreb","last10games-reb",
                         "last10games-ast","last10games-stl","last10games-blk","last10games-to","last10games-pf","last10games+/-","last10games-pts",
                         "last20games-scoreDiff","last20games-position","last20games-mins","last20games-fgm","last20games-fga","last20games-3pm",
                         "last20games-3pa","last20games-ftm","last20games-fta","last20games-dreb","last20games-oreb","last2games-reb",
                         "last20games-ast","last20games-stl","last20games-blk","last20games-to","last20games-pf","last20games+/-","last20games-pts",                     
                         "season-scoreDiff","season-position","season-mins","season-fgm","season-fga","season-3pm","season-3pa",
                         "season-ftm","season-fta","season-dreb","season-oreb","season-reb",
                         "season-ast","season-stl","season-blk","season-to","season-pf","season+/-","season-pts"])
        writer.writerows(todayFeatureList)

    with open('TrainingFeatures.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["playerid","gameid","month","day","year","time","ownTeam","otherTeam","away/home",
                         "lastgame-scoreDiff","lastgame-position","lastgame-mins","lastgame-fgm","lastgame-fga",
                         "lastgame-3pm","lastgame-3pa","lastgame-ftm","lastgame-fta","lastgame-dreb","lastgame-oreb","lastgame-reb",
                         "lastgame-ast","lastgame-stl","lastgame-blk","lastgame-to","lastgame-pf","lastgame+/-","lastgame-pts",                    
                         "last2games-scoreDiff","last2games-position","last2games-mins","last2games-fgm","last2games-fga","last2games-3pm",
                         "last2games-3pa","last2games-ftm","last2games-fta","last2games-dreb","last2games-oreb","last2games-reb",
                         "last2games-ast","last2games-stl","last2games-blk","last2games-to","last2games-pf","last2games+/-","last2games-pts",                   
                         "last3games-scoreDiff","last3games-position","last3games-mins","last3games-fgm","last3games-fga","last3games-3pm",
                         "last3games-3pa","last3games-ftm","last3games-fta","last3games-dreb","last3games-oreb","last3games-reb",
                         "last3games-ast","last3games-stl","last3games-blk","last3games-to","last3games-pf","last3games+/-","last3games-pts",
                         "last5games-scoreDiff","last5games-position","last5games-mins","last5games-fgm","last5games-fga","last5games-3pm",
                         "last5games-3pa","last5games-ftm","last5games-fta","last5games-dreb","last5games-oreb","last5games-reb",
                         "last5games-ast","last5games-stl","last5games-blk","last5games-to","last5games-pf","last5games+/-","last5games-pts",
                         "last10games-scoreDiff","last10games-position","last10games-mins","last10games-fgm","last10games-fga","last10games-3pm",
                         "last10games-3pa","last10games-ftm","last10games-fta","last10games-dreb","last10games-oreb","last10games-reb",
                         "last10games-ast","last10games-stl","last10games-blk","last10games-to","last10games-pf","last10games+/-","last10games-pts",
                         "last20games-scoreDiff","last20games-position","last20games-mins","last20games-fgm","last20games-fga","last20games-3pm",
                         "last20games-3pa","last20games-ftm","last20games-fta","last20games-dreb","last20games-oreb","last2games-reb",
                         "last20games-ast","last20games-stl","last20games-blk","last20games-to","last20games-pf","last20games+/-","last20games-pts",                    
                         "season-scoreDiff","season-position","season-mins","season-fgm","season-fga","season-3pm","season-3pa",
                         "season-ftm","season-fta","season-dreb","season-oreb","season-reb",
                         "season-ast","season-stl","season-blk","season-to","season-pf","season+/-","season-pts"])
        writer.writerows(trainingFeatures)

    with open('TestingFeatures.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["playerid","gameid","month","day","year","time","ownTeam","otherTeam","away/home",
                         "lastgame-scoreDiff","lastgame-position","lastgame-mins","lastgame-fgm","lastgame-fga",
                         "lastgame-3pm","lastgame-3pa","lastgame-ftm","lastgame-fta","lastgame-dreb","lastgame-oreb","lastgame-reb",
                         "lastgame-ast","lastgame-stl","lastgame-blk","lastgame-to","lastgame-pf","lastgame+/-","lastgame-pts",                     
                        "last2games-scoreDiff","last2games-position","last2games-mins","last2games-fgm","last2games-fga","last2games-3pm",
                         "last2games-3pa","last2games-ftm","last2games-fta","last2games-dreb","last2games-oreb","last2games-reb",
                         "last2games-ast","last2games-stl","last2games-blk","last2games-to","last2games-pf","last2games+/-","last2games-pts",                     
                         "last3games-scoreDiff","last3games-position","last3games-mins","last3games-fgm","last3games-fga","last3games-3pm",
                         "last3games-3pa","last3games-ftm","last3games-fta","last3games-dreb","last3games-oreb","last3games-reb",
                         "last3games-ast","last3games-stl","last3games-blk","last3games-to","last3games-pf","last3games+/-","last3games-pts",
                         "last5games-scoreDiff","last5games-position","last5games-mins","last5games-fgm","last5games-fga","last5games-3pm",
                         "last5games-3pa","last5games-ftm","last5games-fta","last5games-dreb","last5games-oreb","last5games-reb",
                         "last5games-ast","last5games-stl","last5games-blk","last5games-to","last5games-pf","last5games+/-","last5games-pts",
                         "last10games-scoreDiff","last10games-position","last10games-mins","last10games-fgm","last10games-fga","last10games-3pm",
                         "last10games-3pa","last10games-ftm","last10games-fta","last10games-dreb","last10games-oreb","last10games-reb",
                         "last10games-ast","last10games-stl","last10games-blk","last10games-to","last10games-pf","last10games+/-","last10games-pts",
                         "last20games-scoreDiff","last20games-position","last20games-mins","last20games-fgm","last20games-fga","last20games-3pm",
                         "last20games-3pa","last20games-ftm","last20games-fta","last20games-dreb","last20games-oreb","last2games-reb",
                         "last20games-ast","last20games-stl","last20games-blk","last20games-to","last20games-pf","last20games+/-","last20games-pts",                     
                         "season-scoreDiff","season-position","season-mins","season-fgm","season-fga","season-3pm","season-3pa",
                         "season-ftm","season-fta","season-dreb","season-oreb","season-reb",
                         "season-ast","season-stl","season-blk","season-to","season-pf","season+/-","season-pts"])
        writer.writerows(testingFeatures)

def generate_labels(statsMap):
    trainingLabelsList = deque([])
    testingLabelsList = deque([])

    for playerid,orderedDict in currentMap.items():
         gameLabels = []

         gamesForPlayer = len(orderedDict)
         count = 0

         for gameid,statList in orderedDict.items():
             if(count != 0):
                 gameLabels = statList[9:] 
                 if(count <= 0.8 * (gamesForPlayer-1)):
                     trainingLabelsList.append(gameLabels)
                 else:
                     testingLabelsList.append(gameLabels)
             count += 1
    return (list(trainingLabelsList), list(testingLabelsList))




#(trainingLabels,testingLabels) = generate_labels(currentMap)
def writeLabelsCSVFiles(trainingLabels,testingLabels):
    with open('TrainingLabels.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["mins","fgm","fga","3pm","3pa","ftm","fta","dreb","oreb","reb",
                         "ast","stl","blk","to","pf","+/-","pts"])
        writer.writerows(trainingLabels)  
    with open('TestingLabels.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["mins","fgm","fga","3pm","3pa","ftm","fta","dreb","oreb","reb",
                         "ast","stl","blk","to","pf","+/-","pts"])
        writer.writerows(testingLabels)  

#f = open("Features.csv","w")
#f.write("playerid,gameid,month,day,year,time,ownTeam,otherTeam,away/home,scoreDiff,position,mins,fgm,fga,3pm,3pa,ftm,fta,dreb,oreb,reb,ast,stl,blk,to,pf,+/-,pts\n")
#f.write(json.dumps(generate_features(currentMap)))
#f.close()

def readCSVFiles():

    trainingFeatures = pd.read_csv("TrainingFeatures.csv")
    trainingFeatures_headers = list(trainingFeatures.columns.values)
    trainingFeatures = trainingFeatures._get_numeric_data()
    trainingFeatures_arr = trainingFeatures.as_matrix()

    testingFeatures = pd.read_csv("TestingFeatures.csv")
    testingFeatures_headers = list(testingFeatures.columns.values)
    testingFeatures = testingFeatures._get_numeric_data()
    testingFeatures_arr = testingFeatures.as_matrix()

    todayFeatures = pd.read_csv("TodayFeatures.csv")
    todayFeatures_headers = list(todayFeatures.columns.values)
    todayFeatures = todayFeatures._get_numeric_data()
    todayFeatures_arr = todayFeatures.as_matrix()

    trainingLabels = pd.read_csv("TrainingLabels.csv")
    trainingLabels_headers = list(trainingLabels.columns.values)
    trainingLabels = trainingLabels._get_numeric_data()
    trainingLabels_arr = trainingLabels.as_matrix()

    testingLabels = pd.read_csv("TestingLabels.csv")
    testingLabels_headers = list(testingLabels.columns.values)
    testingLabels = testingLabels._get_numeric_data()
    testingLabels_arr = testingLabels.as_matrix()

    #print(trainingFeatures_headers)
    #print(trainingFeatures_arr)

    #print(testingFeatures_headers)
    #print(testingFeatures_arr)

    #print(trainingLabels_headers)
    #print(trainingLabels_arr)

    #print(testingLabels_headers)
    #print(testingLabels_arr)

    return (trainingFeatures_arr,trainingLabels_arr,todayFeatures_arr,testingFeatures_arr,testingLabels_arr)



def write_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr):

    #svr = svm.SVR()


    #TODO
    #find r2score for training predictions


    #regr = DecisionTreeRegressor(max_depth=3)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr)
    #print("r2_score 3: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr)))

    #regr = DecisionTreeRegressor(max_depth=2)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr)
    #print("r2_score 2: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr)))

    #regr = DecisionTreeRegressor(max_depth=1)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr)
    #print("r2_score 1: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr)))


    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,0])
    #print("r2_score mins: %f" % r2_score(testingLabels_arr[:,0],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,1])
    #print("r2_score fgm: %f" % r2_score(testingLabels_arr[:,1],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,2])
    #print("r2_score fga: %f" % r2_score(testingLabels_arr[:,2],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,3])
    #print("r2_score 3pm: %f" % r2_score(testingLabels_arr[:,3],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,4])
    #print("r2_score 3pa: %f" % r2_score(testingLabels_arr[:,4],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,5])
    #print("r2_score ftm: %f" % r2_score(testingLabels_arr[:,5],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,6])
    #print("r2_score fta: %f" % r2_score(testingLabels_arr[:,6],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,7])
    #print("r2_score dreb: %f" % r2_score(testingLabels_arr[:,7],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,8])
    #print("r2_score oreb: %f" % r2_score(testingLabels_arr[:,8],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,9])
    #print("r2_score reb: %f" % r2_score(testingLabels_arr[:,9],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,10])
    #print("r2_score ast: %f" % r2_score(testingLabels_arr[:,10],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,11])
    #print("r2_score stl: %f" % r2_score(testingLabels_arr[:,11],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,12])
    #print("r2_score blk: %f" % r2_score(testingLabels_arr[:,12],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,13])
    #print("r2_score to: %f" % r2_score(testingLabels_arr[:,13],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,14])
    #print("r2_score pf: %f" % r2_score(testingLabels_arr[:,14],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,15])
    #print("r2_score +/-: %f" % r2_score(testingLabels_arr[:,15],regr.predict(testingFeatures_arr)))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,16])
    #print("r2_score pts: %f" % r2_score(testingLabels_arr[:,16],regr.predict(testingFeatures_arr)))


    regr = ElasticNet()
    regr.fit(np.vstack((trainingFeatures_arr,testingFeatures_arr)),np.vstack((trainingLabels_arr,testingLabels_arr)))
    #print(regr.predict(todayFeatures_arr))

    preds = regr.predict(todayFeatures_arr)
    today = datetime.date.today()
    todayStr = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
    with open("PredictedToday.csv","w",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["mins","fgm","fga","3pm","3pa","ftm","fta","dreb","oreb","reb",
                         "ast","stl","blk","to","pf","+/-","pts"])
        #writer.writerow(["Last Updated: " + todayStr, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
        writer.writerows(preds)



    #n_iter_search = 50
    #param_dist = {"max_depth":sp_randint(1,11)}

    #rand_search = RandomizedSearchCV(tree,param_distributions = param_dist,n_iter=n_iter_search)

    #rand_search.fit(trainingFeatures_arr,trainingLabels_arr)
    #report(rand_search.grid_scores_)


    #with open('PredictedTestVals.csv', 'w', newline='') as csvfile:
    #    writer = csv.writer(csvfile)
    #    writer.writerow(["mins","fgm","fga","3pm","3pa","ftm","fta","dreb","oreb","reb",
    #                     "ast","stl","blk","to","pf","+/-","pts"])
    #    writer.writerows(regr.predict(testingFeatures_arr))

    #testPreds = pd.read_csv('PredictedTestVals.csv')
    #testPreds_headers = list(trainingLabels.columns.values)
    #testPreds_arr = testPreds._get_numeric_data().as_matrix()

    #print(testPreds_headers)
    #print(testPreds_arr)


    #elasticnet = ElasticNet()
    #lasso = Lasso()
    #ridge = Ridge()

    #elasticnet.fit(trainingFeatures_arr,trainingLabels_arr)
    #lasso.fit(trainingFeatures_arr,trainingLabels_arr)
    #ridge.fit(trainingFeatures_arr,trainingLabels_arr)

    #print("r2_score EN: %f" % r2_score(testingLabels_arr,elasticnet.fit(trainingFeatures,trainingLabels).predict(testingFeatures)))
    #print("r2_score Ridge: %f" % r2_score(testingLabels_arr,ridge.fit(trainingFeatures,trainingLabels).predict(testingFeatures)))
    #print("r2_score Lasso: %f" % r2_score(testingLabels_arr,lasso.fit(trainingFeatures,trainingLabels).predict(testingFeatures)))

    #print(elasticNet.get_params())



def readPredsFile():
    todayPreds = pd.read_csv("PredictedToday.csv")
    #todayPreds_headers = list(todayPreds.columns.values)
    todayPreds = todayPreds._get_numeric_data()
    todayPreds_arr = todayPreds.as_matrix()
    return todayPreds_arr

def extract_playerIDS(todayList):
    return [item[0] for item in todayList]

def playerid_to_playerName(playerid):
    if(playerid in playerIDDict):
        return playerIDDict[playerid]
    else:
        #print(str(playerid))
        playerPage = requests.get("http://espn.go.com/nba/player/_/id/" + str(playerid))
        playerTree = html.fromstring(playerPage.content)
        [playerName] = playerTree.xpath("//div[@class='mod-content']/*/h1/text() | //div[@class='mod-content']/h1/text()")
        playerIDDict[playerid] = playerName
        return playerName
        
def writePlayerIDDict(dict):
    f = open("PlayerIDMap.txt","w")
    f.write(json.dumps(dict))
    f.close()

def calc_fanduel_points():
    return 0

def description(dict):
    f = open("final.txt","w")
    for playerid, statList in dict.items():
        f.write(playerid_to_playerName(int(playerid)) + ": [" + str(statList[0]) + " mins, " + str(statList[1]) + "/" + str(statList[2]) + " fg, " + str(statList[3]) + "/" +  str(statList[4]) + " 3p, "
                + str(statList[5]) + "/" +  str(statList[6]) + " ft, " + str(statList[7]) + " dreb, " + str(statList[8]) + " oreb, " + str(statList[9]) + " reb, " + str(statList[10]) + " ast, " +
                str(statList[11]) + " stl, " + str(statList[12]) + " blk, " + str(statList[13]) + " TO, " + str(statList[14]) + " PF, " + str(statList[15]) + " +/-, " + str(statList[16]) + " pts]\n")
    f.close()
    writePlayerIDDict(playerIDDict)


#(lastModifiedDate,currentMap) = readPlayerStatsFile()
#today_playerMap = create_todays_playerMap()
##print(today_playerMap)
#gameids = getNewGameIDs()
#currentMap = createPlayerMap(gameids,currentMap)
#writePlayerStats(currentMap)

#(trainingFeatureList,testingFeatureList,todayFeatureList) = generate_features(currentMap,today_playerMap)
##print(todayFeatureList)
#writeFeaturesFiles(trainingFeatureList,testingFeatureList,todayFeatureList)

#(trainingLabelsList,testingLabelsList) = generate_labels(currentMap)
#writeLabelsCSVFiles(trainingLabelsList,testingLabelsList)

(trainingFeatures_arr,trainingLabels_arr,todayFeatures_arr,testingFeatures_arr,testingLabels_arr) = readCSVFiles()
#print(todayFeatures_arr)
today_playerIDS = extract_playerIDS(todayFeatures_arr)
#print(today_playerIDS)

#write_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr)
#print(preds)

preds = readPredsFile()
#preds = [item for sublist in preds for item in sublist]



#print(preds)

dictionary = dict(zip(today_playerIDS, preds))
#print(dictionary)

#print(playerid_to_playerName(2959753))
#print(playerIDDict)

description(dictionary)