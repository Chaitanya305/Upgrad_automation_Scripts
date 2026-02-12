import os
import requests
import json
bitbucket_username = "test123-workspace-admin"
bitbucket_password = "ATBBNb2vTs7Kh9x5BBLCSshJaPvG42121258"


def push_file(repo_name, file_name, content, branch):
    #repo_name = "test-poc-repo"
    url = f"https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}"
    url = url+"/src"
    data = {
        "message": f"DO-50 {file_name} added",
        "branch": branch
    }
    files = {
        file_name: content
    }
    response = requests.post(url, auth=(bitbucket_username, bitbucket_password), data=data, files=files)
    if response.status_code == 201:
        print(f"{file_name} file added succesfully")
    else:
        print(f"{file_name} file failed to be added {response.status_code} - {response.text}")

def jenkins_file_creation():
    if os.path.exists("build.gradle"):
        print('Identified as Gradle project...')
        jenkinsfile = "gradleBuild"

    if os.path.exists("server.php") or os.path.exists("index.php"):
        print('Identified as php project...')
        jenkinsfile = "phpBuild"

    if os.path.exists("package.json"):
        print('Identified as Node project...')
        jenkinsfile = "nodeBuild"

    project_name = "te"
    #image = "gradle:6.9-jdk17"
    #run_image = "openjdk:17"
    java = "22"
    gradle = "9"
    data = f'''data = [
"image": "gradle:{gradle}-jdk{java}",
"run_image": "openjdk:{java}",
]'''
    jenkins_file_content = f'''@Library('{project_name}-cicd-repo') _
// Define sample Data here, Test Cases: true/false
def {data}
{jenkinsfile}(data)
// This single file will be used in CI/CD, No any other script will be executed from this repo
// if you face any issue in CI/CD, reach out to DevOps Team'''
    
    #push_file("test-poc-repo", "files/Jenkinsfile", jenkins_file_content, "master")
    with open("jenkinsfile", "w") as f:
        f.write(jenkins_file_content)

    print("Jenkins file generated...")
    #will add jenkins file at bitbucket
# will add gitignore file to the repo
    # repo_name = "test-poc-repo"
    # url = f"https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}"
    # url = url+"/src"
    # data = {
    #     "message": "adding jenkins file",
    #     "branch": "master"
    # }
    # files = {
    #     "Jenkinsfile": jenkins_file_content
    # }
    # response = requests.post(url, auth=(bitbucket_username, bitbucket_password), data=data, files=files)
    # if response.status_code == 201:
    #     print("jenkins file added succesfully")
    # else:
    #     print(f"jenkins failed to be added {response.status_code} - {response.text}")

jenkins_file_creation()




