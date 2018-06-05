import sys
import collections
import datetime
import sys
import pp


import butility
import btransactioniterators

sys.path.append("/home/danbjork/analysis/towers/distance/")
from tower_location_data import *
from tower_location_data_predicted import *





#
# 1. COMPUTE MOBILITY
#

dLineID_Tower_Date_Transactions            = butility.nThreeStruct()
# d[lineid][tower][date] = transactions
dLineID_Tower_TimeOfDayBucket_Transactions = butility.nThreeStruct()
# d[lineid][tower][time of day bucket] = transactions



def classifyTimeBucket( dtTime ):
  nHour      = dtTime.hour
  nDayOfWeek = dtTime.weekday()
  
  if nHour >= 9 and nHour < 12 and (nDayOfWeek==0 or nDayOfWeek==1 or nDayOfWeek==2 or nDayOfWeek==3 or nDayOfWeek==4):
    return 1
  elif nHour >= 14 and nHour < 17 and (nDayOfWeek==0 or nDayOfWeek==1 or nDayOfWeek==2 or nDayOfWeek==3): # government off on friday afternoons, so don't count
    return 2
  elif nHour < 7 or nHour > 19:
    return 3
  else:
    return 0




def ppComputeMobility(YM, GLOBALS):
  print("Worker started:" + YM)
  iterMobility = btransactioniterators.MobilityIterator( [YM] )
  
  #dLineProperties = GLOBALS[0]
  local_dLineID_Tower_Date_Transactions            = butility.nThreeStruct()
  local_dLineID_Tower_TimeOfDayBucket_Transactions = butility.nThreeStruct()
  
  
  for (dtTransaction, cLineID, nTower) in iterMobility:
    try:
      local_dLineID_Tower_Date_Transactions[ cLineID ][ nTower ][ int(dtTransaction.strftime("%y%m%d")) ] += 1 # note transaction
      local_dLineID_Tower_TimeOfDayBucket_Transactions[ cLineID ][ nTower ][ classifyTimeBucket(dtTransaction) ] += 1
    except (IndexError, KeyError):
      print("Index/Key Error\n")
      continue
  
  return (local_dLineID_Tower_Date_Transactions, local_dLineID_Tower_TimeOfDayBucket_Transactions)
  



YMs = ['0501', '0502', '0503', '0504', '0505', '0506', '0507', '0508', '0509', '0510', '0511', '0512', '0601', '0602', '0603', '0604', '0605', '0606', '0607', '0608', '0609', '0610', '0611', '0612', '0701', '0702', '0703', '0704', '0705', '0706', '0707', '0708', '0709', '0710', '0711', '0712', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '0810', '0811', '0812', '0901', '0902', '0903', '0904', '0905' ]

GLOBALS = ()


# START PARALLEL PROCESSING ENGINE
ppservers = ()
# Creates jobserver with min(32,#YM) workers (revan has 32)
#job_server = pp.Server( min(len(YMs), 32), ppservers=ppservers)
job_server = pp.Server( 10, ppservers=ppservers)
print "Starting pp with", job_server.get_ncpus(), "workers"

# LOAD JOBS
jobs = [ (YM, job_server.submit(ppComputeMobility, (YM, GLOBALS), (classifyTimeBucket,), ( "errorManager", "collections", "butility", "btransactioniterators", "datetime")) ) for YM in YMs ]

# COMBINE
for YM, job in jobs:
  # map
  (local_dLineID_Tower_Date_Transactions, local_dLineID_Tower_TimeOfDayBucket_Transactions) = job()
  
  # reduce
  for cLineID, dTemp1 in local_dLineID_Tower_Date_Transactions.iteritems():
    for nTower, dTemp2 in dTemp1.iteritems():
      for cDate, nCount in dTemp2.iteritems():
        dLineID_Tower_Date_Transactions[ cLineID ][ nTower ][ cDate ] += nCount
  
  for cLineID, dTemp1 in local_dLineID_Tower_TimeOfDayBucket_Transactions.iteritems():
    for nTower, dTemp2 in dTemp1.iteritems():
      for nTimeBucket, nCount in dTemp2.iteritems():
        dLineID_Tower_TimeOfDayBucket_Transactions[ cLineID ][ nTower ][ nTimeBucket ] += nCount


# RUN BY HAND
# for YM in ['0502', '0503', '0504', '0505', '0506', '0507', '0508', '0509', '0510', '0511', '0512', '0601', '0602', '0603', '0604', '0605', '0606', '0607', '0608', '0609', '0610', '0611', '0612', '0701', '0702', '0703', '0704', '0705', '0706', '0707', '0708', '0709', '0710', '0711', '0712', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '0810', '0811', '0812', '0901', '0902', '0903', '0904', '0905']:
#   
#   (local_dLineID_Tower_Date_Transactions, local_dLineID_Tower_TimeOfDayBucket_Transactions) = ppComputeMobility(YM, () )
#   
#   # reduce
#   for cLineID, dTemp1 in local_dLineID_Tower_Date_Transactions.iteritems():
#     for nTower, dTemp2 in dTemp1.iteritems():
#       for cDate, nCount in dTemp2.iteritems():
#         dLineID_Tower_Date_Transactions[ cLineID ][ nTower ][ cDate ] += nCount
#   
#   for cLineID, dTemp1 in local_dLineID_Tower_TimeOfDayBucket_Transactions.iteritems():
#     for nTower, dTemp2 in dTemp1.iteritems():
#       for nTimeBucket, nCount in dTemp2.iteritems():
#         dLineID_Tower_TimeOfDayBucket_Transactions[ cLineID ][ nTower ][ nTimeBucket ] += nCount




# for (dtTransaction, cLineID, nTower) in iterMobility:
#   dLineID_Tower_Date_Transactions[ cLineID ][ nTower ][ dtTransaction.strftime("%y%m%d") ] += 1 # note transaction
#   dLineID_Tower_TimeOfDayBucket_Transactions[ cLineID ][ nTower ][ enumTimeOfDayBucket.classifyTimeBucket(dtTransaction) ] += 1





writerTowerDateTransactions = open("tables/importantplaces/line_tower_date_transactions.txt", "w")
writerTowerDateTransactions.write("LineID, Tower, Date, Transactions\n" )
for cLineID, dTemp1 in dLineID_Tower_Date_Transactions.iteritems():
  for nTower, dTemp2 in dTemp1.iteritems():
    for nDate, nCount in dTemp2.iteritems():
      writerTowerDateTransactions.write(",".join([cLineID, str(nTower), "0" + str(nDate), str(nCount)]) + "\n" )

writerTowerDateTransactions.close()



writerTowerDaysTransactions = open("tables/importantplaces/line_tower_days_transactions.txt", "w")
writerTowerDaysTransactions.write("LineID, Tower, Days.Used, Transactions\n" )
for cLineID, dTemp1 in dLineID_Tower_Date_Transactions.iteritems():
  for nTower, dTemp2 in dTemp1.iteritems():
    nDays       = len(dTemp2)
    nTotalCount = 0
    for nDate, nCount in dTemp2.iteritems():
      nTotalCount += nCount
    
    writerTowerDaysTransactions.write(",".join([cLineID, str(nTower), str(nDays), str(nTotalCount)]) + "\n" )

writerTowerDaysTransactions.close()



writerTowerBucketTransactions = open("tables/importantplaces/line_tower_timebucket_transactions.txt", "w")
writerTowerBucketTransactions.write("LineID, Tower, TimeBucket, Transactions\n" )
for cLineID, dTemp1 in dLineID_Tower_TimeOfDayBucket_Transactions.iteritems():
  for nTower, dTemp2 in dTemp1.iteritems():
    for nTimeBucket, nCount in dTemp2.iteritems():
      writerTowerBucketTransactions.write(",".join([cLineID, str(nTower), str(nTimeBucket), str(nCount)]) + "\n" )

writerTowerBucketTransactions.close()



print "Time elapsed: ", time.time() - start_time, "s"
job_server.print_stats()



