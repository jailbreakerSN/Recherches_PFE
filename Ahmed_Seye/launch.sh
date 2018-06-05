#!/bin/sh
usage="Usage: sh launch.sh [Distri|Merch[daily|weekly|monthly].properties]"
if [ ! "$1" ]; then
  echo $usage
  exit 1
fi
source $1
Transactions=0
Subscribers=0
#Check transaction file in HDFS
while [ $(($Subscribers*$Transactions)) -eq 0 ];
do
   sleep 120
  #Check transaction file in HDFS
  if $(hdfs dfs -test -e $HDFS_TRANSACTIONS_DIR/Transactions_$PROCEES_DAYS.csv) ; then
     echo "Le fichier transaction est disponible : "`date +%Y-%m-%d-%H-%M-%S` >> ${LOG_SH}
     Transactions=1
  else
    echo "le fichier transaction n'est pas encore disponible: "`date +%Y-%m-%d-%H-%M-%S` >> ${LOG_SH}
  fi
  #Check subscribers file in HDFS
  if $(hdfs dfs -test -e $HDFS_SUBSCRIBERS_DIR/Subscribers_$PROCEES_DAYS.csv) ; then
     echo "Le fichier Subscribers est disponible : "`date +%Y-%m-%d-%H-%M-%S` >> ${LOG_SH}
     Subscribers=1
  else
    echo "le fichier Subscribers n'est pas encore disponible : "`date +%Y-%m-%d-%H-%M-%S` >> ${LOG_SH}
  fi
done

echo " Début execution jobs Spark $PROJECT_NAME...  "`date +%Y-%m-%d-%H-%M-%S` >> ${LOG_SH}
  spark-submit --master $MASTER --jars $JARS_FILE  --driver-memory $DRIVER_MEMORY  --class $CLASS $DM_JAR_FILE $DM_CONF_FILE >> ${LOG_SH} 2>&1 &
echo " Fin execution execution jobs Spark DAILY OM PARC "`date +%Y-%m-%d-%H-%M-%S` >> ${LOG_SH}

