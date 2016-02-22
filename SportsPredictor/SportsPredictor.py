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
position_number_dict = { 
        ", PG" : 1,
        "PG" : 1,
        ", SG" : 2,
        "SG" : 2,
        ", SF" : 3,
        "SF" : 3,
        ", PF" : 4,
        "PF" : 4,
        ", C" : 5,
        "C" : 5,
        ", F" : 3.5,
        "F" : 3.5
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

    if(str.split("ET")[1] == ''):
        today = datetime.date.today()
        return [today.month, today.day, today.year, time]
    
    [_,dateStr] = str.split("ET, ")
    [monthDayStr,yearStr] = dateStr.split(", ")
    [monthStr,dayStr] = monthDayStr.split(" ")
    return [monthdict[monthStr], int(dayStr), int(yearStr), time]

#takes weird espn date data and returns info in int categories
#espn has this date data organized pretty terribly
def data_date_convert(str):
    [date,time] = str.split("T")
    [year,month,day] = date.split("-")
    year = int(year)
    month = int(month)
    day = int(day)
    hour = (int(time[0:2]) + 7)
    if(hour > 24):
        hour = hour % 24
    else:
        day = day -1
    min = int(time[3:5])
    time = hour + float(min)/60
    return [int(month),int(day),int(year),time]


    

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
    #print(scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/caption"))
    [date] = scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/caption/text()")
    date = strToDate(date)
    #print(date)

    if(date != datetime.date.today()):
        print("ESPN's schedule page has not updated for today's games")
        #exit()
        [date] = scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=3]/table/caption/text()")
        date = strToDate(date)
        
        todaysGameIDs = [x.split("=")[1] for x in scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=3]/table/tbody/tr/td[position()=3]/a/@href")]
       # todayGameTimes = [x+" ET" for x in scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=3]/table/tbody/tr/td[position()=3]/a//text()")]
        if(date != datetime.date.today()):
            print("Actually Exiting")
            exit()
    else:
        todaysGameIDs = [x.split("=")[1] for x in scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/tbody/tr/td[position()=3]/a/@href")]


    #FIX!!!

    for gameid in todaysGameIDs:
        #print("gameid %d" % int(gameid))
        gameBoxScoreURL = "http://espn.go.com/nba/conversation?gameId=" + gameid
        #print(gameBoxScoreURL)
        boxScorePage = requests.get(gameBoxScoreURL)
        boxScoreTree = html.fromstring(boxScorePage.content)


        #first get game data not specific to each player (time,date,score,team numbers etc)
        gameDataList = []
        #print(boxScoreTree.xpath("//span/text()"))
        game_time_info = boxScoreTree.xpath("//div[@class='game-status']/span[position()=2]/@data-date")[0]
        #print(game_time_info)
        [m,d,y,t] = data_date_convert(game_time_info)

    
        #[awayTeamName] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=1]/div[@class='team-info']/h3/a/text()")
        #[homeTeamName] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=2]/div[@class='team-info']/h3/a/text()")

        #print(boxScoreTree.xpath("//div[@class='competitors']/*"))

        [awayTeamName] = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team away']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")
        [homeTeamName] = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team home']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")

        #print(awayTeamName)
        #print(homeTeamName)


        [awayTeamURL] = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team away']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/@href")
        #print(awayTeamName)
        [a,b]=awayTeamURL.split("_")
        awayRosterURL = a + "roster/_" + b
        awayRosterPage = requests.get("http://espn.go.com" + awayRosterURL)
        awayRosterTree = html.fromstring(awayRosterPage.content)
        awayPlayeridList = [x.split("player-46-")[1] for x in awayRosterTree.xpath("//tr[contains(@class,'player-46')]/@class")]
        #print(awayRosterURL)

        for playerid in awayPlayeridList:
            today_playerMap[playerid][gameid] = [m,d,y,t,team_dict[awayTeamName],team_dict[homeTeamName],0]

    
        [homeTeamURL] = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team home']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/@href")
        #print(homeTeamURL)
        [a,b]=homeTeamURL.split("_")
        homeRosterURL = a + "roster/_" + b
        #print(homeRosterURL)
        homeRosterPage = requests.get("http://espn.go.com" + homeRosterURL)
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

    if("COACH'S DECISION" in statsList[1]):
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
    ftm = int(ftmstr)
    fta = int(ftastr)

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
        gameBoxScoreURL = "http://espn.go.com/nba/boxscore?gameId=" + gameid
        boxScorePage = requests.get(gameBoxScoreURL)
        boxScoreTree = html.fromstring(boxScorePage.content)

        gameInfoURL = "http://espn.go.com/nba/game?gameId=" + gameid
        gameInfoPage = requests.get(gameInfoURL)
        gameInfoTree = html.fromstring(gameInfoPage.content)

        #first get game data not specific to each player (time,date,score,team numbers etc)
        gameDataList = []
        #print(gameid)

        try:
            #game_time_info = boxScoreTree.xpath("//div[@class='game-time-location']/p/text()")[0] OLD ESPN
            game_time_info = gameInfoTree.xpath("//div[@class='game-date-time']/span/@data-date")[0]
            #print(game_time_info)

            #[awayName,awayScore] = boxScoreTree.xpath("//div[@class='team away']/div/h3/*/text()") OLD ESPN
            #[homeName,homeScore] = boxScoreTree.xpath("//div[@class='team home']/div/h3/*/text()") OLD ESPN

            [awayName] = boxScoreTree.xpath("//div[@class='team away']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")
            [homeName] = boxScoreTree.xpath("//div[@class='team home']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")

            [awayScore] = boxScoreTree.xpath("//div[@class='team away']/div[@class='content']/div[@class='score-container']/div/text()")
            [homeScore] = boxScoreTree.xpath("//div[@class='team home']/div[@class='content']/div[@class='score-container']/div/text()")

            scoreDifference = int(awayScore) - int(homeScore)
            #print(scoreDifference)
            #print(awayName)
            #print(homeName)


            #keep track of which players were on the away team and which were on the home team
            #[awayTeam] = boxScoreTree.xpath("//table/thead[position()=1]/tr[@class='team-color-strip']/th/text()")
            awayTeamNum = team_dict[awayName]
            #awayPlayeridList = boxScoreTree.xpath("//table/tbody[position()=1 or position()=2]/tr[contains(@class,'player-46')]/@class") OLD ESPN
            #awayPlayeridList = [x.split("player-46-")[1] for x in awayPlayeridList]


            
            awayPlayerURLList = boxScoreTree.xpath("//div[@class='col column-one gamepackage-away-wrap']/div[@class='sub-module']/div[@class='content']/table/tbody/tr/td/a/@href")
            awayPlayeridList = [x.split("_/id/")[1] for x in awayPlayerURLList]
            #print(awayPlayeridList)

           # [homeTeam] = boxScoreTree.xpath("//table/thead[position()=4]/tr[@class='team-color-strip']/th/text()")
            homeTeamNum = team_dict[homeName]
            #homePlayeridList = boxScoreTree.xpath("//table/tbody[position()=4 or position()=5]/tr[contains(@class,'player-46')]/@class")
            #homePlayeridList = [x.split("player-46-")[1] for x in homePlayeridList]

            homePlayerURLList = boxScoreTree.xpath("//div[@class='col column-two gamepackage-home-wrap']/div[@class='sub-module']/div[@class='content']/table/tbody/tr/td/a/@href")
            homePlayeridList = [x.split("_/id/")[1] for x in homePlayerURLList]
           # print(homePlayeridList)


            #gets player stats for away players and appends that to the game stats
            for playerid in awayPlayeridList:
                xPathStatsString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/*/text()"
               

                xPathPositionString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/td/*/text()"
                #print(xPathPositionString)

                gameStatsList = []
                # stores own team's number and also the opposing team's number
                # 0 for away team and score difference is calc away score - home score
                gameStatsList += data_date_convert(game_time_info) + [awayTeamNum, homeTeamNum] + [0,scoreDifference] 
        
 
                playerStatsList = [boxScoreTree.xpath(xPathPositionString)[1]] + boxScoreTree.xpath(xPathStatsString)
                
                #print(playerStatsList)

                if("DNP" not in playerStatsList[1] or "COACH'S DECISION" in playerStatsList[1]):
       
                
                    playerStatsList = playerStatsConvert(playerStatsList)
                   # print(playerStatsList)
                   # playerMap[playerid].append(gameid)
                   # print(gameStatsList+playerStatsList)
        
                    playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
                    #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})

                else:
                    print(playerid + " is injured, so stats from game will not count")
        

            #gets player stats for home players and appends that to the game stats
            for playerid in homePlayeridList:
                xPathStatsString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/*/text()"
               

                xPathPositionString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/td/*/text()"
                #print(xPathPositionString)

                gameStatsList = []
        
                # stores own team's number and also the opposing team's number
                # 1 for home team and score difference is calc away score - home score
                gameStatsList += data_date_convert(game_time_info) + [homeTeamNum, awayTeamNum] + [1, -1 * scoreDifference]

                playerStatsList = [boxScoreTree.xpath(xPathPositionString)[1]] + boxScoreTree.xpath(xPathStatsString)

                if("DNP" not in playerStatsList[1] or "DNP COACH'S DECISION" in playerStatsList[1]):

                
                    playerStatsList = playerStatsConvert(playerStatsList)
                   # print(playerStatsList)
                   # playerMap[playerid].append(gameid)

                    playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
                    #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})
        except (IndexError):
            print("Game " + gameid + " does not exist")
    print(playerMap)

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

     return (np.array(list(trainingFeatureList)),np.array(list(testingFeatureList)), np.array(list(todayFeatureList)))



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
    return (np.array(list(trainingLabelsList)), np.array(list(testingLabelsList)))




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



def create_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr):

    #svr = svm.SVR()

    #print(trainingFeatures_arr)
    #print(trainingFeatures_arr.shape)
    #print(trainingLabels_arr.shape)
    #print(trainingLabels_arr)

    

    regr = DecisionTreeRegressor(max_depth=6)
    regr.fit(trainingFeatures_arr,trainingLabels_arr)
    print("r2_score 6: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))



    minsPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,0])
    r2score1 = r2_score(testingLabels_arr[:,0],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,0])
    r2score2 = r2_score(testingLabels_arr[:,0],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score mins: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,0])
        minsPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score mins: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,0])
        minsPreds = regr2.predict(todayFeatures_arr)
    #print(minsPreds)

    
    
    fgmPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,1])
    r2score1 = r2_score(testingLabels_arr[:,1],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,1])
    r2score2 = r2_score(testingLabels_arr[:,1],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score fgm: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,1])
        fgmPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score fgm: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,1])
        fgmPreds = regr2.predict(todayFeatures_arr)
    #print(fgmPreds)




    
    
    fgaPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,2])
    r2score1 = r2_score(testingLabels_arr[:,2],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,2])
    r2score2 = r2_score(testingLabels_arr[:,2],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score fga: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,2])
        fgaPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score fga: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,2])
        fgaPreds = regr2.predict(todayFeatures_arr)
    #print(fgaPreds)


    tpmPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,3])
    r2score1 = r2_score(testingLabels_arr[:,3],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,3])
    r2score2 = r2_score(testingLabels_arr[:,3],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score 3pm: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,3])
        tpmPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score 3pm: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,3])
        tpmPreds = regr2.predict(todayFeatures_arr)
    #print(tpmPreds)


    tpaPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,4])
    r2score1 = r2_score(testingLabels_arr[:,4],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,4])
    r2score2 = r2_score(testingLabels_arr[:,4],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score 3pa: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,4])
        tpaPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score 3pa: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,4])
        tpaPreds = regr2.predict(todayFeatures_arr)
    #print(tpaPreds)


    
    ftmPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,5])
    r2score1 = r2_score(testingLabels_arr[:,5],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,5])
    r2score2 = r2_score(testingLabels_arr[:,5],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score ftm: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,5])
        ftmPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score ftm: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,5])
        ftmPreds = regr2.predict(todayFeatures_arr)
    #print(ftmPreds)




    ftaPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,6])
    r2score1 = r2_score(testingLabels_arr[:,6],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,6])
    r2score2 = r2_score(testingLabels_arr[:,6],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score fta: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,6])
        ftaPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score fta: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,6])
        ftaPreds = regr2.predict(todayFeatures_arr)
    #print(ftaPreds)

    

    drebPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,7])
    r2score1 = r2_score(testingLabels_arr[:,7],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,7])
    r2score2 = r2_score(testingLabels_arr[:,7],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score dreb: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,7])
        drebPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score dreb: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,7])
        drebPreds = regr2.predict(todayFeatures_arr)
    #print(drebPreds)


        

    orebPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,8])
    r2score1 = r2_score(testingLabels_arr[:,8],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,8])
    r2score2 = r2_score(testingLabels_arr[:,8],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score oreb: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,8])
        orebPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score oreb: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,8])
        orebPreds = regr2.predict(todayFeatures_arr)
    #print(orebPreds)



    rebPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,9])
    r2score1 = r2_score(testingLabels_arr[:,9],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,9])
    r2score2 = r2_score(testingLabels_arr[:,9],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score reb: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,9])
        rebPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score oreb: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,9])
        rebPreds = regr2.predict(todayFeatures_arr)
    #print(rebPreds)


    astPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,10])
    r2score1 = r2_score(testingLabels_arr[:,10],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,10])
    r2score2 = r2_score(testingLabels_arr[:,10],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score ast: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,10])
        astPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score ast: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,10])
        astPreds = regr2.predict(todayFeatures_arr)
    #print(astPreds)


    stlPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,11])
    r2score1 = r2_score(testingLabels_arr[:,11],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,11])
    r2score2 = r2_score(testingLabels_arr[:,11],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score stl: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,11])
        stlPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score stl: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,11])
        stlPreds = regr2.predict(todayFeatures_arr)
    #print(stlPreds)


    
    blkPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,12])
    r2score1 = r2_score(testingLabels_arr[:,12],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,12])
    r2score2 = r2_score(testingLabels_arr[:,12],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score blk: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,12])
        blkPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score blk: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,12])
        blkPreds = regr2.predict(todayFeatures_arr)
    #print(blkPreds)


        
    toPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,13])
    r2score1 = r2_score(testingLabels_arr[:,13],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,13])
    r2score2 = r2_score(testingLabels_arr[:,13],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score to: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,13])
        toPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score to: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,13])
        toPreds = regr2.predict(todayFeatures_arr)
    #print(toPreds)
           



    pfPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,14])
    r2score1 = r2_score(testingLabels_arr[:,14],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,14])
    r2score2 = r2_score(testingLabels_arr[:,14],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score pf: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,14])
        pfPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score pf: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,14])
        pfPreds = regr2.predict(todayFeatures_arr)
    #print(pfPreds)

    

    pmPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,15])
    r2score1 = r2_score(testingLabels_arr[:,15],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,15])
    r2score2 = r2_score(testingLabels_arr[:,15],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score +/-: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,15])
        pmPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score +/-: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,15])
        pmPreds = regr2.predict(todayFeatures_arr)
    #print(pmPreds)

        

    ptsPreds = []
    regr1 = DecisionTreeRegressor(max_depth=6)
    regr1.fit(trainingFeatures_arr,trainingLabels_arr[:,16])
    r2score1 = r2_score(testingLabels_arr[:,16],regr1.predict(testingFeatures_arr))
    regr2 = ElasticNet()
    regr2.fit(trainingFeatures_arr,trainingLabels_arr[:,16])
    r2score2 = r2_score(testingLabels_arr[:,16],regr2.predict(testingFeatures_arr))
    if(r2score1 > r2score2):
        print("Tree r2_score pts: %f" % r2score1)
        regr1.fit(testingFeatures_arr,testingLabels_arr[:,16])
        ptsPreds = regr1.predict(todayFeatures_arr)
    else:
        print("EN r2_score pts: %f" % r2score2)
        regr2.fit(testingFeatures_arr,testingLabels_arr[:,16])
        ptsPreds = regr2.predict(todayFeatures_arr)
    #print(ptsPreds)


    #regr = DecisionTreeRegressor(max_depth=6)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,16])
    #print("r2_score pts: %f" % r2_score(testingLabels_arr[:,16],regr.predict(testingFeatures_arr)))


    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,0])
    #print("r2_score mins: %f" % r2_score(testingLabels_arr[:,0],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,1])
    #print("r2_score fgm: %f" % r2_score(testingLabels_arr[:,1],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,2])
    #print("r2_score fga: %f" % r2_score(testingLabels_arr[:,2],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,3])
    #print("r2_score 3pm: %f" % r2_score(testingLabels_arr[:,3],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,4])
    #print("r2_score 3pa: %f" % r2_score(testingLabels_arr[:,4],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,5])
    #print("r2_score ftm: %f" % r2_score(testingLabels_arr[:,5],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,6])
    #print("r2_score fta: %f" % r2_score(testingLabels_arr[:,6],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,7])
    #print("r2_score dreb: %f" % r2_score(testingLabels_arr[:,7],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,8])
    #print("r2_score oreb: %f" % r2_score(testingLabels_arr[:,8],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,9])
    #print("r2_score reb: %f" % r2_score(testingLabels_arr[:,9],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,10])
    #print("r2_score ast: %f" % r2_score(testingLabels_arr[:,10],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,11])
    #print("r2_score stl: %f" % r2_score(testingLabels_arr[:,11],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,12])
    #print("r2_score blk: %f" % r2_score(testingLabels_arr[:,12],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,13])
    #print("r2_score to: %f" % r2_score(testingLabels_arr[:,13],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,14])
    #print("r2_score pf: %f" % r2_score(testingLabels_arr[:,14],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,15])
    #print("r2_score +/-: %f" % r2_score(testingLabels_arr[:,15],regr.predict(testingFeatures_arr)))

    #regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=2),n_estimators=300)
    #regr.fit(trainingFeatures_arr,trainingLabels_arr[:,16])
    #print("r2_score pts: %f" % r2_score(testingLabels_arr[:,16],regr.predict(testingFeatures_arr)))

    #print(minsPreds.shape)
    #print(fgmPreds.shape)
    #print(fgaPreds.shape)
    #print(tpmPreds.shape)
    #print(tpaPreds.shape)
    #print(ftmPreds.shape)
    #print(ftaPreds.shape)
    #print(drebPreds.shape)
    #print(orebPreds.shape)
    #print(rebPreds.shape)
    #print(astPreds.shape)
    #print(stlPreds.shape)
    #print(blkPreds.shape)
    #print(toPreds.shape)
    #print(pfPreds.shape)
    #print(pmPreds.shape)
    #print(ptsPreds.shape)

    stacked = np.vstack((minsPreds,fgmPreds,fgaPreds,tpmPreds,tpaPreds,ftmPreds,ftaPreds,drebPreds,orebPreds,rebPreds,astPreds,stlPreds,blkPreds,toPreds,pfPreds,pmPreds,ptsPreds))
    print(stacked.shape)

    preds = stacked.T
    #print(preds.shape)


    #regr = ElasticNet()
    #regr.fit(np.vstack((trainingFeatures_arr,testingFeatures_arr)),np.vstack((trainingLabels_arr,testingLabels_arr)))
    #print("1: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))

    #regr = ElasticNet()
    #regr.fit(trainingFeatures_arr,trainingLabels_arr)
    #regr.fit(testingFeatures_arr,testingLabels_arr)
    #print("2: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))

    #regr = DecisionTreeRegressor(max_depth=6)
    #regr.fit(np.vstack((trainingFeatures_arr,testingFeatures_arr)),np.vstack((trainingLabels_arr,testingLabels_arr)))
    ##regr.fit(trainingFeatures_arr,trainingLabels_arr)
    ##print(regr.predict(todayFeatures_arr))

    ##print("ElasticNet r2 score is %f" % r2_score( regr.predict(testingFeatures_arr),testingLabels_arr))

    #preds = regr.predict(todayFeatures_arr)

    #print(preds.shape)
 

    return preds


def write_preds(preds):
    with open("PredictedToday.csv","w",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["mins","fgm","fga","3pm","3pa","ftm","fta","dreb","oreb","reb",
                         "ast","stl","blk","to","pf","+/-","pts"])
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
        #print(playerid)
        
        try:
            [playerName] = playerTree.xpath("//div[@class='mod-content']/*/h1/text() | //div[@class='mod-content']/h1/text()")
        except (IndexError):
            print("Player " + playerid + " causes error")


        playerIDDict[playerid] = playerName
        return playerName
        
def writePlayerIDDict(dict):
    f = open("PlayerIDMap.txt","w")
    f.write(json.dumps(dict))
    f.close()

def calc_fanduel_points(statList):
    return (statList[1] - statList[3]) * 2 + statList[3] * 3 + statList[5] * 1 + statList[9] * 1.2 + statList[10] * 1.5 + statList[11] * 2 + statList[12] * 2 + statList[13] * -1

def gen_description_and_fanduel_map(dict,csvFileName):
    playerList = []

    f = open("final.txt","w")
    fanduel_data_arr = fanduel_scrape(csvFileName)
    
    for playerid, statList in dict.items():
        name = playerid_to_playerName(int(playerid))
        #print(name)
        
        if(name in fanduel_data_arr["Name"].as_matrix()):
            [row] = fanduel_data_arr.loc[fanduel_data_arr['Name'] == name].as_matrix()
            position = row[1]
            fanduelAvg = row[4]
            cost = row[6]
            injured = row[10]

            predicted = calc_fanduel_points(statList)
            
            
            #print(row)
            f.write( name + ": [" + "{0:.2f}".format(statList[0]) + " mins, " + "{0:.2f}".format(statList[1]) + "/" + 
                    "{0:.2f}".format(statList[2]) + " fg, " + "{0:.2f}".format(statList[3]) + "/" +  "{0:.2f}".format(statList[4]) + " 3p, "
                    + "{0:.2f}".format(statList[5]) + "/" +  "{0:.2f}".format(statList[6]) + " ft, " + "{0:.2f}".format(statList[7]) + " dreb, " + 
                    "{0:.2f}".format(statList[8]) + " oreb, " + "{0:.2f}".format(statList[9]) + " reb, " + "{0:.2f}".format(statList[10]) + " ast, " +
                    "{0:.2f}".format(statList[11]) + " stl, " + "{0:.2f}".format(statList[12]) + " blk, " + "{0:.2f}".format(statList[13]) + " TO, " + 
                    "{0:.2f}".format(statList[14]) + " PF, " + "{0:.2f}".format(statList[15]) + " +/-, " + "{0:.2f}".format(statList[16]) + " pts] FANDUEL: " 
                    + "{0:.2f}".format(predicted) + ", " + position + ", " + str(cost) + ", " + "{0:.2f}".format(fanduelAvg) + "\n")

            if(injured != "GTD" and injured != "O"):
                playerList.append([position, predicted, cost,name])

    f.close()
    writePlayerIDDict(playerIDDict)



    return playerList


def write_playerList(playerList):
    with open("playerlist.txt","w") as f:
        f.write(json.dumps(playerList))


def fanduel_scrape(csvFile):

    #TEMPORARY UNTIL I FIGURE OUT HOW TO SCRAPE FANDUEL PROPERLY

    fanduel_data = pd.read_csv(csvFile)
    fanduel_data_headers = list(fanduel_data.columns.values)
    #fanduel_data = fanduel_data._get_numeric_data()
    fanduel_data["Name"] = (fanduel_data["First Name"] + " " + fanduel_data["Last Name"])
   # fanduel_data.drop(fanduel_data.columns[[2,3]],axis=1)
    #fanduel_data.drop("Last Name",axis=1)
    #fanduel_data_arr = fanduel_data.as_matrix()#[:,:12]

    
   # print(fanduel_data_arr)

    return fanduel_data

def cutOut(positionList):
    for i in positionList[::-1]:
        for j in positionList[::-1]:
            if(i==j):
                continue
            #i is projected to score more and costs less
            #print(str(i) + ", " + str(j))
            if(i[1] > j[1] and i[2] <= j[2]):
                #print(str(i[3]) + " dominates " + str(j[3]) + "(payoff " + str(i[1]) + " > " + str(j[1]) + " and cost " + str(i[2]) + " <= " + str(j[2]))
                positionList.remove(j)
    return positionList #[a for a in positionList for b in positionList if a != b and not (a[1]>b[1] and a[2]<=b[2])]

def pairSame(positionList):
    pairedList = [[(a[0],b[0]),(a[1],b[1]),(a[2],b[2]),(a[3],b[3]),a[1]+b[1],a[2]+b[2]] for a in positionList for b in positionList if a != b]
    for i in pairedList[::-1]:
        for j in pairedList[::-1]:
            if(i==j):
                continue
            #i is projected to score more and costs less
            #goal of this is to remove the dominated players
            if(i[4] > j[4] and i[5] <= j[5]):
                pairedList.remove(j)
         
    return pairedList #[a for a in pairedList for b in pairedList if a != b and not (a[4]>b[4] and a[5]<=b[5])]

def pairDifferentFilter(positionList1,positionList2,totalSalary):
    pairedList = [[a[0]+b[0],a[1]+b[1],a[2]+b[2],a[3]+b[3],a[4]+b[4],a[5]+b[5]] for a in positionList1 for b in positionList2 if a[5] + b[5] <= totalSalary]
    #print("done matching")
    for i in pairedList[::-1]:
        for j in pairedList[::-1]:
            if(i==j):
                continue
            #i is projected to score more and costs less
            if(i[4] > j[4] and i[5] <= j[5]):
                pairedList.remove(j)
         
    return pairedList #[a for a in pairedList for b in pairedList if a != b and not (a[4]>b[4] and a[5]<=b[5])]

def combineDifferentNoFilter(positionList1,positionList2,positionList3,totalSalary):
    pairedList = [[a[0]+b[0]+c[0],a[1]+b[1]+c[1],a[2]+b[2]+c[2],a[3]+b[3]+c[3],a[4]+b[4]+c[4],a[5]+b[5]+c[5]] for a in positionList1 for b in positionList2 for c in positionList3 if a[5] + b[5] + c[5] <= totalSalary]
    #print("done matching")
    return pairedList

def formatCenters(centers):
    return [[(item[0],),(item[1],),(item[2],),(item[3],),item[1],item[2]] for item in centers]

def optimize(predsList,totalSalary):

    #position caps are 2 PG, 2 SG, 2 SF, 2 PF, 1 C

    pgs = [item for item in predsList if item[0] == "PG"]
    sgs = [item for item in predsList if item[0] == "SG"]
    sfs = [item for item in predsList if item[0] == "SF"]
    pfs = [item for item in predsList if item[0] == "PF"]
    cs = [item for item in predsList if item[0] == "C"]



    pgs = cutOut(pgs)
    sgs = cutOut(sgs)
    sfs = cutOut(sfs)
    pfs = cutOut(pfs)
    cs = cutOut(cs)






    #print(len(cs))

    pgs = pairSame(pgs)
    sgs = pairSame(sgs)
    sfs = pairSame(sfs)
    pfs = pairSame(pfs)
    cs = formatCenters(cs)


    guards = pairDifferentFilter(pgs,sgs,totalSalary)
    print("Paired Guards")


    forwards = pairDifferentFilter(sfs,pfs,totalSalary)
    print("Paired Forwards")
   

    all_players = combineDifferentNoFilter(guards,forwards,cs,totalSalary)
    print("Generated All Reasonable Combinations. Going to find best one now.")

    optimal = max(all_players, key=lambda x: x[4])

    #print(optimal)


    return optimal







    #brute force WAY too slow
    #maxList = []
    #maxPoints = 0

    #for pg1 in pgs:
    #    #cost1 = pg1[2]
    #    #sum1 = pg1[1]
    #    for pg2 in pgs:
    #        if(pg1 == pg2):
    #            continue
    #        #cost2 = cost1 + pg2[2]
    #        #sum2 = sum1 + pg2[1]
    #        for sg1 in sgs:
    #            #cost3 = cost2 + sg1[2]
    #            #sum3 = sum2 + sg1[1]
    #            for sg2 in sgs:
    #                if(sg1 == sg2):
    #                    continue
    #                #cost4 = cost3 + sg2[2]
    #                #sum4 = cost3 + sg2[1]
    #                for sf1 in sfs:
    #                    #cost5 = cost4 + sf1[2]
    #                    #sum5 = sum4 + sf1[1]
    #                    #if (cost5>totalSalary):
    #                    #    continue
    #                    for sf2 in sfs:
    #                        #cost6 = cost5 + sf2[2]
    #                        #sum6 = sum5 + sf2[1]
    #                        #if (sf1 == sf2 or cost6>totalSalary):
    #                        #    continue
    #                        if(sf1 == sf2):
    #                            continue
    #                        for pf1 in pfs:
    #                            #cost7 = cost6 + pf1[2]
    #                            #sum7 = sum6 + pf1[1]
    #                            #if (cost7>totalSalary):
    #                            #    continue
    #                            for pf2 in pfs:
    #                                #cost8 = cost7 + pf2[2]
    #                                #sum8 = sum7 + pf2[1]
    #                                #if (cost8>totalSalary or pf1 == pf2):
    #                                #    continue
    #                                if(pf1 == pf2):
    #                                    continue
    #                                for c in cs:
    #                                    cost = pg1[2]+pg2[2]+sg1[2]+sg2[2]+sf1[2]+sf2[2]+pf1[2]+pf2[2]+c[2]
    #                                    if (cost>totalSalary):
    #                                        continue
    #                                    sum = pg1[1]+pg2[1]+sg1[1]+sg2[1]+sf1[1]+sf2[1]+pf1[1]+pf2[1]+c[1]
    #                                    if(sum > maxPoints):
    #                                        print("Current Max Points is %f" %sum)
    #                                        maxPoints = sum
    #                                        maxList = [pg1[1],pg2[1],sg1[1],sg2[1],sf1[1],sf2[1],pf1[1],pf2[1],c[1], cost,sum]
    #                                        #print(maxList)
    #return maxList


    #payload = { "email" : "amcire96@gmail.com",
    #           "password" : "kathy_ma",
    #           "cc_session_id" : "sa2s9a83e7f9mq3jtldma09bu1" ,
    #           "cc_action" : "cca_login",
    #           "cc_success_url" : "/games"}

    #with requests.Session() as s:
    #    p = s.post("https://www.fanduel.com/c/CCAuth", data = payload)
    #    print(p.text)

    #r = requests.get("https://www.fanduel.com/games",auth=("amcire96@gmail.com","kathy_ma"))
    #print(r.text)


    #homePage = requests.get("https://www.fanduel.com/games")
    #homeTree = html.fromstring(homePage.content)
    ##firstContestID = homeTree.xpath("//table[@class='contest-list']/tbody/tr[position()=1]/td[@class='enter-contest-cell']/a/@href")
    #firstContestID = homeTree.xpath("//*")
    #print(firstContestID)

    #[a,_] = contestID.split("-")
    #url = "https://www.fanduel.com/games/" + a + "/contests/" + contestID + "/enter"

    #contestPage = requests.get(url)
    #contestTree = html.fromstring(contestPage.content)
    #playerlist = contestTree.xpath("//table/*")
    ##print(playerlist)

    #print(contestTree)





def readPlayerList():
    playerList = []
    with open("playerlist.txt","r") as f:
        playerList = json.loads(f.readline())
    return playerList










#def getPlayerList(contestID):
#    [a,_] = contestID.split("-")
#    url = "https://www.fanduel.com/games/" + a + "/contests/" + contestID + "/enter"

#    contestPage = requests.get(url)
#    contestTree = html.fromstring(contestPage.content)
#    playerlist = contestTree.xpath("//body/*")
#    print(playerlist)

    #print(contestTree)



def format_print(resultList):
    print(resultList[0][0] + "1: " + resultList[3][0] + " with projected " + "{0:.2f}".format(resultList[1][0]) + " points and " + str(resultList[2][0]) + " cost.")
    print(resultList[0][1] + "2: " + resultList[3][1] + " with projected " + "{0:.2f}".format(resultList[1][1]) + " points and " + str(resultList[2][1]) + " cost.")
    print(resultList[0][2] + "1: " + resultList[3][2] + " with projected " + "{0:.2f}".format(resultList[1][2]) + " points and " + str(resultList[2][2]) + " cost.")
    print(resultList[0][3] + "2: " + resultList[3][3] + " with projected " + "{0:.2f}".format(resultList[1][3]) + " points and " + str(resultList[2][3]) + " cost.")
    print(resultList[0][4] + "1: " + resultList[3][4] + " with projected " + "{0:.2f}".format(resultList[1][4]) + " points and " + str(resultList[2][4]) + " cost.")
    print(resultList[0][5] + "2: " + resultList[3][5] + " with projected " + "{0:.2f}".format(resultList[1][5]) + " points and " + str(resultList[2][5]) + " cost.")
    print(resultList[0][6] + "1: " + resultList[3][6] + " with projected " + "{0:.2f}".format(resultList[1][6]) + " points and " + str(resultList[2][6]) + " cost.")
    print(resultList[0][7] + "2: " + resultList[3][7] + " with projected " + "{0:.2f}".format(resultList[1][7]) + " points and " + str(resultList[2][7]) + " cost.")
    print(resultList[0][8] + ": " + resultList[3][8] + " with projected " + "{0:.2f}".format(resultList[1][8]) + " points and " + str(resultList[2][8]) + " cost.")
    print("Total projected points is " + "{0:.2f}".format(resultList[4]))
    print("Total cost is " + str(resultList[5]))




print("Reading previously stored player-stats map")
(lastModifiedDate,currentMap) = readPlayerStatsFile()
isUpdated = (lastModifiedDate == datetime.date.today())

print("Getting data about players playing today")
today_playerMap = create_todays_playerMap()

if(not isUpdated):
    gameids = getNewGameIDs()
    currentMap = createPlayerMap(gameids,currentMap)
    writePlayerStats(currentMap)
    print("Done creating and writing Player Map")
else:
    print("PlayerMap is already updated, so not creating new PlayerMap")


if(not isUpdated):
    (trainingFeatures_arr,testingFeatures_arr,todayFeatures_arr) = generate_features(currentMap,today_playerMap)
    writeFeaturesFiles(trainingFeatures_arr,testingFeatures_arr,todayFeatures_arr)

    (trainingLabels_arr,testingLabels_arr) = generate_labels(currentMap)
    writeLabelsCSVFiles(trainingLabels_arr,testingLabels_arr)

    print("Done generating features and labels")
else:
    (trainingFeatures_arr,trainingLabels_arr,todayFeatures_arr,testingFeatures_arr,testingLabels_arr) = readCSVFiles()
    print("Features and Labels are already updated -- just reading those files now, so not creating new ones")



today_playerIDS = extract_playerIDS(todayFeatures_arr)

if(not isUpdated):
    preds = create_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr)
    write_preds(preds)
    print("Done making predictions about players playing today")
else:
    preds = readPredsFile()
    print("Predictions are already updated -- just reading predictions file now, so not creating new ones")



#WAS GOING TO SKIP IF ALREADY UPDATED BUT BEST TO GIVE USER THE OPTION OF SPECIFYING ANOTHER TOURNAMENT TODAY
#don't need to write/read file then
dictionary = dict(zip(today_playerIDS, preds))

print("------------------------------------------------------------------------------------------------------------------")
print("INSTRUCTIONS: Go to Fanduel's website, sign in, go to an NBA contest page and download the players' stats CSV file")

csvFileName = str(input("What is the absolute or relative path of this CSV file?\n"))
totalSalary = int(input("What is the total salary of this contest?\n"))
print("------------------------------------------------------------------------------------------------------------------")

print("Combining Fanduel Data with Predicted Data")

playerList = gen_description_and_fanduel_map(dictionary,csvFileName)

#write_playerList(playerList)

print("Done using Fanduel Data and now optimizing to find best predicted line-up")

#playerList = readPlayerList()
    

result = optimize(playerList,totalSalary)

format_print(result)






#IDK IF I AM GOING TO KEEP WORKING ON SCRAPING FANDUEL
#IT SEEMS DIFFICULT / AGAINST THE TERMS OF SERVICE
#getPlayerList("14619-22471320")
#fanduel_scrape("FanDuel-NBA-2016-02-03-14597-players-list.csv")


#(trainingFeatures_arr,trainingLabels_arr,todayFeatures_arr,testingFeatures_arr,testingLabels_arr) = readCSVFiles()
#preds = create_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr)
#write_preds(preds)