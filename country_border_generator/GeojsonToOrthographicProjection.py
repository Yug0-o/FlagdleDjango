from unidecode import unidecode
import geopandas as gpd
import pandas as pd
import os

import sys
sys.path.append('D:\\VisualCode_Python\\FlagdleDjango\\Flagdle\\game')

import Base32EncoderDecoder as utf8_To_b64

country_folder = "Flagdle/assets/country"
continents = os.listdir(country_folder)

def create_projection(country_gdf, DEBUG_FULL, DEBUG_INFO, padding=1.05):
    """
    Create an Orthographic projection centered on the country's centroid
    and adjust bounds with padding.
    
    Parameters:
    - country_gdf: GeoDataFrame containing the country's geometry.
    - padding: Padding to apply to the bounds (% of the view size).
    
    Returns:
    - projection: The Cartopy Orthographic projection.
    - (minx, maxx, miny, maxy): Tuple containing the adjusted bounds.
    """
    import cartopy.crs as ccrs
    country_shape = country_gdf.dissolve()
    country_shape = gpd.GeoSeries(country_shape.geometry.unary_union)
    center = country_shape.geometry.centroid.iloc[0]
    central_longitude, central_latitude = center.x, center.y
    # get the width and height of the country
    minx, miny, maxx, maxy = country_shape.total_bounds

    height = (maxy - miny) * padding
    width = min(maxx - minx, 180)  * padding
    bbox_side = max(height, width)

    minx = central_longitude - bbox_side / 2
    maxx = central_longitude + bbox_side / 2
    miny = central_latitude - bbox_side / 2
    maxy = central_latitude + bbox_side / 2

    if DEBUG_FULL: print(f"\n❕ Extent :\n\tminX : {minx:.2f}\n\tmaxX : {maxx:.2f}\n\tminY : {miny:.2f}\n\tmaxY : {maxy:.2f}")

    if DEBUG_FULL: print(f"\n❕ Corrected Extent :\n\tminX : {minx:.2f}\n\tmaxX : {maxx:.2f}\n\tminY : {miny:.2f}\n\tmaxY : {maxy:.2f}")

    projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
    
    return projection, (minx, maxx, miny, maxy), (central_longitude, central_latitude)

def filter_country_gdf(local_gdf, country_name:str, DEBUG_FULL, DEBUG_INFO, laguage='en'):
    """
    Filters the GeoDataFrame for a given country name.
    
    Parameters:
    - local_gdf: The GeoDataFrame containing country data.
    - country_name: The name of the country to filter for.
    
    Returns:
    - A tuple containing the filtered GeoDataFrame containing only the specified country's data
      and the full name of the country.
    """
    if country_name == '':
        return False, False

    if country_name == 'world':
        return local_gdf, 'World'

    if country_name in continents:
        if DEBUG_INFO: print(f"🔄 Listing all countries in {country_name}")
        world_gdf = local_gdf
        continent_name = country_name
        # loop through the countries of each continent in country_path
        continent_gdf = []
        for country in os.listdir(f"{country_folder}/{continent_name}"):
            if 'icon' in country:
                continue

            country_name, extension = os.path.splitext(country)
            country = utf8_To_b64.base32_to_utf8(country_name) + '.' + extension
            
            # add each country's gdf to the continent_gdf
            country_gdf, country_full_name = filter_country_gdf(world_gdf, country.split('.')[0], DEBUG_FULL, DEBUG_INFO, laguage=laguage)
            if country_full_name != False:
                if DEBUG_INFO: print(f"\t- Adding {country_full_name} to {continent_name}...")
                continent_gdf.append(country_gdf)
            else:
                if DEBUG_INFO: print(f"\t-❌ {country} not found in the world")

        if DEBUG_INFO: print(f"🔄 Combining all countries in {continent_name}...")
        if len(continent_gdf) == 0:
            return False, False
        
        continent_gdf = gpd.GeoDataFrame(pd.concat(continent_gdf, ignore_index=True))

        return continent_gdf, continent_name
    try:
        country_input = unidecode(country_name.lower())  # Normalize input name
        
        # Identify columns that represent names in different languages and contain string values
        name_columns = [col for col in local_gdf.columns if col.startswith('name_') and local_gdf[col].dtype in ['object', 'string']]
        
        # Normalize names in the GeoDataFrame and check if the normalized input name is contained within these names
        country_filter = local_gdf[name_columns].apply(lambda x: x.apply(lambda y: unidecode(y).lower() if isinstance(y, str) else y).str.contains(country_input, case=False, regex=False) if x.dtype == 'object' or x.dtype == 'string' else False).any(axis=1)
        
        # Check if there is a perfect match
        perfect_match_filter = local_gdf[name_columns].apply(lambda x: x.apply(lambda y: unidecode(y).lower() if isinstance(y, str) else y) == country_input).any(axis=1)
        
        # If there is a perfect match, use the perfect match filter
        if perfect_match_filter.any():
            country_filter = perfect_match_filter
        
        
        filtered_gdf = local_gdf[country_filter]
        # change the X axis from -180 to 180 to 0 to 360
        # filtered_gdf['geometry'] = filtered_gdf['geometry'].translate(xoff=191.46)
        full_name = filtered_gdf[f'name_{laguage}'].values[0]  # Assuming 'name_en' column contains the full name in English
        
        return filtered_gdf, full_name
    except:
        return False, False