#!/usr/bin/env python
import os
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def fetch_rentcast_data(api_key):
    url = 'https://api.rentcast.io/v1/properties'
    limit = 500  # Set the limit per page
    offset = 0   # Initial offset
    all_properties = []  # List to store all properties

    while True:
        params = {
            'city': 'Exeter',
            'state': 'NH',
            'limit': limit,
            'offset': offset
        }
        headers = {
            'Accept': 'application/json',
            'X-Api-Key': api_key
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                properties = data.get('data', [])
            elif isinstance(data, list):
                properties = data  # If the response is a list, use it directly
            else:
                raise ValueError("Unexpected response format: neither a dict nor a list")
            
            if not properties:
                break  # No more properties to fetch
            all_properties.extend(properties)  # Add fetched properties to the list
            offset += limit  # Increment offset for next page
        else:
            response.raise_for_status()
    
    return {'data': all_properties}


def query_avm(api_key):
    url = 'https://api.rentcast.io/v1/avm/value'
    params = {
        'address': '38 Cross Rd, Exeter, NH 03833',
        'propertyType': 'residential',
        'bedrooms': 3,
        'bathrooms': 4,
        'squareFootage': 3000,
        'maxRadius': 10,
        'daysOld': 300,
        'compCount': 10
    }
    headers = {
        'Accept': 'application/json',
        'X-Api-Key': api_key
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"Error 404: Not Found for URL: {response.url}")
    else:
        response.raise_for_status()

def create_table(data):
    if isinstance(data, dict) and 'data' in data:
        properties = data['data']
    elif isinstance(data, list):
        properties = data
    else:
        raise ValueError("Unexpected data format")

    df = pd.DataFrame(properties)
    return df

def create_map(df):
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in df.iterrows():
        lat = row.get('latitude')
        lon = row.get('longitude')
        popup_text = (
            f"Address: {row.get('address', 'N/A')}\n"
            f"Rent: ${row.get('rent', 'N/A')}\n"
            f"Bedrooms: {row.get('bedrooms', 'N/A')}\n"
            f"Bathrooms: {row.get('bathrooms', 'N/A')}\n"
            f"Square Footage: {row.get('squareFootage', 'N/A')}\n"
            f"Year Built: {row.get('yearBuilt', 'N/A')}"
        )
        if lat and lon:
            folium.Marker(location=[lat, lon], popup=popup_text).add_to(marker_cluster)

    return m

def create_avm_table(data):
    # Flatten the main property data and the comparables into a single DataFrame
    main_property = pd.DataFrame([data], columns=['price', 'priceRangeLow', 'priceRangeHigh', 'latitude', 'longitude'])
    comparables = pd.json_normalize(data['comparables'])
    df = pd.concat([main_property, comparables], ignore_index=True)
    return df

def create_avm_map(df):
    m = folium.Map(location=[df.loc[0, 'latitude'], df.loc[0, 'longitude']], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in df.iterrows():
        lat = row.get('latitude')
        lon = row.get('longitude')
        popup_text = (
            f"Address: {row.get('formattedAddress', 'N/A')}\n"
            f"Price: ${row.get('price', 'N/A')}\n"
            f"Bedrooms: {row.get('bedrooms', 'N/A')}\n"
            f"Bathrooms: {row.get('bathrooms', 'N/A')}\n"
            f"Square Footage: {row.get('squareFootage', 'N/A')}\n"
            f"Year Built: {row.get('yearBuilt', 'N/A')}\n"
            f"Distance: {row.get('distance', 'N/A')} miles\n"
            f"Correlation: {row.get('correlation', 'N/A')}"
        )
        if lat and lon:
            folium.Marker(location=[lat, lon], popup=popup_text).add_to(marker_cluster)

    return m

def main():
    api_key = '1c683a563a6647ba9d079a685c4e0d09'  # Replace with your actual API key
    data = fetch_rentcast_data(api_key)

    # Create and display the table
    df = create_table(data)
    print(df)

    # Save the table to a CSV file
    file_path = 'table.csv'
    if os.path.exists(file_path):
        overwrite = input(f"The file {file_path} already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("File not overwritten.")
            return
    df.to_csv(file_path, index=False)
    print(f"Table saved as {file_path}")

    # Create and display the map
    m = create_map(df)
    m.save('property_map.html')
    print("Map saved as property_map.html")

    # Query the AVM endpoint
    avm_data = query_avm(api_key)
    if avm_data:
        avm_df = create_avm_table(avm_data)
        print(avm_df)

        # Save the AVM table to a CSV file
        avm_file_path = 'values.csv'
        if os.path.exists(avm_file_path):
            overwrite = input(f"The file {avm_file_path} already exists. Do you want to overwrite it? (y/n): ")
            if overwrite.lower() != 'y':
                print("File not overwritten.")
                return
        avm_df.to_csv(avm_file_path, index=False)
        print(f"AVM Table saved as {avm_file_path}")

        # Create and display the AVM map
        avm_map = create_avm_map(avm_df)
        avm_map.save('values.html')
        print("AVM Map saved as values.html")

if __name__ == '__main__':
    main()
