import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def display_country_names(gdf):
    print("Available countries:")
    for name in gdf['name'].unique():
        print(name)


def plot_country_centered(gdf, country_name):
    print(f"Plotting {country_name}...")

    # Filter for the specified country
    country_gdf = gdf[gdf['name'] == country_name]

    if country_gdf.empty:
        print("Country not found.")
        return

    # Calculate the centroid of the country's geometry
    centroid = country_gdf.geometry.centroid.iloc[0]
    lon, lat = centroid.x, centroid.y

    # Dynamically adjust the figure size or projection based on latitude
    fig_size = 10
    if abs(lat) > 60:  # High latitude adjustment
        fig_size = 8  # Smaller figure size for high latitude countries
        # Placeholder for conditional projection adjustment if needed
        projection = ccrs.NearsidePerspective(central_longitude=lon, central_latitude=lat)
    else:
        projection = ccrs.Orthographic(central_longitude=lon, central_latitude=lat)

    fig, ax = plt.subplots(figsize=(fig_size, fig_size), subplot_kw={'projection': projection})

    # Continue with plotting as before
    ax.stock_img()
    country_gdf.plot(ax=ax, transform=ccrs.PlateCarree(), edgecolor='black', facecolor='none')
    plt.title(f"{country_name} Map")
    plt.show()


    
# Load the GeoJSON file into a GeoDataFrame
print("Loading GeoJSON file...")
gdf = gpd.read_file('country_border_generator/custom.geojson')

# Display all country names
display_country_names(gdf)

while True:
    country_name = input("Enter the country name (or type 'exit' to quit):\n> ")
    if country_name.lower() == 'exit':
        break
    if country_name in gdf['name'].values:
        plot_country_centered(gdf, country_name)
    elif country_name.lower() == 'list':
        display_country_names(gdf)
    else:
        print("Country not found. Please try again.")