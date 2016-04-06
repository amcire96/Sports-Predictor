from scipy.stats import randint as sp_randint

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score
from sklearn.linear_model import *
from sklearn.grid_search import RandomizedSearchCV

from sklearn.ensemble import AdaBoostRegressor

from collections import deque
from collections import defaultdict
from collections import OrderedDict

import numpy as np
import datetime


import Scraper
import Util




def generate_features(currentMap,today_stats,injuredIDMap, injuredTodayMap):
     # print(type(currentMap))

     #print(today_stats)
     #featureList = OrderedDict(list)
     trainingFeatureList = deque([])
     testingFeatureList = deque([])

     todayFeatureList = deque([])

     completeFeatureMap = defaultdict(OrderedDict)

     allGameIDs = set()
     
     for playerid,orderedDict in currentMap.items():
         
         #prevGameIds = deque([])
         #19 stats for each game
         seasonGameStatsTotals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
         prevGameStats = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
         #use deques with max size to keep track of most recent n games
         prev2GamesStats = deque([],2)
         prev3GamesStats = deque([],3)
         prev5GamesStats = deque([],5)
         prev10GamesStats = deque([],10)
         prev20GamesStats = deque([],20)


         prev2GamesStats.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
         prev3GamesStats.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
         prev5GamesStats.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
         prev10GamesStats.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
         prev20GamesStats.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])


         count = 0

         #need how many games stats each player has
         #  split 80%-20% train-test
         #  best to split by time
         #first 4/5 of (games-first) = train, rest for test
         gamesForPlayer = len(orderedDict)


         for gameid,statList in orderedDict.items():

             allGameIDs.add(gameid)

             #count represents how many games the player has previously played
             gameFeature = [int(playerid)] + [int(gameid)] + statList[:8] + [count]


             gameFeature += prevGameStats
             gameFeature += Util.avgStats(prev2GamesStats)
             gameFeature += Util.avgStats(prev3GamesStats)
             gameFeature += Util.avgStats(prev5GamesStats)
             gameFeature += Util.avgStats(prev10GamesStats)
             gameFeature += Util.avgStats(prev20GamesStats)
             gameFeature += (np.array(seasonGameStatsTotals) / max(count,1)).tolist()
                 
             if(count <= 0.8 * (gamesForPlayer-1)):
                 trainingFeatureList.append(gameFeature)
             else:
                 testingFeatureList.append(gameFeature)
             # print("HERE gameid " + str(gameid))
             completeFeatureMap[playerid][gameid] = gameFeature
             # print(len(gameFeature))
             # if(len(gameFeature) != 158):
             #     print(gameFeature)



             count+=1
             #prevGameIds += [gameid]     
             prevGameStats = statList[8:]    
             prev2GamesStats.append(statList[8:])
             prev3GamesStats.append(statList[8:])
             prev5GamesStats.append(statList[8:])
             prev10GamesStats.append(statList[8:])
             prev20GamesStats.append(statList[8:])
             seasonGameStatsTotals = [x + y for x, y in zip(seasonGameStatsTotals,statList[8:])]


        
         if(playerid in today_stats):
             (todayGameid,statsList) = today_stats[playerid].popitem()
             feature = [int(playerid)] + [int(todayGameid)] + statsList[:8] + [count] + prevGameStats + Util.avgStats(prev2GamesStats) + Util.avgStats(prev3GamesStats) + Util.avgStats(prev5GamesStats) + Util.avgStats(prev10GamesStats) + Util.avgStats(prev20GamesStats) + (np.array(seasonGameStatsTotals) / count).tolist()
             todayFeatureList.append(feature)



     for feature in todayFeatureList:
        todayGameid = str(feature[1])
        ownTeamNum = feature[6]
        injuredList = injuredTodayMap[ownTeamNum]

        injuredListFeatures = []


        if(len(injuredList) == 0):
            injuredListFeatures = awayInjuredListFeatures = np.zeros((1,148))

        else:

            for injuredName in injuredList:
                injuredID = Scraper.playername_to_id(injuredName)

                for (gameid) in reversed(list(completeFeatureMap[injuredID].keys())):

                #get the last features that the injured player had
                    if(gameid <= todayGameid):
                        gameStatsList = completeFeatureMap[injuredID][gameid]

                        # weight = gameStatsList[10]
                        injuredListFeatures.append(gameStatsList[10:])
                        # print(len(gameStatsList[10:]))

                        break
            injuredListFeatures = np.array(injuredListFeatures)
        # print(injuredListFeatures.shape)


        meanInjuredStats = np.mean(injuredListFeatures,0)
        stdInjuredStats = np.std(injuredListFeatures,0)

        feature += (meanInjuredStats.tolist() + stdInjuredStats.tolist())


         #print(list(todayFeatureList))


     injuredMap = {}

     for currentGameID in allGameIDs:
        #create injury features
        # print(currentGameID)
        # print(type(currentGameID))

        #for both the away team and home team
        awayInjuredIDList = injuredIDMap[currentGameID][0]
        awayInjuredListFeatures = []
        for awayInjuredID in awayInjuredIDList:
            # print(type(completeFeatureMap[injuredID].keys()))
            # print("new awayInjuredID " + str(awayInjuredID))
            for (gameid) in reversed(list(completeFeatureMap[awayInjuredID].keys())):
                # print(gameid)
                # print(type(gameid))
                #get the last features that the injured player had
                if(gameid <= currentGameID):
                    gameStatsList = completeFeatureMap[awayInjuredID][gameid]

                    # weight = gameStatsList[10]
                    awayInjuredListFeatures.append(gameStatsList[10:])
                    # print(len(gameStatsList[10:]))

                    # print(awayInjuredID + " " + currentGameID)
                    # print(gameStatsList)
                    break
        if(len(awayInjuredListFeatures) == 0):
            awayInjuredListFeatures = np.zeros((1,148))
        else:
            awayInjuredListFeatures = np.array(awayInjuredListFeatures)
        # print(injuredListFeatures.shape)
        awayMeanInjuredStats = np.mean(awayInjuredListFeatures,0)
        awayStdInjuredStats = np.std(awayInjuredListFeatures,0)
        # print(awayMeanInjuredStats.shape)
        # print(awayStdInjuredStats.shape)




        homeInjuredIDList = injuredIDMap[currentGameID][1]
        homeInjuredListFeatures = []
        for homeInjuredID in homeInjuredIDList:
            # print(type(completeFeatureMap[injuredID].keys()))
            # print(reversed(list(completeFeatureMap[homeInjuredID].keys())))
            for (gameid) in reversed(list(completeFeatureMap[homeInjuredID].keys())):
                #get the last features that the injured player had
                if(gameid <= currentGameID):
                    gameStatsList = completeFeatureMap[homeInjuredID][gameid]

                    # weight = gameStatsList[10]
                    homeInjuredListFeatures.append(gameStatsList[10:])
                    # print(len(gameStatsList[10:]))

                    # print(homeInjuredID + " " + currentGameID)
                    # print(gameStatsList)
                    break
        if(len(homeInjuredListFeatures) == 0):
            homeInjuredListFeatures = np.zeros((1,148))
        else:
            homeInjuredListFeatures = np.array(homeInjuredListFeatures)
        # print(injuredListFeatures.shape)
        homeMeanInjuredStats = np.mean(homeInjuredListFeatures,0)
        homeStdInjuredStats = np.std(homeInjuredListFeatures,0)
        # print(homeMeanInjuredStats.shape)
        # print(homeStdInjuredStats.shape)




        injuredMap[currentGameID] = (awayMeanInjuredStats.tolist() + awayStdInjuredStats.tolist(), homeMeanInjuredStats.tolist() + homeStdInjuredStats.tolist())
     # print(injuredMap)



     #add injuryfeatures to previously computed features
     for gameFeature in list(trainingFeatureList):

         gameid = gameFeature[1]
         isAway = gameFeature[8]
         # print("HERE: " + str(gameid))
         gameFeature += injuredMap[str(gameid)][isAway]

     for gameFeature in list(testingFeatureList):
         gameid = gameFeature[1]
         isAway = gameFeature[8]
         # print("HERE: " + str(gameid))
         gameFeature += injuredMap[str(gameid)][isAway]


     return (np.array(list(trainingFeatureList)),np.array(list(testingFeatureList)), np.array(list(todayFeatureList)))



#(trainingFeatures,testingFeatures, todayFeatureList) = generate_features(currentMap,create_todays_playerMap())



def generate_labels(currentMap):
    trainingLabelsList = deque([])
    testingLabelsList = deque([])

    for playerid,orderedDict in currentMap.items():
         gameLabels = []

         gamesForPlayer = len(orderedDict)
         count = 0

         for gameid,statList in orderedDict.items():

            gameLabels = statList[12:]
            if(count <= 0.8 * (gamesForPlayer-1)):
                trainingLabelsList.append(gameLabels)
            else:
                testingLabelsList.append(gameLabels)
            count += 1
    return (np.array(list(trainingLabelsList)), np.array(list(testingLabelsList)))





def create_preds(trainingFeatures_arr,trainingLabels_arr,testingFeatures_arr,testingLabels_arr,todayFeatures_arr):

    #svr = svm.SVR()

    #print(trainingFeatures_arr)
    #print(trainingFeatures_arr.shape)
    #print(trainingLabels_arr.shape)
    #print(trainingLabels_arr)

    regr = DecisionTreeRegressor(max_depth=9)
    regr.fit(trainingFeatures_arr,trainingLabels_arr)
    print("r2_score 9: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))

    regr = DecisionTreeRegressor(max_depth=4)
    regr.fit(trainingFeatures_arr,trainingLabels_arr)
    print("r2_score 4: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))

    regr = DecisionTreeRegressor(max_depth=5)
    regr.fit(trainingFeatures_arr,trainingLabels_arr)
    print("r2_score 5: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))

    regr = DecisionTreeRegressor(max_depth=8)
    regr.fit(trainingFeatures_arr,trainingLabels_arr)
    print("r2_score 8: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))

    regr = DecisionTreeRegressor(max_depth=7)
    regr.fit(trainingFeatures_arr,trainingLabels_arr)
    print("r2_score 7: %f" % r2_score(testingLabels_arr,regr.predict(testingFeatures_arr),multioutput='uniform_average'))    

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
        print("EN r2_score reb: %f" % r2score2)
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
