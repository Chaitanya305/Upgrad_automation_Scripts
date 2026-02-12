import requests
import json
import urllib.parse
bitbucket_username = "test123-workspace-admin"
bitbucket_password = "Bitbucket token here"

def check_repo():
    repo_name = "demo-repo-pipeline"
    url = f"https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}"
    response = requests.get(url, auth=(bitbucket_username, bitbucket_password))

    if response.status_code == 200:
        print("repo exist")
    elif response.status_code == 404:
        print("repo not exists")
    else:
        print("request failed with code", response.status_code)


def create_repo(repo_name, project_key):
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
    response = requests.post(url, auth=(bitbucket_username, bitbucket_password), headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        # will add gitignore file to the repo
        url = url+"/src"
        with open("gitignore", 'r') as f:
            gitignore_content = f.read()
        data = {
            "message": "Initial commit",
            "branch": "master"
        }
        files = {
            ".gitignore": gitignore_content
        }
        response = requests.post(url, auth=(bitbucket_username, bitbucket_password), data=data, files=files)
        if response.status_code == 201:
            print("gitignore added succesfully")
        else:
            print(f"gitignore failed to be added {response.status_code} - {response.text}")
        print("Repository created successfully")



    else:
        print(f"Request failed with status code {response.status_code}. Response: {response.text}")

def check_branch(repo_name, branch_name):
    encoded_branch_name = urllib.parse.quote(branch_name, safe='')
    print(encoded_branch_name)
    branch_url = f'https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}/refs/branches/{encoded_branch_name}'
    response = requests.get(branch_url, auth=(bitbucket_username, bitbucket_password))
    if response.status_code == 200:
        print(f"Branch '{branch_name}' exists.")
        #fetch file at barnch
        branch_data = response.json()
        commit_hash = branch_data.get("target", {}).get("hash")
        if not commit_hash:
            print("Could not find commit hash for the branch.")
            return
        
        print(f"Commit hash: {commit_hash}")
        #fetch_file_url = f'https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}/src/{encoded_branch_for_src}/'
        fetch_file_url = f'https://api.bitbucket.org/2.0/repositories/test123-workspace/{repo_name}/src/{commit_hash}/'
        response = requests.get(fetch_file_url, auth=(bitbucket_username, bitbucket_password))
        if response.status_code == 200:
            data = response.json()
            files = [entry["path"] for entry in data.get("values", [])]
            print('list of file are', files)
        else:
            print("failed to fetch files")
            print(f"File fetch status: {response.status_code}")
            print(f"Response text: {response.text}")
    else:
        print("Branch {branch_name} notexists.")


#create_repo("test-repo-poc", "TE")
check_branch("test-repo-poc", 'dev')