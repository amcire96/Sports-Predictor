
from lxml import html
import requests
import datetime
import numpy as np
import pandas as pd

from nameparser import HumanName

import ReadWriteFiles
import Scraper


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

    dateGame = datetime.date(year,month,day)

    hour = (int(time[0:2]) + 7)
    if(hour > 24):
        hour = hour % 24
    else:
        dateGame = dateGame - datetime.timedelta(days = 1)
    min = int(time[3:5])
    time = hour + float(min)/60
    return [int(dateGame.month),int(dateGame.day),int(dateGame.year),time]



def extractNewGameIDs(gameidsList,dateList,lastModifiedDate):
    #print(gameidsList)
    #print(dateList)
    #print(lastModifiedDate)
    #i=0
    for i in range(0,len(dateList)):
        
        dateStr = dateList[i]
        date = strToDate(dateStr)
       # print(date)
        #print(lastModifiedDate)
        if(lastModifiedDate <= date):
            #print(date)
            break
    #print(str(i))
    if(lastModifiedDate > strToDate(dateList[i])):
        return ([],[])
    #eprint(dateList[i:])
    return (gameidsList[i:],[strToDate(x) for x in dateList[i:]])








#takes list of string statistics and converts to numbers
def playerStatsConvert(statsList):

    #print(statsList)
    
    positionNum = position_number_dict[statsList[0]]

    if("COACH'S DECISION" in statsList[1] or "--" in statsList[1]):
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



def addStarting(playerMap,projStarters):
    # print(playerMap)
    for playerid,gameMap in playerMap.items():
        for gameid,gameList in gameMap.items():
            isStarting = 1 if Scraper.playerid_to_playerName(playerid) in projStarters else 0
            gameList.append(isStarting)
    return playerMap




def convertRotowireList(rotoWireList,urlList):

    playerIDDict = ReadWriteFiles.readPlayerIDMap()

    #print("\noriginal list")
    #print(rotoWireList)

    returnedList = []

    for i in range(0,len(rotoWireList)):
        rotoname = rotoWireList[i]

        #takes care of cases where name matches
        #and when first and last name both match -> regardless of Jr. suffix, middle name
        if(rotoname in playerIDDict.keys() or (HumanName(rotoname).first + " " + HumanName(rotoname).last) in playerIDDict.keys()):
            returnedList.append(rotoname)
        else:
            if(rotoname[1] == "."):
                tempLst = []
                for playerName in playerIDDict.keys():
                    if(HumanName(playerName).first == HumanName(rotoname).first and playerName[0] == rotoname[0]):
                        tempLst.append(playerName)
                if len(tempLst) == 1:
                    returnedList.append(tempLst[0])
                else:
                    (html.fromstring(requests.get(urlList[i]).content)).xpath("//h1[position()=1]/text()")[0]

            else:
                for playerName in playerIDDict.keys():
                    if(HumanName(playerName).first == HumanName(rotoname).first and HumanName(playerName).last == HumanName(rotoname).last):
                        returnedList.append(playerName)


    
    # convertedList = [x if (x in playerIDDict.keys()) else [k for (k,v) in playerIDDict.items() if (x[1] == "." and x.split(" ")[1] in k and x[0] == k[0]) or x in k] for x in rotoWireList]

    # print(returnedList)
    # convertedList = [x[0] if not type(x[0]) == list else x[0][0] if len(x[0])==0 else (html.fromstring(requests.get(x[1]).content)).xpath("//h1[position()=1]/text()")[0] for x in zip(convertedList,urlList)]

    #[(html.fromstring(requests.get(x).content)).xpath("//h1[position()=1]/text()")[0] for x in starterFullURLList]

    #print("\nconverted list")
    #print(convertedList)
    return returnedList




def extract_playerIDS(todayList):
    return [item[0] for item in todayList]



def calc_fanduel_points(statList):
    #return (statList[1] - statList[3]) * 2 + statList[3] * 3 + statList[5] * 1 + statList[9] * 1.2 + statList[10] * 1.5 + statList[11] * 2 + statList[12] * 2 + statList[13] * -1
    return statList[16] + statList[9] * 1.2 + statList[10] * 1.5 + statList[11] * 2 + statList[12] * 2 + statList[13] * -1



#gameStatsLists are restricted by their maxlen variables
#if size of gameStatsList < desired number of games, then just avg what you have in gameStatsList
#   e.g. when gen features for 2nd game of season, all lists will just be stats from 1st game
def avgStats(gameStatsList):
    gameCount = len(gameStatsList)
    return (np.array([sum(x) for x in zip(*gameStatsList)]) / gameCount).tolist()



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