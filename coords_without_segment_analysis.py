"""This script is used to compare kalman filter and ccdc estimates for points without ccdc changes detected between 2016-01-01 and 2020-01-01 """
"""Will kf performance similar to kf when ccdc successfully dtected changes?"""
import os
import json
import pandas as pd
import numpy as np
script_directory=os.getcwd()

common_path=os.path.join(script_directory,'tests','kalman','Americas',
                         'coords_without_change_100','unimodal')
coords_dir=os.path.join(common_path,'points.json')
#read coords in json file
with open(coords_dir,'r') as file:
    coords=json.load(file)
print(len(coords))
#read kalman results
kalman_dir=os.path.join(common_path,'result','kalman_state')
#list all files
files=os.listdir(kalman_dir)
#read all files in files
data=[]
for i in range(len(files)):
    coord=coords[i]
    # print(i,coord) 
    result_path=os.path.join(kalman_dir,files[i])
    d=pd.read_csv(result_path)
    d['longitude']=coord[0]
    d['latitude']=coord[1]
    data.append(d)

# data=pd.concat(data)
# print(data)

def RMSE(v1,v2):
    v=np.sqrt(np.mean((v1-v2)**2))
    return(v)

#estimate rmse for each point
rmse=[]
for i in range(len(data)):
    d=data[i]
    t=d.loc[d['z']!=0,:]
    if not t.empty:
        d=d.loc[d['z']!=0,:]
        coord=d[['longitude', 'latitude']].drop_duplicates()
        print(i,coord)
        rmse_ccdc = RMSE(d['ccdc_fit'].to_numpy(), d['z'].to_numpy())
        rmse_kf = RMSE(d['estimate_predicted'].to_numpy(), d['z'].to_numpy())    
        rmse_diff=rmse_kf-rmse_ccdc
        detections=d.shape[0]
        d1={'longitude':coord.iloc[0,0],'latitude':coord.iloc[0,1],'rmse_ccdc':rmse_ccdc,
            'rmse_kf':rmse_kf,
            'rmse_diff_kf_minus_ccdc':rmse_diff,'detections':detections}
    else:
        coord=d[['longitude', 'latitude']].drop_duplicates()
        print(i,coord)
        rmse_ccdc = RMSE(d['ccdc_fit'].to_numpy(), d['z'].to_numpy())
        rmse_kf = RMSE(d['estimate_predicted'].to_numpy(), d['z'].to_numpy())    
        rmse_diff=rmse_kf-rmse_ccdc
        detections=d.shape[0]
        d1={'longitude':coord.iloc[0,0],'latitude':coord.iloc[0,1],'rmse_ccdc':rmse_ccdc,
            'rmse_kf':rmse_kf,
            'rmse_diff_kf_minus_ccdc':rmse_diff,'detections':detections}
    rmse.append(d1)

rmse=pd.DataFrame(rmse)
rmse.to_csv(os.path.join(script_directory,'rmse_coords_without_change_100.csv'),index=False)

#look for ccdc rsme at 24,25,26, 49,50,52, 74,75,76 percentiles
percentiles = [24, 25, 26, 49, 50, 52, 74, 75, 76]
position=np.array(percentiles)-1
rmse_sorted = rmse.sort_values(by='rmse_ccdc', ascending=True)
table=rmse_sorted.iloc[position,:]
table['percentiles']=percentiles
table.to_csv(os.path.join(script_directory,'table_rmse_coords_without_changes.csv'),index=False)
print(table)