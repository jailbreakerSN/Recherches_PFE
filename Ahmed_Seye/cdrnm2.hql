--Transfer CDR temp datas to hourly partitioned table 

--drop table transient.${hiveconf:TABLE};
create TEMPORARY table if not exists transient.${hiveconf:TABLE}( 
Sequence_Number String, 
Version String, 
Switch_Type String, 
Call_Record_Type String, 
Subscription_Type String, 
Call_Termination_Type String, 
Call_Termination_Error_Code String, 
Mobile_Subscriber_Identity String, 
Caller_MSISDN_Type String, 
Caller_MSISDN String, 
Call_Partner_Identity_Type String, 
Call_Partner_Identity String, 
Basic_Service String, 
Bearer_Capability String, 
Call_Date String, 
Call_Time String, 
Call_Duration String, 
MSC_Identity_Type String, 
MSC_Identity String, 
MS_Location_Type String, 
MS_Location String, 
MS_Location_Extension_Type String, 
MS_Location_Extension String, 
Equipment_Identity String, 
Status_of_Equipment String, 
Call_Origin String, 
Channel_Type String, 
Link_Identity String, 
PSTN_Charge String, 
Supplementary_Services String, 
Outgoing_Trunk_Group String, 
Incoming_Trunk_Group String, 
Filler String 
) 
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe' 
WITH SERDEPROPERTIES ("input.regex" = "(.{10})(.{3})(.{1})(.{1})(.{1})(.{1})(.{1})(.{15})(.{1})(.{15})(.{1})(.{15})(.{2})(.{2})(.{8})(.{6})(.{6})(.{1})(.{15})(.{1})(.{18})(.{1})(.{15})(.{15})(.{1})(.{1})(.{1})(.{5})(.{8})(.{8})(.{10})(.{10})(.{37}).*" )   
LOCATION '/dlk/osn/transient/pfs/cdrs/cdrnm/${hiveconf:TABLE}' 
TBLPROPERTIES("skip.footer.line.count"="1"); 
  
SET hive.exec.dynamic.partition.mode=nonstrict;	

FROM transient.${hiveconf:TABLE}
  INSERT INTO TABLE trusted.cdrnm_new PARTITION(Year, Month, Day, Hour, Sens_Trafic, Type_trafic)
SELECT DISTINCT
  trim(Sequence_Number), 
  trim(Version), 
  trim(Switch_Type), 
  trim(Call_Record_Type), 
  trim(Subscription_Type), 
  Call_Termination_Type, 
  Call_Termination_Error_Code, 
  Mobile_Subscriber_Identity, 
  Caller_MSISDN_Type, 
  trim(Caller_MSISDN), 
  trim(Call_Partner_Identity_Type), 
  trim(Call_Partner_Identity), 
  Basic_Service, 
  Bearer_Capability, 
  Call_Date, 
  Call_Time, 
  Call_Duration, 
  MSC_Identity_Type, 
  MSC_Identity, 
  MS_Location_Type, 
  MS_Location, 
  MS_Location_Extension_Type, 
  MS_Location_Extension, 
  Equipment_Identity, 
  Status_of_Equipment, 
  Call_Origin, 
  Channel_Type, 
  Link_Identity, 
  PSTN_Charge, 
  Supplementary_Services, 
  Outgoing_Trunk_Group, 
  Incoming_Trunk_Group, 
  trim(Filler) ,
  
  CASE  Subscription_Type
    WHEN  "3"  THEN 'ROAMER'
    WHEN  "1" THEN 'NOT ROAMER'
    ELSE 'OTHERS'
  END AS Roamer,
  
  trusted.operateur(trim(Call_Partner_Identity),Call_Partner_Identity_Type) 
  AS Operateur,
  
  CASE  substr(trim(Call_Partner_Identity),1,4)
    WHEN  '0191'  THEN IF(Call_Partner_Identity_Type='1',IF(length(trim(Call_Partner_Identity))>=13,substr(Call_Partner_Identity,5,length(Call_Partner_Identity)),''), Call_Partner_Identity)
    WHEN  '0192'  THEN IF(Call_Partner_Identity_Type='1',IF(length(trim(Call_Partner_Identity))>=13,substr(Call_Partner_Identity,5,length(Call_Partner_Identity)),''), Call_Partner_Identity)
    WHEN  '0193'  THEN IF(Call_Partner_Identity_Type='1',IF(length(trim(Call_Partner_Identity))>=13,substr(Call_Partner_Identity,5,length(Call_Partner_Identity)),''), Call_Partner_Identity)
    ELSE trim(Call_Partner_Identity)
  END AS Num_corresp,
  
  CASE  substr(trim(Call_Partner_Identity),1,4)
    WHEN  '0191'  THEN IF(Call_Partner_Identity_Type='1',IF(length(trim(Call_Partner_Identity))>=13,'0191',''), trim(Call_Partner_Identity))
    WHEN  '0192'  THEN IF(Call_Partner_Identity_Type='1',IF(length(trim(Call_Partner_Identity))>=13,'0192',''), trim(Call_Partner_Identity))
    WHEN  '0193'  THEN IF(Call_Partner_Identity_Type='1',IF(length(trim(Call_Partner_Identity))>=13,'0193',''), trim(Call_Partner_Identity))
    ELSE 'DIV'
  END AS Rn_corresp,
  
  substr(Call_Date,1,4) Year,
  substr(Call_Date,5,2) Month,
  substr(Call_Date,1,8) Day,
  substr(Call_Time,1,2) Hour,
  
  CASE  Call_Record_Type
    WHEN  "1"  THEN 'SORTANT'
    WHEN  "2" THEN 'ENTRANT'
    WHEN  "4"  THEN 'SORTANT'
    WHEN  "5" THEN 'ENTRANT'
    WHEN  "6" THEN 'SORTANT'
    ELSE 'OTHERS'
  END AS Sens_Trafic,
  
  CASE  Basic_Service
    WHEN  "11"  THEN 'VOIX'
    WHEN  "12" THEN 'VOIX'
    WHEN  "21"  THEN 'SMS'
    WHEN  "22" THEN 'SMS'
    ELSE 'NA'
  END AS Type_trafic;
  
--drop table transient.${hiveconf:TABLE};
