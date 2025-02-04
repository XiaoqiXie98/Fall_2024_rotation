import ee
ee.Initialize(project="ee-xiaoqixie98n")
from lib.constants import (
    CCDC,
    HARMONIC_TAGS,
    # Harmonic,
    # Kalman,
    # KalmanRecordingFlags,
)
from lib.image_collections import COLLECTIONS
from lib.utils.ee.ccdc_utils import (
    build_ccd_image,
    get_multi_coefs,
    build_segment_tag,
    get_multi_synthetic,
)
# from lib.utils.ee.dates import convert_date
import pandas as pd
import os
# def get_ccdc_coefficients_for_point_by_date(date_str, point):
#     # Convert date from string format (YYYY-MM-DD) to Earth Engine Date
#     date = ee.Date(date_str)

#     # Convert the date to milliseconds (which is required for processing)
#     date_converted = date.millis()

#     ccdc_asset = COLLECTIONS["CCDC_Global"].mosaic()

#     bands = ["SWIR1"]
#     coefs = HARMONIC_TAGS

#     segments_count = 10
#     segments = build_segment_tag(segments_count)

#     ccdc_image = build_ccd_image(ccdc_asset, segments_count, bands)

#     # Get CCDC coefficients for the given date
#     coefs = get_multi_coefs(
#         ccdc_image,
#         date_converted,
#         bands,
#         coef_list=HARMONIC_TAGS,
#         cond=True,
#         segment_names=segments,
#         behavior="before",
#     ).rename([*[f"{CCDC.BAND_PREFIX.value}_{x}" for x in HARMONIC_TAGS]])

#     # Get synthetic image for the given date
#     synthetic_image = get_multi_synthetic(
#         ccdc_image,
#         date_converted,
#         date_format=1,
#         band_list=bands,
#         segments=segments,
#     ).rename(CCDC.FIT.value)

#     # Sample the coefficients and synthetic image at the provided point
#     coefs_at_point = coefs.sample(region=point, scale=30).first()  # Assuming a scale of 30 meters
#     synthetic_at_point = synthetic_image.sample(region=point, scale=30).first()

#     # Extract the longitude and latitude from the point
#     point_coordinates = point.coordinates()
#     longitude = point_coordinates.get(0)
#     latitude = point_coordinates.get(1)

#     if coefs_at_point is not None and synthetic_at_point is not None:
#         combined_data = coefs_at_point.copyProperties(synthetic_at_point)
#     else:
#         print(f"Skipping point due to missing data: {num1}, {num2}")
#         continue  # Skip this iteration
#     # # Combine the coefficients and synthetic image as properties of the feature
#     # combined_data = coefs_at_point.copyProperties(synthetic_at_point)

#     # Add the longitude, latitude, and date as properties to the feature
#     combined_data = combined_data.set({
#         'longitude': longitude,
#         'latitude': latitude,
#         'date': date_str#date_str  # Use the original string format for date
#     })

#     # Convert the feature properties to a dictionary
#     feature_dict = combined_data.toDictionary().getInfo()

#     # Extract CCDC coefficients and other properties into a list
#     result_row = {
#         'longitude': feature_dict['longitude'],
#         'latitude': feature_dict['latitude'],
#         'date': feature_dict['date'],
#     }

#     # Add CCDC coefficient properties (assuming they are stored under specific names)
#     for coef_name in HARMONIC_TAGS:
#         result_row[f"coefficient_{coef_name}"] = feature_dict.get(f"{CCDC.BAND_PREFIX.value}_{coef_name}", None)

#     # Create or append to a pandas DataFrame
#     df = pd.DataFrame([result_row])

#     # Return the DataFrame containing the row with all the properties
#     return df
def get_ccdc_coefficients_for_point_by_date(date_str, point):
    # Convert date from string format (YYYY-MM-DD) to Earth Engine Date
    date = ee.Date(date_str)

    # Convert the date to milliseconds (which is required for processing)
    date_converted = date.millis()

    ccdc_asset = COLLECTIONS["CCDC_Global"].mosaic()

    bands = ["SWIR1"]
    coefs = HARMONIC_TAGS

    segments_count = 10
    segments = build_segment_tag(segments_count)

    ccdc_image = build_ccd_image(ccdc_asset, segments_count, bands)

    # Get CCDC coefficients for the given date
    coefs = get_multi_coefs(
        ccdc_image,
        date_converted,
        bands,
        coef_list=HARMONIC_TAGS,
        cond=True,
        segment_names=segments,
        behavior="before",
    ).rename([*[f"{CCDC.BAND_PREFIX.value}_{x}" for x in HARMONIC_TAGS]])

    # Sample the coefficients at the provided point
    sampled_coefs = coefs.sample(region=point, scale=30)
    # print(f"Sampled coefficients: {sampled_coefs.getInfo()}")
    coefs_at_point = sampled_coefs.first()

    # Check if coefs_at_point is None
    if coefs_at_point is None:
        print(f"Error: No data for point at Longitude: {point}")
        return pd.DataFrame()  # Skip this point by returning an empty DataFrame

    # Extract coordinates
    point_coordinates = point.coordinates()
    longitude = point_coordinates.get(0).getInfo()  # Convert to regular Python value
    latitude = point_coordinates.get(1).getInfo()   # Convert to regular Python value

    # Extract CCDC coefficients into a list for result_row
    feature_dict = coefs_at_point.toDictionary().getInfo()

    # Create the result row with the additional coordinates and date
    result_row = {
        'longitude': longitude,
        'latitude': latitude,
        'date': date_str,
    }

    # Add CCDC coefficient properties (assuming they are stored under specific names)
    for coef_name in HARMONIC_TAGS:
        result_row[f"coefficient_{coef_name}"] = feature_dict.get(f"{CCDC.BAND_PREFIX.value}_{coef_name}", None)

    # Create or append to a pandas DataFrame
    df = pd.DataFrame([result_row])

    # Return the DataFrame containing the row with all the properties
    return df

# Define a function to get CCDC coefficients for multiple dates
def get_multiple_ccdc_coefficients(dates, point):
    # Initialize an empty DataFrame to store results
    all_results = pd.DataFrame()
    
    # Loop through each date and fetch the coefficients
    for date_str in dates:
        # Get the CCDC coefficients for the current date
        df = get_ccdc_coefficients_for_point_by_date(date_str, point)
        
        # Append the results to the all_results DataFrame
        all_results = pd.concat([all_results, df], ignore_index=True)
    
    # Return the DataFrame containing all results
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
for q in range(points.shape[0]):  # Adjust loop for iterating through the points
    coord = points.iloc[q, :].astype(float)
    num1 = coord['Longitude']
    num2 = coord['Latitude']
    print(f"Longitude: {num1}, Latitude: {num2}")
    point = ee.Geometry.Point([num1, num2])

    try:
        # Attempt to get CCDC coefficients for the point
        point_results = get_multiple_ccdc_coefficients(dates, point)
        coefs = point_results.drop(['longitude', 'latitude', 'date'], axis=1)
        
        # Check if coefficients are all the same (no change)
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
        # If an error occurs, print the error and skip to the next point
        # print(f"Error processing point at Longitude: {num1}, Latitude: {num2}. Error: {e}")
        continue  # Skip to the next iteration of the loop
coords_with_change=pd.concat(coords_with_change)
coords_without_change=pd.concat(coords_without_change)
coords_with_change.to_csv(os.path.join(script_dir,'coords_with_change_100.csv'))
coords_without_change.to_csv(os.path.join(script_dir,'coords_without_change_100.csv'))

# # Loop through each point and fetch the CCDC coefficients for each date
# for point in points:
#     point=ee.Geometry.Point([point[0],point[1]])
#     point_results = get_multiple_ccdc_coefficients(dates, point)
    
#     coefs=point_results.drop(['longitude','latitude','date'],axis=1)
#     if i<100:
#         if not coefs.nunique(axis=0).eq(1).all():
#             coords_with_change.append(point_results)
#             i+=1
            
#     if j<100:
#         if coefs.nunique(axis=0).eq(1).all():
#             coords_without_change.append(point_results)
#             j+=1
#             print("i:",i,"j:",j)
#     if i == 100 and j == 100:
#         break

# Define a function to get CCDC coefficients for multiple points and dates
# def get_multiple_ccdc_coefficients_for_points(dates, points):
#     # Initialize an empty DataFrame to store all results
#     all_results = pd.DataFrame()
    
#     # Loop through each point and fetch the CCDC coefficients for each date
#     for point in points:
#         # For each point, call get_multiple_ccdc_coefficients to get the coefficients for all dates
#         point_results = get_multiple_ccdc_coefficients(dates, point)
        
#         # Add a column for the point's coordinates to differentiate them
#         point_coordinates = point.coordinates().getInfo()
#         longitude = point_coordinates[0]
#         latitude = point_coordinates[1]
#         point_results['longitude'] = longitude
#         point_results['latitude'] = latitude
        
#         # Append the point's results to the all_results DataFrame
#         all_results = pd.concat([all_results, point_results], ignore_index=True)
    
#     # Return the combined DataFrame containing results for all points and dates
#     return all_results



# Define a function to check and update CCDC coefficients for each point
# def check_and_update_coefficients_for_points(dates, points):
#     # Initialize an empty DataFrame to store all results
#     all_results = pd.DataFrame()
    
#     # Loop through each point and check if there is a change in coefficients for each date
#     for point in points:
#         # Retrieve coefficients for the first date
#         previous_coefficients = None
        
#         for date_str in dates:
#             # Get the CCDC coefficients for the current date
#             df = get_ccdc_coefficients_for_point_by_date(date_str, point)
            
#             # Extract coefficients as a dictionary for comparison
#             current_coefficients = df.drop(columns=["longitude", "latitude", "date"]).iloc[0].to_dict()
            
#             if previous_coefficients is not None:
#                 # Compare coefficients with the previous date
#                 coefficients_changed = any(
#                     previous_coefficients[key] != current_coefficients[key]
#                     for key in current_coefficients
#                 )
                
#                 if coefficients_changed:
#                     # If there is a change, update all coefficients (i.e., add new row with updated values)
#                     df["updated_coefficients"] = "Yes"
#                 else:
#                     # If there is no change, mark as "No"
#                     df["updated_coefficients"] = "No"
#             else:
#                 # For the first date, just mark as "No"
#                 df["updated_coefficients"] = "No"
            
#             # Save the current coefficients for comparison in the next iteration
#             previous_coefficients = current_coefficients
            
#             # Add the point's coordinates for identification
#             point_coordinates = point.coordinates().getInfo()
#             df['longitude'] = point_coordinates[0]
#             df['latitude'] = point_coordinates[1]
            
#             # Append the point's results to the all_results DataFrame
#             all_results = pd.concat([all_results, df], ignore_index=True)
    
#     # Return the combined DataFrame containing results for all points and dates
#     return all_results

# # Define a function to check and update CCDC coefficients for each point and return two DataFrames
# def check_and_update_coefficients_for_points(dates, points):
#     # Initialize DataFrames to store results for points with and without changes
#     points_with_changes_df = pd.DataFrame()
#     points_without_changes_df = pd.DataFrame()
    
#     # Loop through each point and check if there is a change in coefficients for each date
#     for point in points:
#         # Retrieve coefficients for the first date
#         previous_coefficients = None
#         point_changed = False  # Flag to track if there's any change for the point
        
#         for date_str in dates:
#             # Get the CCDC coefficients for the current date
#             df = get_ccdc_coefficients_for_point_by_date(date_str, point)
            
#             # Extract coefficients as a dictionary for comparison
#             current_coefficients = df.drop(columns=["longitude", "latitude", "date"]).iloc[0].to_dict()
            
#             if previous_coefficients is not None:
#                 # Compare coefficients with the previous date
#                 coefficients_changed = any(
#                     previous_coefficients[key] != current_coefficients[key]
#                     for key in current_coefficients
#                 )
                
#                 if coefficients_changed:
#                     point_changed = True  # Mark the point as changed if any coefficient changed
#             # Save the current coefficients for comparison in the next iteration
#             previous_coefficients = current_coefficients
        
#         # After checking all dates for the point, classify the point into the appropriate DataFrame
#         if point_changed:
#             if len(points_with_changes_df) < 101:
#                 points_with_changes_df = pd.concat([points_with_changes_df, df], ignore_index=True)  # Append to the changes DataFrame
#         else:
#             if len(points_without_changes_df) < 101:
#                 points_without_changes_df = pd.concat([points_without_changes_df, df], ignore_index=True)  # Append to the no-changes DataFrame
        
#         # Stop adding rows once both DataFrames have reached 100 rows
#         if len(points_with_changes_df) >= 100 and len(points_without_changes_df) >= 100:
#             break
    
#     # Return the two DataFrames
#     return points_with_changes_df, points_without_changes_df

# # List of multiple points
# points = [
#     ee.Geometry.Point([-123.3656, 48.4284]),  # Point 1
#     ee.Geometry.Point([-122.6765, 45.5231]),  # Point 2
#     ee.Geometry.Point([-120.7401, 47.6500]),  # Point 3
#     # Add more points as needed
# ]

# # Dates to retrieve CCDC coefficients for
# dates = ["2016-01-01", "2017-01-01", "2018-01-01", "2019-01-01"]

# # Get the two DataFrames with points that have changes and points without changes
# points_with_changes_df, points_without_changes_df = check_and_update_coefficients_for_points(dates, points)
# print(points_without_changes_df)