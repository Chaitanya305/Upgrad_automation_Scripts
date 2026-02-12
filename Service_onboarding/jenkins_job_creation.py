#pip install python-jenkins
#here will create jenkins job 
import jenkins

#jenkins_url = 'https://zeroops.upgrad.com/jenkins-zeroops'
jenkins_url = 'http://13.218.103.89/jenkins-zeroops'
username = 'chaitanya.golhar@upgrad.com'
#password_or_api_token = '1125c5ba5c78855ce24ab80375bd0bd369'
password_or_api_token = '11901fa81aa0e7e0f9a447db78d8c2a24d'
#password_or_api_token = '11cefe0f4cda7debcb9deb4a44b90c9f85' #new upgrad one
#connecting to server
server = jenkins.Jenkins(jenkins_url, username=username, password=password_or_api_token)
job_name = 'upgrad-testing-api'
existing_job = 'poc-job'
new_repo_url = 'git@bitbucket.org:upgrad_dev/{}.git'.format(job_name)
if server.job_exists(job_name):
    print(f"Job '{job_name}' already exists.")
else:
    print("job not exist", job_name)
    config_xml = server.get_job_config(existing_job)
    updated_config_xml = config_xml.replace(
    'git@bitbucket.org:upgrad_dev/pedagogy.git',
    new_repo_url)
    print("Creating new job: {}".format(job_name))
    server.create_job(job_name, updated_config_xml)
    print(f"Done! Visit: {jenkins_url}/job/{job_name}/")

