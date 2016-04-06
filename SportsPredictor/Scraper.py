from lxml import html
import requests
import datetime
from collections import defaultdict
from collections import OrderedDict
import Util
import ReadWriteFiles



def playername_to_id(playername):
    playerIDDict = ReadWriteFiles.readPlayerIDMap()
    return playerIDDict[playername]

def playerid_to_playerName(playerid):

    playerIDDict = ReadWriteFiles.readPlayerIDMap()

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
        playerIDDict[playerName] = playerid

        ReadWriteFiles.writePlayerIDDict(playerIDDict)

        return playerName
        

def createPlayerMap(gameids,currentMap):

    #use defaultdict to map playerids to game stats
    playerMap = defaultdict(OrderedDict)
    #playerMap = OrderedDict()

    print(sorted(gameids,key=lambda x: x[1]))

    #will keep track of playerids of injured players on both teams
    injuredIDMap = ReadWriteFiles.readInjuredIDMap()
    
    for gameid in sorted(gameids,key=lambda x: x[1]):
        gameid = gameid[0]
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
            OTfinalStatus = gameInfoTree.xpath("//div[@class='game-status']/span/text()")[0]
            if("OT" in OTfinalStatus):

                [_,ot] = OTfinalStatus.split("/")
                if (ot == "OT"):
                    overtime = 1
                else:
                    overtime = int(ot[0])
            else:
                overtime = 0
            #print(OTfinalStatus)
            #print(game_time_info)

            #[awayName,awayScore] = boxScoreTree.xpath("//div[@class='team away']/div/h3/*/text()") OLD ESPN
            #[homeName,homeScore] = boxScoreTree.xpath("//div[@class='team home']/div/h3/*/text()") OLD ESPN

            awayName = boxScoreTree.xpath("//div[@class='team away']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")[0]
            homeName = boxScoreTree.xpath("//div[@class='team home']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")[0]

            awayScore = boxScoreTree.xpath("//div[@class='team away']/div[@class='content']/div[@class='score-container']/div/text()")[0]
            homeScore = boxScoreTree.xpath("//div[@class='team home']/div[@class='content']/div[@class='score-container']/div/text()")[0]

            #scoreDifference = int(awayScore) - int(homeScore)


            #print(scoreDifference)
            #print(awayName)
            #print(homeName)


            #keep track of which players were on the away team and which were on the home team
            #[awayTeam] = boxScoreTree.xpath("//table/thead[position()=1]/tr[@class='team-color-strip']/th/text()")
            awayTeamNum = Util.team_dict[awayName]
            #awayPlayeridList = boxScoreTree.xpath("//table/tbody[position()=1 or position()=2]/tr[contains(@class,'player-46')]/@class") OLD ESPN
            #awayPlayeridList = [x.split("player-46-")[1] for x in awayPlayeridList]
            
            #print(boxScoreTree.xpath("//tr/td/a/@href"))
            #print(boxScoreTree.xpath("//div[@class='col column-one gamepackage-away-wrap']/*"))
            #print(boxScoreTree.xpath("//div[@class='col column-one gamepackage-away-wrap']/div[@class='sub-module']/*"))
            #print(boxScoreTree.xpath("//div[@class='col column-one gamepackage-away-wrap']/div[@class='sub-module']/div/table/tbody/tr/td/a/@href"))
            awayPlayerURLList = boxScoreTree.xpath("//div[@class='col column-one gamepackage-away-wrap']/div[@class='sub-module']/div/table/tbody/tr/td/a/@href")
            awayPlayeridList = [x.split("_/id/")[1] for x in awayPlayerURLList]
            awayStarteridList = awayPlayeridList[0:5]
            awayBenchidList = awayPlayeridList[5:]
            #print(awayPlayeridList)



           # [homeTeam] = boxScoreTree.xpath("//table/thead[position()=4]/tr[@class='team-color-strip']/th/text()")
            homeTeamNum = Util.team_dict[homeName]
            #homePlayeridList = boxScoreTree.xpath("//table/tbody[position()=4 or position()=5]/tr[contains(@class,'player-46')]/@class")
            #homePlayeridList = [x.split("player-46-")[1] for x in homePlayeridList]

            homePlayerURLList = boxScoreTree.xpath("//div[@class='col column-two gamepackage-home-wrap']/div[@class='sub-module']/div/table/tbody/tr/td/a/@href")
            homePlayeridList = [x.split("_/id/")[1] for x in homePlayerURLList]
            homeStarteridList = homePlayeridList[0:5]
            homeBenchidList = homePlayeridList[5:]
            #print(homePlayeridList)





            awayInjuredIDList = []
            #gets player stats for away players and appends that to the game stats
            for playerid in awayStarteridList:
                xPathStatsString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/*/text()"
                xPathPositionString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/td/*/text()"
                #print(xPathPositionString)

                gameStatsList = []
                # stores own team's number and also the opposing team's number
                # 0 for away team then 1 for being a starter and then away score (own score) then home score (other score)
                
                gameStatsList += Util.data_date_convert(game_time_info) + [awayTeamNum, homeTeamNum] + [0, 1, int(awayScore),int(homeScore), overtime]      
 
                playerStatsList = [boxScoreTree.xpath(xPathPositionString)[1]] + boxScoreTree.xpath(xPathStatsString)
                
                #print(playerStatsList)

                if("DNP" not in playerStatsList[1] or "COACH'S DECISION" in playerStatsList[1] or len(playerStatsList) != 2):         
                    playerStatsList = Util.playerStatsConvert(playerStatsList)
                   # print(playerStatsList)
                   # playerMap[playerid].append(gameid)
                   # print(gameStatsList+playerStatsList)
        
                    playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
                    #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})

                else:
                    awayInjuredIDList.append(playerid)
                    print(playerid + " is injured, so stats from game will not count")



            #gets player stats for away players and appends that to the game stats
            for playerid in awayBenchidList:
                xPathStatsString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/*/text()"
                xPathPositionString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/td/*/text()"
                #print(xPathPositionString)

                gameStatsList = []
                # stores own team's number and also the opposing team's number
                # 0 for away team then 0 for coming off the benchand then away score (own score) then home score (other score)
                
                gameStatsList += Util.data_date_convert(game_time_info) + [awayTeamNum, homeTeamNum] + [0, 0,int(awayScore),int(homeScore), overtime]      
 
                playerStatsList = [boxScoreTree.xpath(xPathPositionString)[1]] + boxScoreTree.xpath(xPathStatsString)
                
                #print(playerStatsList)

                if("DNP" not in playerStatsList[1] or "COACH'S DECISION" in playerStatsList[1]):         
                    playerStatsList = Util.playerStatsConvert(playerStatsList)
                   # print(playerStatsList)
                   # playerMap[playerid].append(gameid)
                   # print(gameStatsList+playerStatsList)
        
                    playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
                    #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})

                else:
                    awayInjuredIDList.append(playerid)
                    print(playerid + " is injured, so stats from game will not count")
        



            homeInjuredIDList = []
            #gets player stats for home players and appends that to the game stats
            for playerid in homeStarteridList:
                xPathStatsString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/*/text()"
               

                xPathPositionString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/td/*/text()"
                #print(xPathPositionString)

                gameStatsList = []
        
                # stores own team's number and also the opposing team's number
                # 1 for home team, 1 for starter and score difference is calc away score - home score
                #
                gameStatsList += Util.data_date_convert(game_time_info) + [homeTeamNum, awayTeamNum] + [1, 1, int(homeScore), int(awayScore), overtime]

                playerStatsList = [boxScoreTree.xpath(xPathPositionString)[1]] + boxScoreTree.xpath(xPathStatsString)

                if("DNP" not in playerStatsList[1] or "COACH'S DECISION" in playerStatsList[1]):

                
                    playerStatsList = Util.playerStatsConvert(playerStatsList)
                   # print(playerStatsList)
                   # playerMap[playerid].append(gameid)

                    playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
                    #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})
                else:
                    homeInjuredIDList.append(playerid)
                    print(playerid + " is injured, so stats from game will not count")


                    #gets player stats for home players and appends that to the game stats
            for playerid in homeBenchidList:
                xPathStatsString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/*/text()"
               

                xPathPositionString = "//tr[td/a/@href='http://espn.go.com/nba/player/_/id/" + playerid + "']/td/*/text()"
                #print(xPathPositionString)

                gameStatsList = []
        
                # stores own team's number and also the opposing team's number
                # 1 for home team, 0 for bench and score difference is calc away score - home score
                # 
                gameStatsList += Util.data_date_convert(game_time_info) + [homeTeamNum, awayTeamNum] + [1, 0, int(homeScore), int(awayScore), overtime]

                playerStatsList = [boxScoreTree.xpath(xPathPositionString)[1]] + boxScoreTree.xpath(xPathStatsString)

                if("DNP" not in playerStatsList[1] or "COACH'S DECISION" in playerStatsList[1]):

                
                    playerStatsList = Util.playerStatsConvert(playerStatsList)
                   # print(playerStatsList)
                   # playerMap[playerid].append(gameid)

                    playerMap[playerid][gameid]=(gameStatsList+playerStatsList)
                    #playerMap[playerid] = OrderedDict({gameid:(gameStatsList+playerStatsList)})
                else:
                    homeInjuredIDList.append(playerid)
                    print(playerid + " is injured, so stats from game will not count")

            injuredIDMap[gameid] = (awayInjuredIDList,homeInjuredIDList)

        except (IndexError):
            print("Game " + gameid + " does not exist")
            #raise IndexError
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



    return (currentMap,injuredIDMap)




def getInjuredPlayers():
    projURL = "http://www.rotowire.com/basketball/nba_lineups.htm"
    # projURL = "http://www.rotowire.com/basketball/nba_lineups.htm?date=tomorrow"
    projPage = requests.get(projURL)
    projTree = html.fromstring(projPage.content)


    awayTeamNames = projTree.xpath("//div[@class='span15 dlineups-mainbox']/div[@class='span15 dlineups-mainbar']/div[@class='dlineups-mainbar-away']/a/text()")
    # print(awayTeamNames)

    homeTeamNames = projTree.xpath("//div[@class='span15 dlineups-mainbox']/div[@class='span15 dlineups-mainbar']/div[@class='dlineups-mainbar-home']/a/text()")
    # print(homeTeamNames)


    injuredMap = {}

    for awayTeamName in awayTeamNames:
        teamNum = Util.team_dict[awayTeamName]
        injuredNameList = projTree.xpath("//div[div/div/a = '" + awayTeamName + "']/div[@class='span15']/div[@class='span15']/div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/a/text()")
        injuredURLList = projTree.xpath("//div[div/div/a = '" + awayTeamName + "']/div[@class='span15']/div[@class='span15']/div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/a/@href")
        injuredURLList = ["http://www.rotowire.com" + x for x in injuredURLList]
        injuredDesignationList = projTree.xpath("//div[div/div/a = '" + awayTeamName + "']/div[@class='span15']/div[@class='span15']/div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/b/text()")
        finalList = [x[0] for x in zip(Util.convertRotowireList(injuredNameList,injuredURLList),injuredDesignationList) if x[1] != "inactive"]
        injuredMap[teamNum] = finalList


    for homeTeamName in homeTeamNames:
        teamNum = Util.team_dict[homeTeamName]
        injuredNameList = projTree.xpath("//div[div/div/a = '" + homeTeamName + "']/div[@class='span15']/div[@class='span15']/div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/a/text()")
        injuredURLList = projTree.xpath("//div[div/div/a = '" + homeTeamName + "']/div[@class='span15']/div[@class='span15']/div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/a/@href")
        injuredURLList = ["http://www.rotowire.com" + x for x in injuredURLList]
        injuredDesignationList = projTree.xpath("//div[div/div/a = '" + homeTeamName + "']/div[@class='span15']/div[@class='span15']/div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/text()")
        finalList = [x[0] for x in zip(Util.convertRotowireList(injuredNameList,injuredURLList),injuredDesignationList) if x[1] != "inactive"]
        injuredMap[teamNum] = finalList


    # injuredNameList = projTree.xpath("//div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/a/text() | //div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/a/text()")
    #
    # injuredURLList = projTree.xpath("//div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/a/@href | //div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/a/@href")
    # injuredURLList = ["http://www.rotowire.com" + x for x in injuredURLList]

    # injuredDesignationList = projTree.xpath("//div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/b/text() | //div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/b/text() | //div[@class='dlineups-half equalheight']/div[@class='dlineups-vplayer']/div/text() | //div[@class='dlineups-half equalheight']/div[@class='dlineups-hplayer']/div/text()")

    #print(injuredDesignationList)



    return injuredMap




def getProjStarters():
    projURL = "http://www.rotowire.com/basketball/nba_lineups.htm"
    projPage = requests.get(projURL)
    projTree = html.fromstring(projPage.content)


    starterNameList = projTree.xpath("//div[@class='dlineups-half']/div[@class='dlineups-vplayer']/div/a/text() | //div[@class='dlineups-half']/div[@class='dlineups-hplayer']/div/a/text()")


    starterURLList = projTree.xpath("//div[@class='dlineups-half']/div[@class='dlineups-vplayer']/div/a/@href | //div[@class='dlineups-half']/div[@class='dlineups-hplayer']/div/a/@href")


    starterURLList = ["http://www.rotowire.com" + x for x in starterURLList]


    #print(starterFullURLList)

    #starterNameList = [(html.fromstring(requests.get(x).content)).xpath("//h1[position()=1]/text()")[0] for x in starterFullURLList]
    #print(starterNameList)


    return Util.convertRotowireList(starterNameList,starterURLList)





def getNewGameIDs(lastModifiedDate):
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

        (newGameIDs,newGameIDDates) = Util.extractNewGameIDs(teamGameidList,gameDateList,lastModifiedDate)
        #print(newGameIDs)
        gameids |= set([(newGameIDs[i],newGameIDDates[i]) for i in range(0,len(newGameIDs))])
    return gameids





#generate playerMap for today's game -> will be what we are predicting
#map with have list of m, d, y, time, ownTeam, otherTeam, away/home
def create_todays_playerMap():
    today_playerMap = defaultdict(OrderedDict)



    schedulePage = requests.get("http://espn.go.com/nba/schedule")
    scheduleTree = html.fromstring(schedulePage.content)
    #print(scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/caption"))
    date = scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=2]/table/caption/text()")[0]
    date = Util.strToDate(date)
    #print(date)

    if(date != datetime.date.today()):
        print("ESPN's schedule page has not updated for today's games")
        #exit()
        date = scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=3]/table/caption/text()")[0]
        date = Util.strToDate(date)
        
        todaysGameIDs = [x.split("=")[1] for x in scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=3]/table/tbody/tr/td[position()=3]/a/@href")]
       # todayGameTimes = [x+" ET" for x in scheduleTree.xpath("//div[@class='basketball']/div[@id='sched-container']/div[position()=3]/table/tbody/tr/td[position()=3]/a//text()")]
        if(date != datetime.date.today()):
            print("Something is wrong with ESPN's schedule page")
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
        game_time_info = boxScoreTree.xpath("//div[@class='game-status']/span/@data-date")[0]
        #print(game_time_info)
        [m,d,y,t] = Util.data_date_convert(game_time_info)

    
        #[awayTeamName] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=1]/div[@class='team-info']/h3/a/text()")
        #[homeTeamName] = boxScoreTree.xpath("//div[@class='gamehq-wrapper']/div[@class='summary-tabs-container']/div[@class='span-4']/div[position() = 2]/div[position()=2]/div[@class='team-info']/h3/a/text()")

        #print(boxScoreTree.xpath("//div[@class='competitors']/*"))

        awayTeamName = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team away']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")[0]
        homeTeamName = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team home']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/span[@class='short-name']/text()")[0]

        #print(awayTeamName)
        #print(homeTeamName)


        awayTeamURL = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team away']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/@href")[0]
        #print(awayTeamName)
        [a,b]=awayTeamURL.split("_")
        awayRosterURL = a + "roster/_" + b
        awayRosterPage = requests.get("http://espn.go.com" + awayRosterURL)
        awayRosterTree = html.fromstring(awayRosterPage.content)
        awayPlayeridList = [x.split("player-46-")[1] for x in awayRosterTree.xpath("//tr[contains(@class,'player-46')]/@class")]
        #print(awayRosterURL)

        for playerid in awayPlayeridList:
            # playername = playerid_to_playerName(playerid)
            # print(playername)

            today_playerMap[playerid][gameid] = [m,d,y,t,Util.team_dict[awayTeamName],Util.team_dict[homeTeamName],0]

    
        homeTeamURL = boxScoreTree.xpath("//div[@class='competitors']/div[@class='team home']/div[@class='content']/div[@class='team-container']/div[@class='team-info']/a/@href")[0]
        #print(homeTeamURL)
        [a,b]=homeTeamURL.split("_")
        homeRosterURL = a + "roster/_" + b
        #print(homeRosterURL)
        homeRosterPage = requests.get("http://espn.go.com" + homeRosterURL)
        homeRosterTree = html.fromstring(homeRosterPage.content)
        homePlayeridList = [x.split("player-46-")[1] for x in homeRosterTree.xpath("//tr[contains(@class,'player-46')]/@class")]
        #print(homePlayeridList)
        for playerid in homePlayeridList:
            # playername = playerid_to_playerName(playerid)
            # print(playername)
            today_playerMap[playerid][gameid] = [m,d,y,t,Util.team_dict[homeTeamName],Util.team_dict[awayTeamName],1]
    
    return today_playerMap