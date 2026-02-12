def mysql_acces(client, dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name, dbpass):
    #check user exist or not
    user_exist_cmd = '''mysql -h {} -u {} -p{} -Bse "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{}')"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name)
    stdin3, stdout3, stderr3 = client.exec_command(user_exist_cmd)
    user_exist = stdout3.read().decode().strip()
    if user_exist == "0":
        print("creating user", user_name)
        create_user_cmd = '''mysql -h {} -u {} -p{} -e "CREATE USER '{}'@'%' IDENTIFIED BY '{}'"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name, dbpass)
        stdin4, stdout4, stderr4 = client.exec_command(create_user_cmd)
    else:
        print("Altering user's password for ", user_name)
        alter_password_cmd = '''mysql -h {} -u {} -p{} -e "ALTER USER '{}'@'%' IDENTIFIED BY '{}'"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name, dbpass)
        stdin5, stdout5, stderr5 = client.exec_command(alter_password_cmd)
    print("Granting Access for", user_name)
    grant_access_cmd = '''mysql -h {} -u {} -p{} -e "GRANT SELECT, INSERT, UPDATE, DELETE ON *.* TO '{}'@'%'"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name)
    stdin6, stdout6, stderr6 = client.exec_command(grant_access_cmd)


def psql_access(client, dev_psql_password, dev_psql_host, dev_psql_user_name, user_name, dbpass):
    user_exist_cmd = '''PGPASSWORD={} psql -t -h {} -U {} -d postgres -c "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='{}')"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name)
    psqlin3, psqlout3, psqlerr3 = client.exec_command(user_exist_cmd)
    user_exist = psqlout3.read().decode().strip()
    if user_exist == "f":
        print("creating user", user_name)
        create_user_cmd = '''PGPASSWORD={} psql -h {} -U {} -d postgres -c "CREATE ROLE {} WITH PASSWORD '{}' LOGIN"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name, dbpass)
        psqlin4, psqlout4, psqlerr4 = client.exec_command(create_user_cmd)
    else:
        print("Altering user's password for", user_name)
        alter_password_cmd = '''PGPASSWORD={} psql -h {} -U {} -d postgres -c "ALTER USER {} WITH PASSWORD '{}'"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name, dbpass)
        psqlin4, psqlout4, psqlerr4 = client.exec_command(alter_password_cmd)
    #execute sleep command
    sleep_command = '''sleep 5'''
    psqlin6, psqlout6, psqlerr6 = client.exec_command(sleep_command)
    print("Granting permission to user for", user_name)
    grant_access_cmd = '''PGPASSWORD={} psql -h {} -U {} -d postgres -c "GRANT readwrite TO {}"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name)
    psqlin5, psqlout5, psqlerr5 = client.exec_command(grant_access_cmd)


def grant_db_access(user_name, dbpass, env):
    import paramiko
    import os
    from paramiko import RSAKey

    hostname = "43.204.119.211"
    port = 22
    username = "ubuntu"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pem_file_path = os.path.join(script_dir, 'ug-nonprod.pem')
    #key_file = pem_file_path
    key = RSAKey.from_private_key_file(pem_file_path)
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect using key
        client.connect(hostname, port, username, pkey=key)

        #mysql access
        if env == "dev":
            pass
            # dev_mysql_host = "ug-nonprod-mysql-dev.cdxjkd3y4d2x.ap-south-1.rds.amazonaws.com"

            # stdin1, stdout1, stderr1 = client.exec_command("aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-south-1:635145294553:secret:dev-oms-yiWf9j --region ap-south-1 | jq --raw-output '.SecretString' | jq -r .LEARN_USERNAME")
            # dev_mysql_user_name = stdout1.read().decode().strip()

            # stdin2, stdout2, stderr2 = client.exec_command("aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-south-1:635145294553:secret:dev-oms-yiWf9j --region ap-south-1 | jq --raw-output '.SecretString' | jq -r .LEARN_PASSWORD")
            # dev_mysql_password = stdout2.read().decode().strip()

            # mysql_acces(client, dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name, dbpass)

            # #check user exist or not
            # user_exist_cmd = '''mysql -h {} -u {} -p{} -Bse "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{}')"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name)
            # stdin3, stdout3, stderr3 = client.exec_command(user_exist_cmd)
            # user_exist = stdout3.read().decode().strip()

        # if user_exist == "0":
        #     print("creating user", user_name)
        #     create_user_cmd = '''mysql -h {} -u {} -p{} -e "CREATE USER '{}'@'%' IDENTIFIED BY '{}'"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name, dbpass)
        #     stdin4, stdout4, stderr4 = client.exec_command(create_user_cmd)
        # else:
        #     print("Altering user's password for ", user_name)
        #     alter_password_cmd = '''mysql -h {} -u {} -p{} -e "ALTER USER '{}'@'%' IDENTIFIED BY '{}'"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name, dbpass)
        #     stdin5, stdout5, stderr5 = client.exec_command(alter_password_cmd)
        # print("Granting Access for", user_name)
        # grant_access_cmd = '''mysql -h {} -u {} -p{} -e "GRANT SELECT, INSERT, UPDATE, DELETE ON *.* TO '{}'@'%'"'''.format(dev_mysql_host, dev_mysql_user_name, dev_mysql_password, user_name)
        # stdin6, stdout6, stderr6 = client.exec_command(grant_access_cmd)
        if env == "stage":
            mysql_stage_platform_host = "ug-nonprod-mysql-stage-platform.cdxjkd3y4d2x.ap-south-1.rds.amazonaws.com"

            # stdin1, stdout1, stderr1 = client.exec_command("aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-south-1:635145294553:secret:stage-acquisition-H3E7nu --region ap-south-1 | jq --raw-output '.SecretString' | jq -r .LEARN_USERNAME")
            # mysql_stage_platform_user_name = stdout1.read().decode().strip()
            mysql_stage_platform_user_name = "mysqllearnadmin"

            # stdin2, stdout2, stderr2 = client.exec_command("aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-south-1:635145294553:secret:stage-acquisition-H3E7nu--region ap-south-1 | jq --raw-output '.SecretString' | jq -r .LEARN_PASSWORD")
            # mysql_stage_platform_password = stdout2.read().decode().strip()
            mysql_stage_platform_password = "04VnaNo433KL"
            mysql_acces(client, mysql_stage_platform_host, mysql_stage_platform_user_name, mysql_stage_platform_password, user_name, dbpass)

        #psql access 
        if env == "dev":
            pass
        #     dev_psql_host = "ug-nonprod-postgres-dev.cdxjkd3y4d2x.ap-south-1.rds.amazonaws.com"
            
        #     psqlin1, psqlout1, psqlerr1 = client.exec_command("aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-south-1:635145294553:secret:dev-oms-yiWf9j --region ap-south-1 | jq --raw-output '.SecretString' | jq -r .PAYMENT_USERNAME")
        #     dev_psql_user_name = psqlout1.read().decode().strip()

        #     psqlin2, psqlout2, psqlerr2 = client.exec_command("aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:ap-south-1:635145294553:secret:dev-oms-yiWf9j --region ap-south-1 | jq --raw-output '.SecretString' | jq -r .PAYMENT_PASSWORD")
        #     dev_psql_password = psqlout2.read().decode().strip()
            #setting psql password
            # set_pass_cmd = '''export PGPASSWORD="${}"'''.format(dev_psql_password)
            # psqlin3, psqlout3, psqlerr3 = client.exec_command(set_pass_cmd)

            # user_exist_cmd = '''PGPASSWORD={} psql -t -h {} -U {} -d postgres -c "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='{}')"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name)
            # psqlin3, psqlout3, psqlerr3 = client.exec_command(user_exist_cmd)

            # user_exist = psqlout3.read().decode().strip()
            # if user_exist == "f":
            #     print("creating user", user_name)
            #     create_user_cmd = '''PGPASSWORD={} psql -h {} -U {} -d postgres -c "CREATE ROLE {} WITH PASSWORD '{}' LOGIN"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name, dbpass)
            #     psqlin4, psqlout4, psqlerr4 = client.exec_command(create_user_cmd)
            # else:
            #     print("Altering user's password for", user_name)
            #     alter_password_cmd = '''PGPASSWORD={} psql -h {} -U {} -d postgres -c "ALTER USER {} WITH PASSWORD '{}'"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name, dbpass)
            #     psqlin4, psqlout4, psqlerr4 = client.exec_command(alter_password_cmd)

            # #execute sleep command
            # sleep_command = '''sleep 5'''
            # psqlin6, psqlout6, psqlerr6 = client.exec_command(sleep_command)
            # print("Granting permission to user for", user_name)
            # grant_access_cmd = '''PGPASSWORD={} psql -h {} -U {} -d postgres -c "GRANT readwrite TO {}"'''.format(dev_psql_password, dev_psql_host, dev_psql_user_name, user_name)
            # psqlin5, psqlout5, psqlerr5 = client.exec_command(grant_access_cmd)
            
    finally:
        client.close()
        print("SSH connection closed.")



grant_db_access("chaitanyagolhar", "pass12345", "stage")