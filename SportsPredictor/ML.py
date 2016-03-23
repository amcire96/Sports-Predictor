from scipy.stats import randint as sp_randint

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score
from sklearn.linear_model import *
from sklearn.grid_search import RandomizedSearchCV

from sklearn.ensemble import AdaBoostRegressor

from collections import deque

import numpy as np

import Util




def generate_features(currentMap,today_stats):
     #print(today_stats)
     #featureList = OrderedDict(list)
     trainingFeatureList = deque([])
     testingFeatureList = deque([])

     todayFeatureList = deque([])
     
     for playerid,orderedDict in currentMap.items():
         
         #prevGameIds = deque([])
         #19 stats for each game
         seasonGameStatsTotals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
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
             gameFeature = [int(playerid)] + [int(gameid)] + statList[:8]

             #don't do anything for the first game
             if (count != 0):
                 gameFeature += prevGameStats
                 gameFeature += Util.avgStats(prev2GamesStats)
                 gameFeature += Util.avgStats(prev3GamesStats)
                 gameFeature += Util.avgStats(prev5GamesStats)
                 gameFeature += Util.avgStats(prev10GamesStats)
                 gameFeature += Util.avgStats(prev20GamesStats)
                 gameFeature += (np.array(seasonGameStatsTotals) / count).tolist()
                 
                 if(count <= 0.8 * (gamesForPlayer-1)):
                     trainingFeatureList.append(gameFeature)
                 else:
                     testingFeatureList.append(gameFeature)

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
             (key,val) = today_stats[playerid].popitem()
             feature = [int(playerid)] + [int(key)] + val[:8] + prevGameStats + Util.avgStats(prev2GamesStats) + Util.avgStats(prev3GamesStats) + Util.avgStats(prev5GamesStats) + Util.avgStats(prev10GamesStats) + Util.avgStats(prev20GamesStats) + (np.array(seasonGameStatsTotals) / count).tolist()
             todayFeatureList.append(feature)

         #print(list(todayFeatureList))

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
             if(count != 0):
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
