repo_name = "service-onboarding-poc"
ENV= "prod"
configmap_file_content = f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: {repo_name}
  namespace: {ENV}-app
  annotations:
    strategy.spinnaker.io/versioned: "false"
data:
  Key: Value
'''

with open("config.yaml","w") as f:
    f.write(configmap_file_content)

print("configmap is created ...")