# Databricks notebook source
!pip install azure.identity

# COMMAND ----------

# Getting the authentication secrets from Databricks scope
client_id = dbutils.secrets.get(scope="mlops",key="client_id")
client_secret = dbutils.secrets.get(scope="mlops",key="client_secret")
tenant_id = dbutils.secrets.get(scope="mlops",key="tenant_id")
scope = dbutils.secrets.get(scope="mlops",key="scope")

# COMMAND ----------

from azure.identity import ClientSecretCredential, InteractiveBrowserCredential, UsernamePasswordCredential

# Function to get access token by providing authentication secrets
def get_access_token(client_id,client_secret,tenant_id,scope="https://analysis.windows.net/powerbi/api/.default"):
    client_secret_credential_class = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    access_token_class = client_secret_credential_class.get_token(scope)
    access_token_string = access_token_class.token
    print("Access Token Created....")
    return access_token_string

# COMMAND ----------

import json
import requests
from datetime import datetime

# Function to refresh dataset by providing access token along with workspace and dataset name
def refresh_dataset(access_token,workspace_name,dataset_name):
  header = {'Authorization': f'Bearer {access_token}'}
  try :
      workspace_request_url = 'https://api.powerbi.com/v1.0/myorg/groups'
      workspaces_request_response = json.loads(requests.get(url=request_url, headers=header).content)
  except Exception as error :
      print("Request Error : ",error)
      return []
  try :
      workspace_id = [workspace_content['id'] for workspace_content in workspaces_request_response['value'] if workspace_content['name'] == workspace_name][0]
  except:
      print("No workspace with workspace name : {} exists...".format(workspace_name))
      return []
  try :  
      datasets_request_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + workspace_id + '/datasets'
      datasets_request_response = json.loads(requests.get(url=datasets_request_url, headers=header).content)
  except Exception as error:
      print("Request Error : ",error)
      return []
  try :
      dataset_id = [dataset_content['id'] for dataset_content in datasets_request_response['value'] if dataset_content['name'] == dataset_name][0]
  except Exception as error : 
      print("No dataset with dataset name : {} exists in workspace : {}.....".format(dataset_name,workspace_name))
      return []
  try : 
      refresh_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + workspace_id + '/datasets/' + dataset_id + '/refreshes'
      requests.post(url=refresh_url, headers=header)
      current_time = datetime.now().strftime("%H:%M:%S")
      print("Dataset with Dataset Name : {} in Workspace : {} Refreshed at Time : {}".format(dataset_name,workspace_name,current_time))
  except Exception as error :
      print("Request Error : ",error)
      return []
  return [(workspace_name,workspace_id),(dataset_name,dataset_id)]

# COMMAND ----------

# Driver Program
workspace_name = 'Trigger Workspace'
dataset_name = 'Table'

access_token = get_access_token(client_id,client_secret,tenant_id)
refresh_dataset(access_token,workspace_name,dataset_name)
