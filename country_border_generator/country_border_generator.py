import geopandas as gpd
from shapely.geometry import box
from shapely.affinity import translate
import matplotlib.pyplot as plt
import sys

def print_all_countries():
    # Assuming 'name_en' is the primary name column for listing
    all_countries = data['name_en'].dropna().unique()
    for country in sorted(all_countries, key=lambda x: x.lower()):
        print(country)

def create_image_for_country(country_input: str):
    country_input = country_input.lower()
    
    # Identify columns that represent names in different languages and contain string values
    name_columns = [col for col in data.columns if col.startswith('name_') and data[col].dtype in ['object', 'string']]
    
    # Ensure that the .str accessor is applied only to columns with string values
    country_filter = data[name_columns].apply(lambda x: x.str.lower().str.contains(f'^{country_input}$', regex=True) if x.dtype == 'object' or x.dtype == 'string' else False).any(axis=1)
    
    filtered_data = data[country_filter]
    
    if filtered_data.empty:
        print(f"No data found for {country_input}")
        sys.stdout.flush()
    else:
        print(f"Creating image for {country_input}...")
        sys.stdout.flush()
        
        # The rest of your existing plotting logic follows here...
        
        # Calculate the centroid of the selected country's geometry
        centroid = filtered_data.geometry.centroid.iloc[0]
        
        # Compute the difference to shift the geometry to (0, 0)
        shift_x = -centroid.x
        shift_y = -centroid.y
        
        # Apply the transformation
        transformed_geometry = filtered_data.geometry.apply(lambda geom: translate(geom, xoff=shift_x, yoff=shift_y))
        
        # Create a new GeoDataFrame with the transformed geometry
        transformed_data = gpd.GeoDataFrame(filtered_data, geometry=transformed_geometry, crs="EPSG:4326")
        
        fig, ax = plt.subplots()
        
        # Set figure background to black
        fig.patch.set_facecolor('black')
        
        # Plot the transformed GeoDataFrame with white color
        transformed_data.plot(ax=ax, color='white')
        
        # Hide the axis
        ax.axis('off')
        
        # Calculate bounds of the transformed geometry and set plot limits with padding
        minx, miny, maxx, maxy = transformed_data.total_bounds
        padding_x = (maxx - minx) * 0.1  # 10% padding
        padding_y = (maxy - miny) * 0.1  # 10% padding
        ax.set_xlim([minx - padding_x, maxx + padding_x])
        ax.set_ylim([miny - padding_y, maxy + padding_y])

        # Fetch the French name of the country and replace any characters in the French name that are not suitable for filenames
        safe_country_name_fr = filtered_data['name_fr'].iloc[0].replace('/', '_').lower()
        
        # Save the figure without axis and with specified background color
        plt.savefig(f'country_border_generator\\{safe_country_name_fr}.png', bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
        print("Image created")
        sys.stdout.flush()
        plt.close(fig)  # Close the plot to avoid displaying it in a window

# Read the GeoJSON file
print("reading file...")
sys.stdout.flush()
data = gpd.read_file('country_border_generator\\custom.geo.json')
print("file read")

while True:
    print("\nEnter a country name, 'list' to show all countries, or type 'exit' to quit:\n")
    country_input = input("> ").strip()
    if country_input.lower() == 'exit':
        break
    elif country_input.lower() == 'list':
        print_all_countries()
    else:
        create_image_for_country(country_input)