
import os
import json
import csv
import pandas as pd
import datetime
from collections import OrderedDict
from collections import defaultdict

import Scraper
import Util



def writePlayerStats(currentMap):

    #today's date to label when writing the json
    today = datetime.date.today()
    todayStr = str(today.month) + "/" + str(today.day) + "/" + str(today.year)

    #write default dict into file -- default dict in json format
    with open("PlayerStats.txt","w") as f:
        f.write("Last Modified: " + todayStr + "\n")
        f.write(json.dumps(currentMap))






def writeFeaturesFiles(trainingFeatures,testingFeatures,todayFeatureList):

    with open('TodayFeatures.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["playerid","gameid","month","day","year","time","ownTeam","otherTeam","away/home",
                         "lastgame-ownscore","lastgame-otherscore", "lastgame-ot", "lastgame-started","lastgame-position","lastgame-mins","lastgame-fgm","lastgame-fga",
                         "lastgame-3pm","lastgame-3pa","lastgame-ftm","lastgame-fta","lastgame-dreb","lastgame-oreb","lastgame-reb",
                         "lastgame-ast","lastgame-stl","lastgame-blk","lastgame-to","lastgame-pf","lastgame+/-","lastgame-pts",                     
                         "last2games-ownscore","last2games-otherscore", "last2games-ot", "last2games-started","last2games-position","last2games-mins","last2games-fgm","last2games-fga","last2games-3pm",
                         "last2games-3pa","last2games-ftm","last2games-fta","last2games-dreb","last2games-oreb","last2games-reb",
                         "last2games-ast","last2games-stl","last2games-blk","last2games-to","last2games-pf","last2games+/-","last2games-pts",                     
                         "last3games-ownscore","last3games-otherscore", "last3games-ot", "last3games-started","last3games-position","last3games-mins","last3games-fgm","last3games-fga","last3games-3pm",
                         "last3games-3pa","last3games-ftm","last3games-fta","last3games-dreb","last3games-oreb","last3games-reb",
                         "last3games-ast","last3games-stl","last3games-blk","last3games-to","last3games-pf","last3games+/-","last3games-pts",
                         "last5games-ownscore","last5games-otherscore", "last5games-ot", "last5games-started","last5games-position","last5games-mins","last5games-fgm","last5games-fga","last5games-3pm",
                         "last5games-3pa","last5games-ftm","last5games-fta","last5games-dreb","last5games-oreb","last5games-reb",
                         "last5games-ast","last5games-stl","last5games-blk","last5games-to","last5games-pf","last5games+/-","last5games-pts",
                         "last10games-ownscore","last10games-otherscore", "last10games-ot", "last10games-started","last10games-position","last10games-mins","last10games-fgm","last10games-fga","last10games-3pm",
                         "last10games-3pa","last10games-ftm","last10games-fta","last10games-dreb","last10games-oreb","last10games-reb",
                         "last10games-ast","last10games-stl","last10games-blk","last10games-to","last10games-pf","last10games+/-","last10games-pts",
                         "last20games-ownscore","last20games-otherscore", "last20games-ot", "last20games-started","last20games-position","last20games-mins","last20games-fgm","last20games-fga","last20games-3pm",
                         "last20games-3pa","last20games-ftm","last20games-fta","last20games-dreb","last20games-oreb","last2games-reb",
                         "last20games-ast","last20games-stl","last20games-blk","last20games-to","last20games-pf","last20games+/-","last20games-pts",                     
                         "season-ownscore","season-otherscore", "season-ot", "season-started","season-position","season-mins","season-fgm","season-fga","season-3pm","season-3pa",
                         "season-ftm","season-fta","season-dreb","season-oreb","season-reb",
                         "season-ast","season-stl","season-blk","season-to","season-pf","season+/-","season-pts"])
        writer.writerows(todayFeatureList)

    with open('TrainingFeatures.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["playerid","gameid","month","day","year","time","ownTeam","otherTeam","away/home",
                         "lastgame-ownscore","lastgame-otherscore", "lastgame-ot", "lastgame-started","lastgame-position","lastgame-mins","lastgame-fgm","lastgame-fga",
                         "lastgame-3pm","lastgame-3pa","lastgame-ftm","lastgame-fta","lastgame-dreb","lastgame-oreb","lastgame-reb",
                         "lastgame-ast","lastgame-stl","lastgame-blk","lastgame-to","lastgame-pf","lastgame+/-","lastgame-pts",                     
                         "last2games-ownscore","last2games-otherscore", "last2games-ot", "last2games-started","last2games-position","last2games-mins","last2games-fgm","last2games-fga","last2games-3pm",
                         "last2games-3pa","last2games-ftm","last2games-fta","last2games-dreb","last2games-oreb","last2games-reb",
                         "last2games-ast","last2games-stl","last2games-blk","last2games-to","last2games-pf","last2games+/-","last2games-pts",                     
                         "last3games-ownscore","last3games-otherscore", "last3games-ot", "last3games-started","last3games-position","last3games-mins","last3games-fgm","last3games-fga","last3games-3pm",
                         "last3games-3pa","last3games-ftm","last3games-fta","last3games-dreb","last3games-oreb","last3games-reb",
                         "last3games-ast","last3games-stl","last3games-blk","last3games-to","last3games-pf","last3games+/-","last3games-pts",
                         "last5games-ownscore","last5games-otherscore", "last5games-ot", "last5games-started","last5games-position","last5games-mins","last5games-fgm","last5games-fga","last5games-3pm",
                         "last5games-3pa","last5games-ftm","last5games-fta","last5games-dreb","last5games-oreb","last5games-reb",
                         "last5games-ast","last5games-stl","last5games-blk","last5games-to","last5games-pf","last5games+/-","last5games-pts",
                         "last10games-ownscore","last10games-otherscore", "last10games-ot", "last10games-started","last10games-position","last10games-mins","last10games-fgm","last10games-fga","last10games-3pm",
                         "last10games-3pa","last10games-ftm","last10games-fta","last10games-dreb","last10games-oreb","last10games-reb",
                         "last10games-ast","last10games-stl","last10games-blk","last10games-to","last10games-pf","last10games+/-","last10games-pts",
                         "last20games-ownscore","last20games-otherscore", "last20games-ot", "last20games-started","last20games-position","last20games-mins","last20games-fgm","last20games-fga","last20games-3pm",
                         "last20games-3pa","last20games-ftm","last20games-fta","last20games-dreb","last20games-oreb","last2games-reb",
                         "last20games-ast","last20games-stl","last20games-blk","last20games-to","last20games-pf","last20games+/-","last20games-pts",                     
                         "season-ownscore","season-otherscore", "season-ot", "season-started","season-position","season-mins","season-fgm","season-fga","season-3pm","season-3pa",
                         "season-ftm","season-fta","season-dreb","season-oreb","season-reb",
                         "season-ast","season-stl","season-blk","season-to","season-pf","season+/-","season-pts"])
        writer.writerows(trainingFeatures)

    with open('TestingFeatures.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["playerid","gameid","month","day","year","time","ownTeam","otherTeam","away/home",
                         "lastgame-ownscore","lastgame-otherscore", "lastgame-ot", "lastgame-started","lastgame-position","lastgame-mins","lastgame-fgm","lastgame-fga",
                         "lastgame-3pm","lastgame-3pa","lastgame-ftm","lastgame-fta","lastgame-dreb","lastgame-oreb","lastgame-reb",
                         "lastgame-ast","lastgame-stl","lastgame-blk","lastgame-to","lastgame-pf","lastgame+/-","lastgame-pts",                     
                         "last2games-ownscore","last2games-otherscore", "last2games-ot", "last2games-started","last2games-position","last2games-mins","last2games-fgm","last2games-fga","last2games-3pm",
                         "last2games-3pa","last2games-ftm","last2games-fta","last2games-dreb","last2games-oreb","last2games-reb",
                         "last2games-ast","last2games-stl","last2games-blk","last2games-to","last2games-pf","last2games+/-","last2games-pts",                     
                         "last3games-ownscore","last3games-otherscore", "last3games-ot", "last3games-started","last3games-position","last3games-mins","last3games-fgm","last3games-fga","last3games-3pm",
                         "last3games-3pa","last3games-ftm","last3games-fta","last3games-dreb","last3games-oreb","last3games-reb",
                         "last3games-ast","last3games-stl","last3games-blk","last3games-to","last3games-pf","last3games+/-","last3games-pts",
                         "last5games-ownscore","last5games-otherscore", "last5games-ot", "last5games-started","last5games-position","last5games-mins","last5games-fgm","last5games-fga","last5games-3pm",
                         "last5games-3pa","last5games-ftm","last5games-fta","last5games-dreb","last5games-oreb","last5games-reb",
                         "last5games-ast","last5games-stl","last5games-blk","last5games-to","last5games-pf","last5games+/-","last5games-pts",
                         "last10games-ownscore","last10games-otherscore", "last10games-ot", "last10games-started","last10games-position","last10games-mins","last10games-fgm","last10games-fga","last10games-3pm",
                         "last10games-3pa","last10games-ftm","last10games-fta","last10games-dreb","last10games-oreb","last10games-reb",
                         "last10games-ast","last10games-stl","last10games-blk","last10games-to","last10games-pf","last10games+/-","last10games-pts",
                         "last20games-ownscore","last20games-otherscore", "last20games-ot", "last20games-started","last20games-position","last20games-mins","last20games-fgm","last20games-fga","last20games-3pm",
                         "last20games-3pa","last20games-ftm","last20games-fta","last20games-dreb","last20games-oreb","last2games-reb",
                         "last20games-ast","last20games-stl","last20games-blk","last20games-to","last20games-pf","last20games+/-","last20games-pts",                     
                         "season-ownscore","season-otherscore", "season-ot", "season-started","season-position","season-mins","season-fgm","season-fga","season-3pm","season-3pa",
                         "season-ftm","season-fta","season-dreb","season-oreb","season-reb",
                         "season-ast","season-stl","season-blk","season-to","season-pf","season+/-","season-pts"])
        writer.writerows(testingFeatures)







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






def write_all_today_preds(preds):
    with open("PredictedToday.csv","w",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["mins","fgm","fga","3pm","3pa","ftm","fta","dreb","oreb","reb",
                         "ast","stl","blk","to","pf","+/-","pts"])
        writer.writerows(preds)



def readPredsFile():
    todayPreds = pd.read_csv("PredictedToday.csv")
    #todayPreds_headers = list(todayPreds.columns.values)
    todayPreds = todayPreds._get_numeric_data()
    todayPreds_arr = todayPreds.as_matrix()
    return todayPreds_arr




def writePlayerIDDict(dict):
    with open("PlayerIDMap.txt","w") as f:
        f.write(json.dumps(dict))



def write_playerList(playerList):
    with open("playerlist.txt","w") as f:
        f.write(json.dumps(playerList))


def writeFinal_predList(pred_statList):
    with open("final_predList.txt","w") as f:
        f.write(json.dumps(pred_statList))



def readPlayerStatsFile():

    #read the file and extract the json/defaultdict
    with open("PlayerStats.txt","r") as f:
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

    return (lastModifiedDate,currentMap)




def readPlayerList():
    playerList = []
    with open("playerlist.txt","r") as f:
        playerList = json.loads(f.readline())
    return playerList



def readPlayerIDMap():
    with open("PlayerIDMap.txt","r") as f:
        a = f.readline()
        if(a == ""):
            playerIDDict = {}
        else:
            playerIDDict = json.loads(a)
            #print(playerIDDict)
    return playerIDDict




def gen_description_and_fanduel_map(dict,csvFileName):
    playerList = []
    pred_statList = {}

    with open("final.txt","w") as f:
        fanduel_data_arr = Util.fanduel_scrape(csvFileName)
    
        for playerid, statList in dict.items():
            name = Scraper.playerid_to_playerName(str(int(playerid)))
            #print(name)
        
            if(name in fanduel_data_arr["Name"].as_matrix()):
                [row] = fanduel_data_arr.loc[fanduel_data_arr['Name'] == name].as_matrix()
                position = row[1]
                fanduelAvg = row[4]
                cost = row[6]
                injured = row[10]

                predicted = Util.calc_fanduel_points(statList)

                #print(type(statList))

                pred_statList[name] = statList.tolist()
            
            
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


    writeFinal_predList(pred_statList)

    #writePlayerIDDict(playerIDDict)

    return playerList



def write_final_preds(resultList):
    with open("final_preds.txt","w") as f:
        f.write(json.dumps(resultList))
        f.write("\n")
        f.write(resultList[0][0] + "1: " + resultList[3][0] + " with projected " + "{0:.2f}".format(resultList[1][0]) + " points and " + str(resultList[2][0]) + " cost.\n")
        f.write(resultList[0][1] + "2: " + resultList[3][1] + " with projected " + "{0:.2f}".format(resultList[1][1]) + " points and " + str(resultList[2][1]) + " cost.\n")
        f.write(resultList[0][2] + "1: " + resultList[3][2] + " with projected " + "{0:.2f}".format(resultList[1][2]) + " points and " + str(resultList[2][2]) + " cost.\n")
        f.write(resultList[0][3] + "2: " + resultList[3][3] + " with projected " + "{0:.2f}".format(resultList[1][3]) + " points and " + str(resultList[2][3]) + " cost.\n")
        f.write(resultList[0][4] + "1: " + resultList[3][4] + " with projected " + "{0:.2f}".format(resultList[1][4]) + " points and " + str(resultList[2][4]) + " cost.\n")
        f.write(resultList[0][5] + "2: " + resultList[3][5] + " with projected " + "{0:.2f}".format(resultList[1][5]) + " points and " + str(resultList[2][5]) + " cost.\n")
        f.write(resultList[0][6] + "1: " + resultList[3][6] + " with projected " + "{0:.2f}".format(resultList[1][6]) + " points and " + str(resultList[2][6]) + " cost.\n")
        f.write(resultList[0][7] + "2: " + resultList[3][7] + " with projected " + "{0:.2f}".format(resultList[1][7]) + " points and " + str(resultList[2][7]) + " cost.\n")
        f.write(resultList[0][8] + ": " + resultList[3][8] + " with projected " + "{0:.2f}".format(resultList[1][8]) + " points and " + str(resultList[2][8]) + " cost.\n")
        f.write("Total projected points is " + "{0:.2f}".format(resultList[4]) + "\n")
        f.write("Total cost is " + str(resultList[5]))




def check_yesterday_fanduel(playerMap):
    yesterdayDate = datetime.date.today()-datetime.timedelta(days=1)
    with open("final_preds.txt","r") as f:
        resultList = json.loads(f.readline())
    with open("final_predList.txt","r") as f:
        predList = json.loads(f.readline())
    with open("yesterday_results.txt","w") as f:
        totalPred = 0
        totalActual = 0
        totalCost = 0
        for i in range(0,len(resultList[0])):
            name = resultList[3][i]
            points = resultList[1][i]
            position = resultList[0][i]
            cost= resultList[2][i]

            totalPred += points
            totalCost += cost

            #print(name)
            playeridStr = Scraper.playername_to_id(str(name))
            #print(playeridStr)
           # print(type(playeridStr))

            gameOrderedDict = playerMap[playeridStr]


            lastGameStats = gameOrderedDict[next(reversed(gameOrderedDict))]

            predictedStatsList = predList[name]
            

            if(lastGameStats[0] != yesterdayDate.month or lastGameStats[1] != yesterdayDate.day or lastGameStats[2] != yesterdayDate.year):
                f.write(name + " might have been injured or did not play\n")
                f.write(name + " (" + position + ") was projected for " + str(points) + " points at " + str(cost) + " cost and actually got " + str(0) + "\n")
            else:
                f.write(json.dumps([float("{0:.2f}".format(x)) for x in predictedStatsList])+"\n")
                statsList = lastGameStats[12:]
                f.write(json.dumps(statsList)+"\n")
                actual_fanduel = calc_fanduel_points(statsList)
                totalActual += actual_fanduel
                f.write(name + " (" + position + ") was projected for " + str(points) + " points at " + str(cost) + " cost and actually got " + str(actual_fanduel) + "\n")
            f.write("\n")
        f.write("Total Predicted points is " + str(totalPred) + " at " + str(totalCost) + " cost, and total actual points is " + "{0:.2f}".format(totalActual)) 
