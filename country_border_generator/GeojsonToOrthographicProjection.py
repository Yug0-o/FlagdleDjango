import cartopy.crs as ccrs

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
    country_shape = country_gdf.dissolve()
    center = country_shape.geometry.centroid.iloc[0]
    central_longitude, central_latitude = center.x, center.y

    minx, miny, maxx, maxy = country_gdf.geometry.total_bounds
    
    # Calculate padding based on the size of the country
    x_padding = (maxx - minx) * padding
    y_padding = (maxy - miny) * padding

    # Adjust bounds with padding
    minx -= x_padding
    miny -= y_padding
    maxx += x_padding
    maxy += y_padding

    projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
    
    return projection, (minx, maxx, miny, maxy), (central_longitude, central_latitude)