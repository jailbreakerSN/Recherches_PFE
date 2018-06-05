import collections
import sys
sys.path.append("/home/danbjork/analysis/towers/distance/")
sys.path.append("/home/dbjorkeg/analysis/towers/distance/")

from tower_distance_data_predicted import *
from tower_distance_data import *



dTower_aDistances = collections.defaultdict(list)


# find nearest towers
for nTowerFrom in tower_dist_predicted.iterkeys(): # loop over ALL towers (including predicted)
  for nTowerTo, fDistance in tower_dist_predicted[ nTowerFrom ].iteritems():
    if nTowerTo in tower_dist: # but only consider distance to known towers
      dTower_aDistances[ nTowerFrom ].append( fDistance )

# write 

nFurthestTowerToCompute = 50

writer = open("tables/bDistanceToNearestTowerByTower.txt", "w")
for nTower in dTower_aDistances.iterkeys():
  dTower_aDistances[ nTower ].sort()
  # write out distance to nearest 1,2,3,...nFurthestTowerToCompute towers. note that [0] will be self, so skip that.
  writer.write(str(nTower) + "," + ",".join( [ str(dTower_aDistances[nTower][x]) for x in range(1,nFurthestTowerToCompute+1) ]) + "\n")


writer.close()

