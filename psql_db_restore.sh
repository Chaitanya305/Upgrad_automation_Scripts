#!/bin/bash

psql_host="upgrad-staging-postgres-platform.cscyttgt1cwf.us-east-1.rds.amazonaws.com"
psql_user="user"
psql_password='pass'

echo "Restoring for DB Host: $psql_host"
export PGPASSWORD="$psql_password"
 
psql_name="referrals"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql

psql_name="sa_dcs"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql


psql_name="dcs"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql


psql_name="document_management"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql


psql_name="kh_leadms"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql


psql_name="leadms"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql


psql_name="otp_service"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql


psql_name="ug_partner_service"
echo "Restoring dump for db $psql_name...."

psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
psql -h $psql_host -U $psql_user $psql_name < dev/$psql_name.sql

#psql -h $psql_host -U $psql_user -d postgres -c "DROP DATABASE IF EXISTS $psql_name"
# psql -h $psql_host -U $psql_user -d postgres -c "CREATE DATABASE $psql_name"
# psql -h $psql_host -U $psql_user $psql_name < dev/payment_service.sql




#drop db is use when need to do clean restore.
# SELECT pg_terminate_backend (pid) FROM	pg_stat_activity where pg_stat_activity.datname = 'one_program_service';
# drop database one_program_service;


#query to provide read write acces to users in postgress 
#GRANT readwrite / readonly to <user>;


#readwire group shoudl also need to have write acces in that db chekc that as well.