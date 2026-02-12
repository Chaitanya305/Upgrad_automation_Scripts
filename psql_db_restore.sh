#!/bin/bash
# psql_host="upgrad-dev-postgres-payment.cscyttgt1cwf.us-east-1.rds.amazonaws.com"
# psql_user="postgres"
# psql_password='3MDRGVogLpcq'


# psql_host="upgrad-staging-postgres-lead-management.cscyttgt1cwf.us-east-1.rds.amazonaws.com"
# psql_user="postgres"
# psql_password='9-hm=),_d9ZEHLO?3Qk$LzjTUzF#f,A5'

# psql_host="ug-nonprod-postgres-dev.cdxjkd3y4d2x.ap-south-1.rds.amazonaws.com"
# psql_user="postgres"
# psql_password='mq9P9mdWrsHs'

# psql_host="upgrad-staging-postgres-payment.cscyttgt1cwf.us-east-1.rds.amazonaws.com"
# psql_user="postgres"
# psql_password='B4VqW<=fl}tGi)j#ypK]R*W|-,)_]0n#'

# psql_host="upgrad-staging-postgres.cscyttgt1cwf.us-east-1.rds.amazonaws.com"
# psql_user="psqladmin"
# psql_password='Qm7t<m%jx3OEnKrj|sLch>YF;5=+;W5!'

psql_host="upgrad-staging-postgres-platform.cscyttgt1cwf.us-east-1.rds.amazonaws.com"
psql_user="psqladmin"
psql_password='RfVvLPeoIoVa'

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