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


import Optimize
import ML
import Util
import ReadWriteFiles
import Scraper


# print("Reading previously stored player-stats map")
(lastModifiedDate,currentMap) = ReadWriteFiles.readPlayerStatsFile()
isUpdated = (lastModifiedDate == datetime.date.today())

print("Getting data about players playing today")
today_playerMap = Scraper.create_todays_playerMap()
projStarters = Scraper.getProjStarters()

today_playerMap = Util.addStarting(today_playerMap,projStarters)
print(json.dumps(today_playerMap))


(lastModifiedDate,currentMap) = ReadWriteFiles.readPlayerStatsFile()

injuredTodayMap = Scraper.getInjuredPlayers()
injuredIDMap = ReadWriteFiles.readInjuredIDMap()



if(not isUpdated):
    print("Creating Player Map")
    gameids = Scraper.getNewGameIDs(lastModifiedDate)
    #print(gameids)
    (currentMap,injuredIDMap) = Scraper.createPlayerMap(gameids,currentMap)
    #
    # ReadWriteFiles.writePlayerStats(currentMap)
    # ReadWriteFiles.writeInjuredIDMap(injuredIDMap)

    # print(currentMap)

    print("Done creating and writing Player Map")




else:
    print("PlayerMap is already updated, so not creating new PlayerMap")



print("------------------------------------------------------------------------------------------------------------------")
checkFanduel = str(input("Would you like to check yesterday's prediction results? (Y/N)\n"))
if(checkFanduel.lower() == "y" or checkFanduel.lower() == "yes"):
    print("Checking yesterday's results")
    ReadWriteFiles.check_yesterday_fanduel(currentMap)
    print("Done checking. Wrote results to 'yesterday_results.txt'")

if(not isUpdated):
    print("Generating features/labels")
    (trainingFeatures_arr,testingFeatures_arr,todayFeatures_arr) = ML.generate_features(currentMap,today_playerMap,injuredIDMap,injuredTodayMap)
    

    (trainingLabels_arr,testingLabels_arr) = ML.generate_labels(currentMap)
    

    print("Done generating features and labels")
else:
    (trainingFeatures_arr,trainingLabels_arr,todayFeatures_arr,testingFeatures_arr,testingLabels_arr) = ReadWriteFiles.readCSVFiles()
    print("Features and Labels are already updated -- just reading those files now, so not creating new ones")



today_playerIDS = Util.extract_playerIDS(todayFeatures_arr)

if(not isUpdated):
    print("Creating predictions")
    preds = ML.create_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr)
    
    print("Done making predictions about players playing today")
else:
    preds = ReadWriteFiles.readPredsFile()
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



playerList = ReadWriteFiles.gen_description_and_fanduel_map(dictionary,csvFileName)

#write_playerList(playerList)

print("Done using Fanduel Data and now optimizing to find best predicted line-up")

#playerList = readPlayerList()
    

result = Optimize.optimize(playerList,totalSalary)

Util.format_print(result)

print("writing files to update information")
if(not isUpdated):
    ReadWriteFiles.writePlayerStats(currentMap)
    ReadWriteFiles.writeFeaturesFiles(trainingFeatures_arr,testingFeatures_arr,todayFeatures_arr)
    ReadWriteFiles.writeLabelsCSVFiles(trainingLabels_arr,testingLabels_arr)
    ReadWriteFiles.write_all_today_preds(preds)
    ReadWriteFiles.writeInjuredIDMap(injuredIDMap)
#final_preds could be different if player list from fanduel is updated
ReadWriteFiles.write_final_preds(result)



# Experimenting with auto login to FanDuel
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


#def getPlayerList(contestID):
#    [a,_] = contestID.split("-")
#    url = "https://www.fanduel.com/games/" + a + "/contests/" + contestID + "/enter"

#    contestPage = requests.get(url)
#    contestTree = html.fromstring(contestPage.content)
#    playerlist = contestTree.xpath("//body/*")
#    print(playerlist)

    #print(contestTree)