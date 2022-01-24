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


## LIst of European countries + codes for API requests
country_codes_eur = {'BEL': 'Belgium', 'NLD': 'Netherlands', 'AUT': 'Austria', 'GBR': 'United Kingdom', 'IRL': 'Ireland', 'DEU': 'Germany', 'FRA': 'France', 'ESP': 'Spain', 'PRT': 'Portugal', 'DNK': 'Denmark', 'NOR': 'Norway', 'SWE': 'Sweden', 'FIN': 'Finland', 'CHE': 'Switzerland', 'CYP': 'Cyprus', 'CZE': 'Czech_Republic', 'EST': 'Estonia', 'GRC': 'Greece', 'GRL': 'Greenland', 'HRV': 'Croatia', 'HUN': 'Hungary', 'ISL': 'Iceland', 'LUX': 'Luxembourg', 'LVA': 'Latvia', 'MKD': 'Macedonia', 'POL': 'Poland', 'ROU': 'Romania', 'SRB': 'Serbia', 'SVK': 'Slovakia', 'SVN': 'Slovenia', 'UKR': 'Ukraine', 'EEC': 'European_Union'}   
country_codes_eur_list = list(country_codes_eur.keys())
country_codes_eur_list_values = list(country_codes_eur.values())


## Request from re3data API list of repositories per country

re3data_requests = []  # requests for re3data API
for x in range(0, len(country_codes_eur_list)):
    re3data_requests.append(
    "https://www.re3data.org/api/beta/repositories?query=&countries%5B%5D=" + country_codes_eur_list[x])

re3data_requests_count = len(re3data_requests)
re3data_results = []  # collect responses from re3data API

for y in range(0, re3data_requests_count):

    response = requests.get(re3data_requests[y], timeout=5)
    if response.status_code == 200:
        response_2 = str(response.text)
        re3data_results.append(response_2)
    else:
        re3data_results.append("error")

    sys.stdout.write("\rCurrent loop - re3data API requests: %d of %d" % ((y + 1), re3data_requests_count))
    sys.stdout.flush()


df_list = [] # Extract information from harvested metadata: repository ID, name and link
for z in range(0, len(re3data_results)):

    soup = BeautifulSoup(re3data_results[z], 'xml')   
  
    # Extracting the data
    ids = soup.find_all('id')
    names = soup.find_all('name')
    links = soup.find_all('link', href = True)

    data_re3data = []
  
    # Loop to store the data in a list named 'data_re3data'
    for i in range(0, len(ids)):
        rows = [ids[i].get_text(), names[i].get_text(), links[i]['href']]
        data_re3data.append(rows)
        
    # Converting the list into dataframe
    df = pd.DataFrame(data_re3data, columns=['ID', 'name', 'link'], dtype = float)
    df['country'] = [country_codes_eur_list_values[z]] * len(ids)
    df_list.append(df)

data_re3data_final = pd.concat(df_list)
data_re3data_final.to_excel((working_dir_input + '/output_re3data_1.xlsx'), index=False, header=True)



## Second part: get extended information per repository

repo_links = list(data_re3data_final['link']) # all repository links
repo_links_count = len(repo_links)
re3data_results_2 = []

for w in range(0, repo_links_count): # request extended information per repository from re3data API

    response = requests.get(repo_links[w], timeout=5)
    if response.status_code == 200:
        response_2 = str(response.text)
        re3data_results_2.append(response_2)
    else:
        re3data_results_2.append("error")

    sys.stdout.write("\rCurrent loop - re3data API requests: %d of %d" % ((w + 1), repo_links_count))
    sys.stdout.flush()


df_list_2 = [] # https://www.geeksforgeeks.org/convert-xml-structure-to-dataframe-using-beautifulsoup-python/
for q in range(0, len(re3data_results_2)):

    soup = BeautifulSoup(re3data_results_2[q], 'xml')
  
    # Extracting the data
    repositoryURL = soup.find_all('repositoryURL')
    repositoryURL_list = '+'.join([i.get_text() for i in repositoryURL])
    
    repo_type = soup.find_all('type')
    repo_type_list = '+'.join(set([i.get_text() for i in repo_type]))
    
    subject_first = soup.find_all('subject')
    subject_first_list = '+'.join([i.get_text() for i in subject_first if i.get_text()[1] == " " ])
          
    subject = soup.find_all('subject')
    subject_list = '+'.join([i.get_text() for i in subject])
    
    institutionName = soup.find_all('institutionName')
    institutionName_list = '+'.join([i.get_text() for i in institutionName])
    
    institutionType = soup.find_all('institutionType')
    institutionType_list = '+'.join(set([i.get_text() for i in institutionType]))
    
    pidSystem = soup.find_all('pidSystem')
    pidSystem_list = '+'.join([i.get_text() for i in pidSystem])
    
    data_re3data_2 = [repositoryURL_list, repo_type_list, subject_first_list, subject_list, institutionName_list, institutionType_list, pidSystem_list]
    df_list_2.append(data_re3data_2)

df_2 = pd.DataFrame(df_list_2, columns=['repositoryURL', 'type', 'subject_first', 'subject', 'institutionName', 'institutionType', 'pidSystem'], dtype = float)

data_re3data_final.reset_index(drop=True, inplace=True)
df_2.reset_index(drop=True, inplace=True)
result = pd.concat([data_re3data_final, df_2],  axis = 1)
result.to_excel((working_dir_input + '/output_re3data_2.xlsx'), index=False, header=True)

print("\n End of script.")



