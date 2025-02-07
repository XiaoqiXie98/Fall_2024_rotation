"""This script is used to compare kalman filter and ccdc estimates for points with ccdc changes detected between 2016-01-01 and 2020-01-01 """
"""Will kf performance similar to kf when ccdc successfully dtected changes?"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
script_directory=os.getcwd()

common_path=os.path.join(script_directory,'tests','kalman','Americas',
                         'coords_with_change_100','unimodal')
coords_dir=os.path.join(common_path,'points.json')
#read coords in json file
with open(coords_dir,'r') as file:
    coords=json.load(file)

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

os.makedirs(os.path.join(script_directory,'coords_with_segments'),exist_ok=True)

#estimate rmse for each point
rmse=[]
for i in range(len(data)):
    d=data[i]
    d1=d.loc[d['z']!=0,:]
    coord=d[['longitude', 'latitude']].drop_duplicates()
    plt.figure(figsize=(12,8))
    plt.plot(d1['frac_of_year'], d1['z'], label='Z', linestyle='-', marker='o', alpha=0.7)
    plt.plot(d['frac_of_year'], d['ccdc_fit'], label='CCDC Fit', linestyle='--', alpha=0.7)
    plt.plot(d1['frac_of_year'], d1['estimate_predicted'], label='Estimate Predicted', linestyle='-.', marker='^', alpha=0.7)

    plt.xlabel('Fraction of Year')
    plt.ylabel('Values')
    plt.title('Comparison of Z, CCDC Fit, and Estimate Predicted Over Time')
    plt.legend()
    plt.savefig(os.path.join(script_directory,'coords_with_segments',f'{coord.values}.png'),bbox_inches='tight')

    print(i,coord)
    rmse_ccdc = RMSE(d1['ccdc_fit'].to_numpy(), d1['z'].to_numpy())
    rmse_kf = RMSE(d1['estimate_predicted'].to_numpy(), d1['z'].to_numpy())    
    rmse_diff=rmse_kf-rmse_ccdc
    detections=d.shape[0]
    d1={'longitude':coord.iloc[0,0],'latitude':coord.iloc[0,1],'rmse_ccdc':rmse_ccdc,
        'rmse_kf':rmse_kf,
        'rmse_diff_kf_minus_ccdc':rmse_diff,'detections':detections}
    rmse.append(d1)

rmse=pd.DataFrame(rmse)
rmse.to_csv(os.path.join(script_directory,'rmse_coords_with_change_100.csv'),index=False)

#look for ccdc rsme at 24,25,26, 49,50,52, 74,75,76 percentiles
percentiles = [24, 25, 26, 49, 50, 52, 74, 75, 76]
position=np.array(percentiles)-1
rmse_sorted = rmse.sort_values(by='rmse_ccdc', ascending=True)
table=rmse_sorted.iloc[position,:]
table['percentiles']=percentiles
table.to_csv(os.path.join(script_directory,'table_rmse_coords_with_changes.csv'),index=False)
print(table)
