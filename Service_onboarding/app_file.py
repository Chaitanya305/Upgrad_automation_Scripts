import json
import io

repo_name = "service-onboarding-poc"
ENV= "prod"

def adding_secrets(secret_keys, app_file_content):
    # List of secret keys
    secret_keys = secret_keys.split(" ")
    #secret_keys = ["DB_PASSWORD", "API_KEY", "TOKEN"]

    extra_envs = "extraEnvs:\n"
    for key in secret_keys:
        extra_envs += f"  - name: {key}\n"
        extra_envs += f"    valueFrom:\n"
        extra_envs += f"      secretKeyRef:\n"
        extra_envs += f"        name: secrets-{ENV}-app\n"
        extra_envs += f"        key: {key}\n"
    # Define the structure of the values.yaml
    # values_data = {
    # "extraEnvs": [
    #     {
    #         "name": key,
    #         "valueFrom": {
    #             "secretKeyRef": {
    #                 "name": f"secrets-{ENV}-app",
    #                 "key": key
    #             }
    #         }
    #     }
    #     for key in secret_keys
    # ]
    # }
    # # Write to values.yaml
    # #with open("app.yaml", "a") as file:
    # #yaml.dump(values_data, app_file_content, default_flow_style=False, sort_keys=False)
    # secrets_yaml_stream = io.StringIO()
    # json.dump(values_data, secrets_yaml_stream, default_flow_style=False, sort_keys=False)
    # secrets_yaml_content = secrets_yaml_stream.getvalue()

    # Append the secrets YAML to app_file_content
    #updated_content = app_file_content + secrets_yaml_content
    updated_content = app_file_content + extra_envs

    print("Secrets added to app.yaml content (in memory)")
    return updated_content
    print("secrets added to app.yaml")


app_file_content = f'''app:
  name: {ENV}-{repo_name}
  appid: {ENV}-{repo_name}
  environment: {ENV}
deployment:
  replicaCount: 1
  image:
    repository: 443370702768.dkr.ecr.ap-south-1.amazonaws.com/{repo_name}
    tag: common-prod
    pullPolicy: Always
  configMap: {ENV}-{repo_name}
  livenessProbe:
    path: /actuator/health
  readinessProbe:
    path: /actuator/health
service:
  type: NodePort
  externalPort: 80
  internalPort: 8080
ingress:
  enabled: true
  class: alb
  host: degrees-kuber.lmscontent.in
  annotations:
    alb.ingress.kubernetes.io/group.order: "300"
    alb.ingress.kubernetes.io/group.name: ingress-alb-{ENV}-public'''

# with open("app.yaml", "w") as file:
#     file.write(app_file_content)
secrets = input("Secrets need to be added YES/NO: ")
if secrets:
    secret_keys = input("Provide secrets env keys with space as seprated :")
    app_file_content = adding_secrets(secret_keys, app_file_content)
    print(app_file_content)
with open("app.yaml", "w") as file:
    file.write(app_file_content)

print("app file created ...")