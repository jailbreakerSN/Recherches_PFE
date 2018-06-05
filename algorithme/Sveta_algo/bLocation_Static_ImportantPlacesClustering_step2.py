import sys

import butility
sys.path.append("/home/danbjork/analysis/towers/distance/")
from tower_location_data import *
from tower_location_data_predicted import *








reader = open("tables/importantplaces/line_tower_date_transactions_bkup.txt", "r")
# LineID, Tower, Date, Transactions
reader.next()




#
# 2. CLUSTER TOWERS
#
dClusterTowerProperty = butility.ThreeStruct()



# d[cluster][tower][property]

def computeClusterCentroid(dTowerProperty):
  fNumeratorLat  = 0
  fNumeratorLong = 0
  fDenominator   = 0
  
  for nTower, dProperties in dTowerProperty.iteritems():
    fNumeratorLat  += dProperties[ "Days.Used" ] * TOWER_LATp[  nTower ]
    fNumeratorLong += dProperties[ "Days.Used" ] * TOWER_LONGp[ nTower ]
    fDenominator   += dProperties[ "Days.Used" ]
  
  return (fNumeratorLat/fDenominator, fNumeratorLong/fDenominator)

def weightCluster_MaxDaysUsed(dTowerProperty):
  nMaxDaysUsed = 0
  for nTower, dProperties in dTowerProperty.iteritems():
    nMaxDaysUsed = max( nMaxDaysUsed, dProperties[ "Days.Used" ])
  return nMaxDaysUsed

def weightCluster_TotalDaysUsed(dTowerProperty):
  nTotalDaysUsed = 0
  for nTower, dProperties in dTowerProperty.iteritems():
    nTotalDaysUsed += dProperties[ "Days.Used" ]
  return nTotalDaysUsed

def weightCluster_TotalTransactions(dTowerProperty):
  nTransactions = 0
  for nTower, dProperties in dTowerProperty.iteritems():
    nTransactions += dProperties[ "Transactions" ]
  return nTransactions

def weightCluster_CombinedDaysUsed(dTowerProperty, dTower_Date_Transactions): # find dates covered by cluster (no duplication)
  dDatesCovered = {}
  for nTower in dTowerProperty.iterkeys(): # note that dtowerproperty is towers within this cluster, but dtower_date_transactions covers all towers every used by this line
    for cDate in dTower_Date_Transactions[ nTower ].iterkeys():
      dDatesCovered[ cDate ] = 1
  
  return len(dDatesCovered)


# nCLUSTER_DISTANCE_THRESHOLD = 20

# nCLUSTER_DISTANCE_THRESHOLD_MIN = 5 # vs. 1mi in Isaacman et al 2011
# nCLUSTER_DISTANCE_THRESHOLD_MAX = 15

# nCLUSTER_DISTANCE_THRESHOLD_MIN = 15 # vs. 1mi in Isaacman et al 2011
# nCLUSTER_DISTANCE_THRESHOLD_MAX = 15

#nCLUSTER_DISTANCE_THRESHOLD_MIN = 5 # vs. 1mi in Isaacman et al 2011
#nCLUSTER_DISTANCE_THRESHOLD_MAX = 30

nCLUSTER_DISTANCE_THRESHOLD_MIN = 5 # vs. 1mi in Isaacman et al 2011
nCLUSTER_DISTANCE_THRESHOLD_MAX = 2000


dClusterDistanceThresholdByTower = {}
readThreshold = open("../../towerlocations/distance/tables/bDistanceToNearestTowerByTower.txt", "r")
for line in readThreshold:
  fields = [ x.strip() for x in line.split(",") ]
  
  nTower             = int(fields[0])
  fThirdNearestTower = float(fields[3])
  fNinthNearestTower = float(fields[9])
  
  dClusterDistanceThresholdByTower[ nTower ] = max(nCLUSTER_DISTANCE_THRESHOLD_MIN, min(nCLUSTER_DISTANCE_THRESHOLD_MAX, fNinthNearestTower + 0.01) ) # include a bit of fudge room in case of rounding issues

readThreshold.close()



def computeAndWriteClusters( local_dTower_Date_Transactions, local_writerClusters, local_writerMaxCombinedDaysClusters ):
  dClusterTowerProperty = butility.ThreeStruct()
  
  # assemble aggregate properties by tower
  aTowers       = local_dTower_Date_Transactions.keys()
  aDaysUsed     = [ len( local_dTower_Date_Transactions[ nTower ] )              for nTower in aTowers ]
  aTransactions = [ sum( local_dTower_Date_Transactions[ nTower ].itervalues() ) for nTower in aTowers ]
  # put into tuples and sort by days used
  atupTowers_DaysUsed_Transactions = sorted(zip(aTowers, aDaysUsed, aTransactions), key=lambda tup: tup[1], reverse=True)
  
  # CLUSTER TOWERS
  for (nTower, nDaysUsed, nTransactions) in atupTowers_DaysUsed_Transactions:
    nDestinationCluster = -1
    if nDaysUsed > 0 and nTransactions > 0:
      try:
        (fTowerLat,   fTowerLong  ) = ( TOWER_LATp[ nTower ], TOWER_LONGp[ nTower ] )
      except KeyError:
        continue
      
      for nCluster in range(0, len(dClusterTowerProperty)):
        (fClusterLat, fClusterLong) = computeClusterCentroid( dClusterTowerProperty[ nCluster ] )
        
        fDistance = butility.haversine( fClusterLong, fClusterLat, fTowerLong, fTowerLat )
        
        if fDistance < dClusterDistanceThresholdByTower[ nTower ]: # Note here we are using a dynamic threshold based on the tower we are placin. TODO: unclear if better to use threshold from placing tower or first tower added to this cluster.
          nDestinationCluster = nCluster
          dClusterTowerProperty[ nDestinationCluster ][ nTower ][ "Days.Used"    ] = nDaysUsed
          dClusterTowerProperty[ nDestinationCluster ][ nTower ][ "Transactions" ] = nTransactions
          break
      
      if nDestinationCluster == -1:
        nDestinationCluster = len(dClusterTowerProperty)
        dClusterTowerProperty[ nDestinationCluster ][ nTower ][ "Days.Used"    ] = nDaysUsed
        dClusterTowerProperty[ nDestinationCluster ][ nTower ][ "Transactions" ] = nTransactions
  
  
  # WRITE OUT CLUSTERS
  nMaxCombinedDays = 0 # keep track of max by combined days
  cMaxLineToWrite  = ""
  for nCluster in range(0, len(dClusterTowerProperty)):
    tupLocation   = computeClusterCentroid( dClusterTowerProperty[ nCluster ] )
    nCombinedDays = weightCluster_CombinedDaysUsed(dClusterTowerProperty[ nCluster ], local_dTower_Date_Transactions)
    cLineToWrite  = ",".join([ cLastLineID,
                               str(nCluster),
                               str(tupLocation[0]),
                               str(tupLocation[1]),
                               str(nCombinedDays),
                               str(weightCluster_MaxDaysUsed(dClusterTowerProperty[ nCluster ])),
                               str(weightCluster_TotalDaysUsed(dClusterTowerProperty[ nCluster ])),
                               str(weightCluster_TotalTransactions(dClusterTowerProperty[ nCluster ])),
                               "|".join( dClusterTowerProperty[nCluster].keys() )   ]) + "\n"
    
    local_writerClusters.write( cLineToWrite )
    
    if nCombinedDays > nMaxCombinedDays:
      nMaxCombinedDays = nCombinedDays
      cMaxLineToWrite  = cLineToWrite
  
  local_writerMaxCombinedDaysClusters.write( cMaxLineToWrite ) # write only max cluster to this file







writerClusters = open("tables/importantplaces/line_cluster_properties_9towers_nomax_towermember.txt", "w")
writerClusters.write("LineID, Cluster, Cluster.Lat, Cluster.Long, Days.Used.Combined, Days.Used.Max, Days.Used.Total, Transactions, Cluster.Towers.Members\n")


writerMaxCombinedDaysClusters = open("tables/importantplaces/line_cluster_properties_maxCombinedDuration_9towers_nomax_towermember.txt", "w")
writerMaxCombinedDaysClusters.write("LineID, Cluster, Cluster.Lat, Cluster.Long, Days.Used.Combined, Days.Used.Max, Days.Used.Total, Transactions, Cluster.Towers.Members\n")




dTower_Date_Transactions = butility.TwoStruct()


cLastLineID = ""
for line in reader:
  fields = [ x.strip() for x in line.split(",") ]
  cLineID       =     fields[0]
  nTower        = int(fields[1])
  cDate         =     fields[2]
  nTransactions = int(fields[3])
  
  if not cLineID==cLastLineID and not cLastLineID=="":
    # write out
    computeAndWriteClusters( dTower_Date_Transactions, writerClusters, writerMaxCombinedDaysClusters )
    # purge data structure
    dTower_Date_Transactions = butility.TwoStruct()
    
  
  
  cLastLineID = cLineID
  dTower_Date_Transactions[ nTower ][ cDate ] = nTransactions


computeAndWriteClusters( dTower_Date_Transactions, writerClusters, writerMaxCombinedDaysClusters )

writerClusters.close()
writerMaxCombinedDaysClusters.close()


