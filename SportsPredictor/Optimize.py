

import numpy as np


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