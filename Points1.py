import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json

#Let's go over the generated unstable points before getting more points.
script_directory=os.path.dirname(os.path.realpath(__file__))

study_area="Americas"

type='unstable'

reference_date = datetime(2017, 1, 1)

def RMSE(v1,v2):
    v=np.sqrt(np.mean((v1-v2)**2))
    return(v)

def import_values(dir, file_names, json_file_path):
    values = []
    
    # Load JSON file with points
    with open(json_file_path, 'r') as json_file:
        points = json.load(json_file)

    for i, file_name in enumerate(file_names):
        # Create full file path
        file_path = os.path.join(dir, file_name)
        
        # Check if the file exists
        if os.path.isfile(file_path):
            # Read the CSV file
            d = pd.read_csv(file_path)
            # d['point'] = i  # Assign point index
            
            # Access corresponding point coordinates
            ll = points[i]  
            d['longitude'] = ll[0]  # Assign longitude
            d['latitude'] = ll[1]  # Assign latitude
            
            # Append DataFrame to the list
            values.append(d)

    # Concatenate all DataFrames into one (optional)
    if values:
        values = pd.concat(values, ignore_index=True)
    
    return values

# set_num=[0,50,100,150,200,250,300,350,400]

data=[]
nam="unstable_threshold0.3_2017_2019"


d=[]
run_directory = os.path.join(script_directory, 'tests', 'kalman',
                                study_area,nam,#f'set_{num1}_{num2}',
                                'unimodal','result',
                                'kalman_state'
                                )

points_directory1 = os.path.join(script_directory, 'tests', 'kalman',
                                study_area,nam,#f'set_{num1}_{num2}',
                                'unimodal',"points.json")

files_names=[]
if os.path.exists(run_directory):
    files_names=os.listdir(run_directory)

points_value=import_values(run_directory,files_names,points_directory1)
# points_value=pd.concat(points_value)
points_value['date'] = pd.to_datetime(points_value['date'])
points_value=points_value[points_value['date']>=reference_date]
residual_ccdc=points_value['ccdc_fit']-points_value['z']
residual_kf=points_value['estimate_predicted']-points_value['z']
d.append(points_value)
d=pd.concat(d)
d['area']=study_area
d['residual_ccdc']=residual_ccdc
d['residual_kf']=residual_kf
data.append(d)

data=pd.concat(data)
data.to_csv(os.path.join(script_directory,f"data_R_0.003_{nam}.csv"),index=False)

data_dir=os.path.join(script_directory,f"data_R_0.003_{nam}.csv")
data=pd.read_csv(data_dir)

# """Points with large residuals"""
# #through the accumulated absolute residuals
ll=data[['longitude','latitude']].drop_duplicates()
# print(ll.shape)
Data=[]
for i, row in ll.iterrows():
    coord=(row['longitude'], row['latitude']) 
    sub = data[(data['longitude'] == coord[0]) 
               & (data['latitude'] == coord[1])
               & (data['z']!=0)
               ]
    acc_abs_residual_ccdc=sub['residual_ccdc'].abs().sum()
    acc_abs_residual_kf=sub['residual_kf'].abs().sum()
    rmse_ccdc=RMSE(sub['ccdc_fit'],sub['z'])
    rmse_kf=RMSE(sub['estimate_predicted'],sub['z'])
    r={"longitude":row['longitude'],
       "latitude":row['latitude'],
       "abs_residual_ccdc":acc_abs_residual_ccdc,
       "abs_residual_kf":acc_abs_residual_kf,
       "rmse_ccdc":rmse_ccdc,
       "rmse_kf":rmse_kf}
    Data.append(r)

Data=pd.DataFrame(Data)
Data.to_csv(os.path.join(script_directory,f"rmse_R_0.003_{nam}.csv"),index=False)

# #quantile at 90% is 0.088 for rmse_ccdc. This is the value to identify between large and giant.
# data_dir=os.path.join(script_directory,"rmse_R_0.003_unstable.csv")
# data=pd.read_csv(data_dir)
# #0.068 and 0.088
