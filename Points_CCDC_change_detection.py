"""Look for points with change of CCDC estimates and without change."""
import ee
ee.Initialize(project="")
from lib.utils.ee.ccdc_utils import get_segments_for_coordinates
import os 
import pandas as pd

script_dir=os.getcwd()
point_dir=os.path.join(script_dir,'Point_selection','Random_points',"groups","Americas",
                       "random_points","random_points_100000.csv")
points=pd.read_csv(point_dir)

i = 0
j = 0
coords_with_change = []
coords_without_change = []

for q in range(points.shape[0]):
    point = points.iloc[q,:]
    lon = float(point['Longitude'])
    lat = float(point['Latitude'])
    try:
        d = get_segments_for_coordinates([lon, lat])
        filtered = [(start, end) for start, end in d if start != 0.0 and end != 0.0]

        filtered_df = pd.DataFrame(filtered, columns=['start', 'end'])

        # Check if there is at least one start value between 2016 and 2020
        # If there is at least one start, then this point is identified to have a change of CCDC estimates
        if filtered_df.shape[0] > 1 and (filtered_df['start'].between(2016, 2020).any()):
            if j < 100:
                coords_with_change.append([lon, lat])
                j += 1

        else:  
            if i < 100:
                coords_without_change.append([lon, lat])
                i += 1

        print("i:", i, "j:", j)

        if i == 100 and j == 100:
            break

    except Exception as e:
        continue  # Skip to the next iteration of the loop
coords_with_change=pd.concat(coords_with_change)
coords_without_change=pd.concat(coords_without_change)
coords_with_change.to_csv(os.path.join(script_dir,'coords_with_change_100.csv'))
coords_without_change.to_csv(os.path.join(script_dir,'coords_without_change_100.csv'))

