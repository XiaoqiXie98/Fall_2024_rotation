"""This code is written based on Khash's private code."""
import ee
ee.Initialize(project="")
from lib.constants import (
    CCDC,
    HARMONIC_TAGS,
)
from lib.image_collections import COLLECTIONS
from lib.utils.ee.ccdc_utils import (
    build_ccd_image,
    get_multi_coefs,
    build_segment_tag,
    get_multi_synthetic,
)
import pandas as pd
import os
def get_ccdc_coefficients_for_point_by_date(date_str, point):

    date = ee.Date(date_str)

    
    date_converted = date.millis()

    ccdc_asset = COLLECTIONS["CCDC_Global"].mosaic()

    bands = ["SWIR1"]
    coefs = HARMONIC_TAGS

    segments_count = 10
    segments = build_segment_tag(segments_count)

    ccdc_image = build_ccd_image(ccdc_asset, segments_count, bands)


    coefs = get_multi_coefs(
        ccdc_image,
        date_converted,
        bands,
        coef_list=HARMONIC_TAGS,
        cond=True,
        segment_names=segments,
        behavior="before",
    ).rename([*[f"{CCDC.BAND_PREFIX.value}_{x}" for x in HARMONIC_TAGS]])

    
    sampled_coefs = coefs.sample(region=point, scale=30)
    # print(f"Sampled coefficients: {sampled_coefs.getInfo()}")
    coefs_at_point = sampled_coefs.first()

    # Check if coefs_at_point is None
    if coefs_at_point is None:
        print(f"Error: No data for point at Longitude: {point}")
        return pd.DataFrame()  # Skip this point by returning an empty DataFrame

    
    point_coordinates = point.coordinates()
    longitude = point_coordinates.get(0).getInfo()  # Convert to regular Python value
    latitude = point_coordinates.get(1).getInfo()   # Convert to regular Python value

    
    feature_dict = coefs_at_point.toDictionary().getInfo()

    
    result_row = {
        'longitude': longitude,
        'latitude': latitude,
        'date': date_str,
    }

    
    for coef_name in HARMONIC_TAGS:
        result_row[f"coefficient_{coef_name}"] = feature_dict.get(f"{CCDC.BAND_PREFIX.value}_{coef_name}", None)

    
    df = pd.DataFrame([result_row])

   
    return df


def get_multiple_ccdc_coefficients(dates, point):
    
    all_results = pd.DataFrame()
    
    
    for date_str in dates:
        
        df = get_ccdc_coefficients_for_point_by_date(date_str, point)
        
        all_results = pd.concat([all_results, df], ignore_index=True)
    
    return all_results

script_dir=os.getcwd()
point_dir=os.path.join(script_dir,'Point_selection','Random_points',"groups","Americas",
                       "random_points","random_points_100000.csv")
points=pd.read_csv(point_dir)
dates = ["2016-01-01", "2017-01-01", "2018-01-01", "2019-01-01","2020-01-01"]
coords_with_change = []
coords_without_change = []
i=0
j=0
for q in range(points.shape[0]):  
    coord = points.iloc[q, :].astype(float)
    num1 = coord['Longitude']
    num2 = coord['Latitude']
    print(f"Longitude: {num1}, Latitude: {num2}")
    point = ee.Geometry.Point([num1, num2])

    try:
        point_results = get_multiple_ccdc_coefficients(dates, point)
        coefs = point_results.drop(['longitude', 'latitude', 'date'], axis=1)
        
        if coefs.nunique(axis=0).eq(1).all():  # If coefficients are constant, it's a "no change" point
            if j < 100:
                coords_without_change.append(point_results)
                j += 1

        else:  # If coefficients are different, it's a "change" point
            if i < 100:
                coords_with_change.append(point_results)
                i += 1

        print("i:", i, "j:", j)

        if i == 100 and j == 100:
            break

    except Exception as e:
        # print(f"Error processing point at Longitude: {num1}, Latitude: {num2}. Error: {e}")
        continue  # Skip to the next iteration of the loop
coords_with_change=pd.concat(coords_with_change)
coords_without_change=pd.concat(coords_without_change)
coords_with_change.to_csv(os.path.join(script_dir,'coords_with_change_100.csv'))
coords_without_change.to_csv(os.path.join(script_dir,'coords_without_change_100.csv'))

