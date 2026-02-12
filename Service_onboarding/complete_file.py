import env
import requests
import json
import os

def app_file_content(environment, repo_name, port, university):
    app_file_content = f'''app:
  name: {environment}-{repo_name}
  appid: {environment}-{repo_name}
  environment: {environment}
deployment:
  replicaCount: 1
  image:
    repository: 443370702768.dkr.ecr.ap-south-1.amazonaws.com/{repo_name}
    tag: {university}-{environment}
    pullPolicy: Always
  configMap: {environment}-{repo_name}
  livenessProbe:
    path: /actuator/health
  readinessProbe:
    path: /actuator/health
service:
  type: NodePort
  externalPort: 80
  internalPort: {port}
ingress:
  enabled: true
  class: alb
  host: <TBA>
  annotations:
    alb.ingress.kubernetes.io/group.order: "300"
    alb.ingress.kubernetes.io/group.name: ingress-alb-{environment}-public
'''
    return app_file_content

def app_file_creation(environment, repo_name, university, project_name, techstack):
    #checking port
    if techstack =='java':
        port = '8080'
    if techstack == 'php':
        port = '80'
    if techstack == 'node':
        port = '3000'
    file_content = app_file_content(environment, repo_name, port, university)
    if project_name == 'talentedge':
        file_path = f'apps/{university}/{environment}/{repo_name}.yaml'
        if bitbucket_file_push('te-app-scripts', file_path, file_content):
            print('app file is pushed successfully')
            return True
        else:
            return False
        
def config_file_content(repo_name, environment):
    file_content = f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: {environment}-{repo_name}
  namespace: {environment}-app
  annotations:
    strategy.spinnaker.io/versioned: "false"
data:
  Key: Value'''
    return file_content

def config_file_creation(project_name, university, environment, repo_name):
    file_content = config_file_content(repo_name, environment)
    if project_name == 'talentedge':
        file_path = f'configs/{university}/{environment}/{repo_name}.yaml'
        if bitbucket_file_push('te-app-scripts', file_path, file_content):
            print('config file is pushed successfully')
            return True
        else:
            return False

def jenkins_file_content(data, project_name, techstack):
    if project_name == "talentedge":
        project_name = "te"
    if techstack == "php":
        techstack = "phpBuild"
    elif techstack == "node":
        techstack = "nodeBuild"
    elif techstack == "java":
        techstack = "gradleBuild"
    file_content = f'''@Library('{project_name}-cicd-repo') _
// Define sample Data here, Test Cases: true/false
def {data}
{techstack}(data)
// This single file will be used in CI/CD, No any other script will be executed from this repo
// if you face any issue in CI/CD, reach out to DevOps Team'''
    return file_content

def jenkins_file_creation(repo_name, version, project_name, techstack):
    version = version.split(" ")
    if techstack == "java":
        if "default" not in version and "gradle" in version and "java" in version:
            gradle_version = version[1]
            java_version = version[3]
            image = f'gradle:{gradle_version}-jdk{java_version}'
            run_image = f'openjdk:{java_version}'
            data = f'''data = [
"image": "{image}",
"run_image": "{run_image}",
]'''
            file_content = jenkins_file_content(data, project_name, techstack)
        elif "default" in version:
            data = '''data = [
"KEY": "VALUE",
]'''
            file_content = jenkins_file_content(data, project_name, techstack)
    elif techstack == "node":
        if "default" not in version and "node" in version:
            node_version = version[1]
            if node_version == "18.18.0":
                image = "node:18.18.0"
            elif node_version == "22.12":
                image = "node:22.12-alpine"
            data = f'''data = [
"image": "{image}",
]'''
            file_content = jenkins_file_content(data, project_name, techstack)
        elif "default" in version:
            data = '''data = [
"KEY": "VALUE",
]'''    
            file_content = jenkins_file_content(data, project_name, techstack)
    elif techstack == "php":
        if "default" in version:
            data = '''data = [
"KEY": "VALUE",
]'''
            file_content = jenkins_file_content(data, project_name, techstack)
    #pushing jenkinsfile
    if bitbucket_file_push(repo_name, "Jenkinsfile", file_content):
        print("Jenkins file pushed on bitbucket")
        return True
    else:
        print("failed to push Jenkins file on bitbucket")
        return False


def bitbucket_file_push(repo_name, file_name, content):
    url = f"https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}"
    url = url+"/src"
    data = {
        "message": f"DO-50 {file_name} added",
        "branch": 'master'
    }
    files = {
        file_name: content
    }
    response = requests.post(url, auth=(env.bitbucket_username, env.bitbucket_password), data=data, files=files)
    if response.status_code == 201:
        print(f"{file_name} file added succesfully")
        return True
    else:
        print(f"{file_name} file failed to be added {response.status_code} - {response.text}")
        return False

def bitbucket_repo_creation(repo_name, project_key):
    url = f"https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}"
    payload = {
    "scm": "git",
    "is_private": True,
    "project": {"key": project_key},
    "mainbranch": {"name": "master"}
    }
    headers = {
    "Content-Type": "application/json"
    }
    response = requests.post(url, auth=(env.bitbucket_username, env.bitbucket_password), headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Repository created successfully")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gitignore_path = os.path.join(script_dir, 'gitignore')
        #adding gitignore file
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        if bitbucket_file_push(repo_name, ".gitignore", gitignore_content):
            print("repo created and gitignore file added successfuly")
            return True
        else:
            print("Failed to push gitignore file")
    else:
        print(f"Repository creations failed with status code {response.status_code}. Response: {response.text}")
        return False


def Service_Onboarding():
    #creating repo if not exist
    workspace = "test123-workspace"
    repo_name = "demo-repo-service-onboarding"
    project_name = "talentedge"
    if project_name == "talentedge":
            project_key = "TE"
    techstack = "java"
    university = "common"
    environment = "prod"
    version = "gradle 6.9 java 17"
    #check repo exist or not
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_name}"
    repo_response = requests.get(url, auth=(env.bitbucket_username, env.bitbucket_password))

    if repo_response.status_code == 200:
        print("repo exist")
    elif repo_response.status_code == 404:
        print("repo not exists")
        #create repo
        if bitbucket_repo_creation(repo_name, project_key):
            #push jenkinsfile
            if jenkins_file_creation(repo_name, version, project_name, techstack):
                #push config file
                if config_file_creation(project_name, university, environment, repo_name):
                    #app file push
                    if app_file_creation(environment, repo_name, university, project_name, techstack):
                        print("Service Onboarfing is completed")        
    else:
        print("request failed with code", repo_response.status_code)


Service_Onboarding()