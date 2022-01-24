# -*- coding: utf-8 -*-
"""
2021

@author: Niek Van Wettere
"""

## Import libraries
import json
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys


## Define where output files have to be saved

working_dir_input = input("\n\nInput here the path to the directory where the output files have to be saved:")  # for example: C:/Users/nvwetter/OneDrive - Vrije Universiteit Brussel/Documenten
os.chdir(working_dir_input)  # set working directory where output files are to be saved


## DataCite clients 

response_DataCite = requests.get("https://api.datacite.org/clients/", timeout=5)
DataCite_clients = []
DataCite_clients.append(json.loads(response_DataCite.text))
totalPages = DataCite_clients[0]['meta']['totalPages']

for a in range(0, totalPages):
    request_link = DataCite_clients[a]['links']['next'] # use next to go to next page of API
    response_DataCite_2 = requests.get(request_link, timeout=15)
    DataCite_clients.append(json.loads(response_DataCite_2.text))
    
    sys.stdout.write("\rCurrent loop - DataCite API requests: %d of %d" % ((a + 1), totalPages))
    sys.stdout.flush()


DataCite_info = []
DataCite_clients_final = []
for b in range(0,len(DataCite_clients)):
    for c in DataCite_clients[b]['data']:
        DataCite_info.append([c['attributes']['name'], c['attributes']['symbol'], c['attributes']['url']])
        DataCite_clients_final.append(c['attributes']['symbol'])
    
df_1 = pd.DataFrame(DataCite_info, columns=['repo_name', 'repo_symbol', 'repo_url'], dtype = float)
df_1.to_excel((working_dir_input + '/output_DataCite_clients.xlsx'), index=False, header=True)


## Harvest usage statistics for DataCite client (API request also includes counts for datasets and software specific) 

PublicationYear = input("\n\nInput here the publication year for which you want to obtain usage statistics:")

DataCite_results = []  # collect responses from DataCite API
DataCite_results_datasets = []
DataCite_results_software = []
for d in range(0, len(DataCite_clients_final)):

    response_DataCite_repo = requests.get(("https://api.datacite.org/dois?query=publicationYear:" + PublicationYear + "&client-id=" + DataCite_clients_final[d].lower()), timeout=60)
    if response_DataCite_repo.status_code == 200:
        DataCite_results.append(json.loads(response_DataCite_repo.text)['meta']['total'])  # use meta-field to harvest total number of DOIs for that repository & publication year
        
        
        try:
            
            dataset_ok = None
            software_ok = None
            
            resource_types_counts = json.loads(response_DataCite_repo.text)['meta']['resourceTypes']
            
            for resource_type in resource_types_counts:
                if resource_type['id'] == "dataset":
                    DataCite_results_datasets.append(resource_type["count"])
                    
                    dataset_ok = "ok"
                    
                    break
    
            for resource_type in resource_types_counts:
                if resource_type['id'] == "software":
                    DataCite_results_software.append(resource_type["count"])
                    
                    software_ok = "ok"
                    
                    break
            
            if dataset_ok != "ok":
                DataCite_results_datasets.append("NA")
            
            if software_ok != "ok":
                DataCite_results_software.append("NA")
            
        except KeyError:
            DataCite_results_datasets.append("error")
            DataCite_results_software.append("error")
        
        
    else:
        DataCite_results.append("error")
        DataCite_results_datasets.append("error")
        DataCite_results_software.append("error")

    sys.stdout.write("\rCurrent loop - DataCite API requests: %d of %d" % ((d + 1), len(DataCite_clients_final)))
    sys.stdout.flush()

data_tuples = list(zip(DataCite_clients_final, DataCite_results, DataCite_results_datasets, DataCite_results_software))
df_2 = pd.DataFrame(data_tuples, columns=['DataCite_clients_final', ('total_depo_' + PublicationYear), 'count_datasets', 'count_software'], dtype = float)
df_2.to_excel((working_dir_input + '/output_DataCite_depo_per_repo.xlsx'), index=False, header=True)

print("\n End of script.")






