import requests

def is_build_failed(jenkins_url, job_name, build_number, username, api_token):
    url = f"{jenkins_url}/job/{job_name}/{build_number}/api/json"
    
    try:
        response = requests.get(url, auth=(username, api_token))

        if response.status_code == 200:
            build_info = response.json()
            print("Build id is there")
            if build_info.get("result") == "FAILURE":
                return True
            else:
                return False
        elif response.status_code == 404:
            print(f"Build number {build_number} for job '{job_name}' does not exist.")
            return False
        else:
            print(f"Error checking build: HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def check_job_statsu(username, api_token, job_name):
    jenkins_url = "https://zeroops.upgrad.com/jenkins-zeroops"
    #checking if jenkins is up or not
    try:
        response = requests.get(jenkins_url, timeout=5, auth=(username, api_token))  # Set verify=True if using valid SSL
        if response.status_code == 200:
            print("jenkins is up")
        else:
            print("jenkins is down")
            return False
    except Exception as e:
        print("Jenkins not reachable: {}".format(e))
        return False
    job_url = f"{jenkins_url}/job/{job_name}/api/json"
    try:
        job_response = requests.get(job_url, auth=(username, api_token))
        if job_response.status_code == 200:
            print(f"Jenkins job '{job_name}' already exists.")
            return True
        elif job_response.status_code == 404:
            print(f"Jenkins job '{job_name}' does not exist.")
            return False
        else:
            print(f"Unexpected status code: {job_response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to query job: {e}")
        return False
        

jenkins_url = 'https://zeroops.upgrad.com/jenkins-zeroops'
job_name =  'self-service-portal'
build_number = '288'
username = 'chaitanya.ar@upgrad.com'
api_token = '112530bd369'

if is_build_failed(jenkins_url, job_name, build_number, username, api_token):
    print("Job and build id present with failure status")

if check_job_statsu(username, api_token, job_name):
    print("HJob is there")