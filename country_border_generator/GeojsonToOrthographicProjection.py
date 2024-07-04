from unidecode import unidecode
import geopandas as gpd
import pandas as pd
import os

country_folder = "Flagdle/assets/country"
continents = os.listdir(country_folder)

def create_projection(country_gdf, padding=0.05):
    """
    Create an Orthographic projection centered on the country's centroid
    and adjust bounds with padding.
    
    Parameters:
    - country_gdf: GeoDataFrame containing the country's geometry.
    - padding: Padding to apply to the bounds (as a fraction of the total size).
    
    Returns:
    - projection: The Cartopy Orthographic projection.
    - (minx, maxx, miny, maxy): Tuple containing the adjusted bounds.
    """
    import cartopy.crs as ccrs
    country_shape = country_gdf.dissolve()
    country_shape = gpd.GeoSeries(country_shape.geometry.unary_union)
    center = country_shape.geometry.centroid.iloc[0]
    central_longitude, central_latitude = center.x, center.y

    minx, miny, maxx, maxy = country_gdf.geometry.total_bounds
    print(f"\n❕ Extent :\n\tminX : {minx:.2f}\n\tmaxX : {maxx:.2f}\n\tminY : {miny:.2f}\n\tmaxY : {maxy:.2f}")
    
    # Calculate padding based on the size of the country
    x_padding = (maxx - minx) * padding
    y_padding = (maxy - miny) * padding

    # Adjust bounds with padding
    minx -= x_padding
    miny -= y_padding
    maxx += x_padding
    maxy += y_padding

    minx = max(minx,-180)
    miny = max(miny,-90)
    maxx = min(maxx, 180)
    maxy = min(maxy, 90)

    # central_latitude = (miny + maxy) / 2

    print(f"\n❕ Padded Extent :\n\tminX : {minx:.2f}\n\tmaxX : {maxx:.2f}\n\tminY : {miny:.2f}\n\tmaxY : {maxy:.2f}")

    projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
    
    return projection, (minx, maxx, miny, maxy), (central_longitude, central_latitude)

def filter_country_gdf(local_gdf, country_name:str, laguage='en'):
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

    if country_name in continents:
        print(f"🔄 Listing all countries in {country_name}")
        world_gdf = local_gdf
        continent_name = country_name
        # loop through the countries of each continent in country_path
        continent_gdf = []
        for country in os.listdir(f"{country_folder}/{continent_name}"):
            if country == "icon.png":
                continue
            # add each country's gdf to the continent_gdf
            country_gdf, country_full_name = filter_country_gdf(world_gdf, country.split('.')[0])
            if country_full_name != False:
                print(f"\t- Adding {country_full_name} to {continent_name}...")
                continent_gdf.append(country_gdf)
            else:
                print(f"\t-❌ {country} not found in the world")

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
        full_name = filtered_gdf[f'name_{laguage}'].values[0]  # Assuming 'name_en' column contains the full name in English
        
        return filtered_gdf, full_name
    except:
        return False, False

"""
❌ Failed to update:
        - Amerique > Les Bahamas
        - Europe > Republique Tchèque
"""