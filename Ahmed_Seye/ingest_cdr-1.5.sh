#!/bin/sh
usage="Usage: sh ingest_cdr.sh [cdr[nm|gh].properties]"

if [ ! "$1" ]; then
  echo $usage   
  exit 1
fi

source $1
#FILE_MASK=$CDR_NAME| tr  '[:lower:]' '[:upper:]'
TEMP_DIR_PAR_TIME=`date +$CDR_NAME"_"%Y%m%d%H%M`
TEMP_DIR_PAR=$TEMP_DIR/$TEMP_DIR_PAR_TIME
MSG1='MOVING DATA FROM[`'$TEMP_DIR_PAR'`]TO[`'$HDFS_TRANSIENT_DIR'`]'
MSG2='EXECUTING HIVE SCRIPT[`'$HIVE_TRUSTED_SCRIPT'`]'
MSG3='DELETING DATA FROM[`'$HDFS_TRANSIENT_DIR'`]'
MSG4='MOVING DATA FROM[`'$CDR_DIR/$FILE_MASK'`]TO[`'$TEMP_DIR_PAR'`]'
MSG5='ARCHIVE IN GZIP FORMAT TO[`'$HDFS_RAW_DIR'`]'
MSG6='TASK '
#if $(test -e $TEMP_DIR/.IN_PROGRESS) ; then
#echo -e $MSG6: '\t [IN PROGRESS]'
#else
year=`date +%Y`
#TEMP_DIR_PAR_TIME=`date +tmp_%H-%M`
#TEMP_DIR_PAR=$TEMP_DIR/$TEMP_DIR_PAR_TIME
echo -e $MSG4: ' \t [IN PROGRESS]'   
#echo -e ssh mediation@master1 'mv $CDR_DIR/$FILE_MASK* $TEMP_DIR'
mkdir $TEMP_DIR_PAR
#mv $CDR_DIR/$FILE_MASK $TEMP_DIR_PAR  
#NUMBER_OF_FILES=80;
for i in "${CDR_DIR}"/$FILE_MASK*; do
  [ "$((NUMBER_OF_FILES--))" = 0 ] && break
  mv -t "${TEMP_DIR_PAR}" -- "$i"
done 

if [ $? -eq 0 ]; then 
echo -e $MSG4:' \t [OK]'
echo -e  $MSG1:' \t [IN PROGRESS]'
#touch  $TEMP_DIR/.IN_PROGRESS   
#Managing duplicate file
#ls $TEMP_DIR | while read f; do
#echo -e $f
#prefixed=`echo $f|cut -c $PREFIXE`
#echo -e  hdfs dfs -test -e $HDFS_RAW_DIR/$year/$CDR_NAME'_'$prefixed/$f.zip
#if $(hdfs dfs -test -e $HDFS_RAW_DIR/$year/$CDR_NAME'_'$prefixed/$f.zip) ; then
#   echo -e "$HDFS_RAW_DIR/$year/$CDR_NAME_$prefixed/$f.zip is archived: \t [DUPLICATE]"
#else
#    echo "$f in  $HDFS_TRANSIENT_DIR "
#    hdfs dfs -copyFromLocal -f $TEMP_DIR/$f  $HDFS_TRANSIENT_DIR
#fii
#done
#pwd
hdfs dfs -copyFromLocal -f $TEMP_DIR_PAR  $HDFS_TRANSIENT_DIR 
#touch  $TEMP_DIR/.IN_PROGRESS   
if [ $? -eq 0 ]; then
    echo -e $MSG1:' \t [OK]' # >>{LOG_SH} 2>&1 &
    hdfs dfs -ls  $HDFS_TRANSIENT_DIR/$TEMP_DIR_PAR_TIME  
    echo -e $MSG2:' \t [IN PROGRESS]'   
    echo -e 'hive -hiveconf TABLE='$TEMP_DIR_PAR_TIME '-f' $HIVE_CREATE_TABLE
    hive --hiveconf TABLE=$TEMP_DIR_PAR_TIME -f $HIVE_TRUSTED_SCRIPT  
    if [ $? -eq 0 ]; then
       echo -e $MSG2:' \t [OK]'  
       echo -e $MSG5:' \t [IN PROGRESS]' 
       ##cd $TEMP_DIR
       #year=`date +%Y`
       ls $TEMP_DIR_PAR | while read f; do
	  prefixe=`echo $f|cut -c $PREFIXE`
          # case cdrgh with 2 file format
          if [ "$CDR_NAME" == "cdrgh" ]; then
             cat=`echo $f|cut -c 6-6`
             if [ "$cat" == "4" ]; then
                prefixe=`echo $f|cut -c 9-11`
             else 
                prefixe=`echo $f|cut -c 8-10`
             fi
          fi
          if $(hdfs dfs -test -d $HDFS_RAW_DIR/$year/$CDR_NAME'_'$prefixe) ; then
             echo "$HDFS_RAW_DIR/$year/$CDR_NAME"_"$prefixe exists"   
          else
             echo "$HDFS_RAW_DIR/$year/$CDR_NAME"_"$prefixe created"  
             hdfs dfs -mkdir -p  $HDFS_RAW_DIR/$year/$CDR_NAME'_'$prefixe  
          fi 
          if [[ ${f: -3} == ".gz" ]];  then 
               echo -e  $f 'is gzip';
               #gzip -1 $TEMP_DIR_PAR/$f
               hdfs dfs -moveFromLocal  $TEMP_DIR_PAR/$f $HDFS_RAW_DIR/$year/$CDR_NAME'_'$prefixe/
          else
	          gzip -1 $TEMP_DIR_PAR/$f
              #zip $TEMP_DIR/$f.zip $TEMP_DIR/$f
	          ##echo $f
              hdfs dfs -moveFromLocal  $TEMP_DIR_PAR/$f.gz $HDFS_RAW_DIR/$year/$CDR_NAME'_'$prefixe/
              #rm $TEMP_DIR/$f.gz
	          #hdfs dfs -rm -skipTrash $HDFS_TRANSIENT_DIR/$f
              #rm $TEMP_DIR/$f
          fi 
       done
       echo -e $MSG5: '\t [OK]'  
       echo -e $MSG3:' \t [IN PROGRESS]'
       rm -r $TEMP_DIR_PAR
       hdfs dfs -rm -r -skipTrash $HDFS_TRANSIENT_DIR/$TEMP_DIR_PAR_TIME
       #rm $TEMP_DIR/.IN_PROGRESS
       if [ $? -eq 0 ]; then
          echo -e $MSG3:' \t [OK]'  
       else
           echo -e $MSG3:' \t [KO]'
           #rm $TEMP_DIR/.IN_PROGRESS  
       fi
    else
        ## add after the hiveQL failed
        hdfs dfs -rm -r -skipTrash $HDFS_TRANSIENT_DIR/$TEMP_DIR_PAR_TIME
        #rm $TEMP_DIR/.IN_PROGRESS
        echo -e  $MSG2:' \t [KO]'  
    fi
else
    echo -e  $MSG1:' \t [KO]'  
    #rm $TEMP_DIR/.IN_PROGRESS
fi
else 
echo -e  $MSG4:' \t [KO]'   

fi
#fi
