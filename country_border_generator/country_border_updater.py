import matplotlib.pyplot as plt
import geopandas as gpd
from GeojsonToOrthographicProjection import create_projection
from unidecode import unidecode
import cartopy.crs as ccrs
import os

print("\n🔄 Loading country data...")
local_gdf = gpd.read_file('country_border_generator/custom.geojson')
country_folder = "Flagdle/assets/country"

languages = ["ar","bn","de","en","es","fa","fr","el","he","hi","hu","id","it","ja","ko","nl","pl","pt","ru","sv","tr","uk","ur","vi","zh","zht"]



def CountryName_to_png(country_name:str, save_path=''):
    """
    Given a country name, plot the country borders centered on the country's centroid.
    if save_path is not empty, save the plot to the path.
    """
    country_gdf, country_name = filter_country_gdf(local_gdf, country_name)

    if country_name == False:
        print("Country not found.")
        return False

    if country_gdf.empty:
        print("Country not found.")
        return False

    if save_path == '': print(f"🔄 Plotting {country_name}...\n")

    # Use the new create_projection function
    projection, (minx, maxx, miny, maxy), (central_longitude, central_latitude) = create_projection(country_gdf)

    print(f"❕ Center coordinates of {country_name}: {central_longitude}, {central_latitude}")
    
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    # ax.set_global()
    
    # Plot longitude and latitude lines
    ax.gridlines(draw_labels=False, linewidth=0.75, color='gray', alpha=0.5, linestyle='-')

    # Plot the chosen country in grey
    for _, row in country_gdf.iterrows():
        geom = row['geometry']
        ax.add_geometries([geom], ccrs.PlateCarree(), facecolor='#505060', edgecolor='#000000', linewidth=0.5, zorder=2)

    # if save_path == '': ax.plot(central_longitude, central_latitude, 'ro', markersize=5, transform=projection)

    ax.set_extent([minx, maxx, miny, maxy], crs=ccrs.PlateCarree())

    print(f"❕ Extent of {country_name}:\n\tminX : {minx:.2f}\n\tmaxX : {maxx:.2f}\n\tminY : {miny:.2f}\n\tmaxY : {maxy:.2f}")
    
    #-------------saving----------------

    plt.axis('off')
    if save_path == '':
        print(f"\n✅ Successfully plotted {country_name}.")
        plt.axis('off')
        plt.show(block=False)
    else:
        plt.savefig(save_path)
        
    return True




def print_country_names(language:str):
    """
    Print the names of all countries in the GeoDataFrame in alphabetical order.
    """
    for name in sorted(local_gdf[f'name_{language}']):
        print(f"\t- {name}")
    
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

def update_countries(country_folder:str):
    """
    Given a country folder, update the country borders of the images in the folder.
    """
    failed = []

    print("✅ Country border updater initialized.")

    i = 0
    # for each image in each folder in the country_folder, get the country name and update the country border
    for folder in os.listdir(country_folder):
        print(f"\n🔄 Updating {folder}...")
        for image in os.listdir(os.path.join(country_folder, folder)):
            country_name = image.split(".")[0]
            save_path = os.path.join(country_folder, folder, image)
            print(f"\n🔄 Updating {country_name}...")
            if CountryName_to_png(country_name, save_path): print(f"✅ Updated {country_name}")
            else :
                failed.append(f"{folder} > {country_name}")
                print(f"❌ Failed to update {country_name}")

            i += 1
            # if i > 1:
            #     quit(0)
            
        print(f"✅ Updated {folder}")
        print(f"❌ Failed to update:")
        for fail in failed:
            print(f"\t- {fail}")


    print("\n\n✅ Country border updater finished.")
    print(f"❌ Failed to update:")
    for fail in failed:
        print(f"\t- {fail}")

    return failed

def manual_update_countries():
    """
    Manually update the country borders of the images in the country folder.
    """
    while True:
        target_file = input("\nEnter the file path of the image to update (or type 'exit' to quit):\n> ")
        if target_file.lower() == 'exit':
            break
        elif not os.path.exists(target_file):
            print("File not found.")
            continue
        elif not target_file.endswith('.png'):
            print("Invalid file format. Please provide a PNG file.")
            continue

        country_name = target_file.split('\\')[-1].split('.')[0]
        print(f"\n🔄 Searching for '{country_name}'...")
        if filter_country_gdf(local_gdf, country_name)[1] == False:
            print("Country not found.\n")
            manual_update = input("Would you like to manually update the country? (Y/n)\n> ")
            if manual_update.lower() == 'n':
                continue
            else:
                #print all countries name
                print("languages available : ")
                for language in languages:
                    print(f"\t- {language}")
                    
                language = input("\n> ")
                if language not in languages:
                    print("Invalid language.")
                    continue
                
                print_country_names(language)
                    
                country_name = input("Enter the country name:\n> ")
                found_name = filter_country_gdf(local_gdf, country_name, language)[1]
                if found_name == False:
                    print("Country not found.")
                    continue

                print(f"✅ {found_name} found.")
                print(f"🔄 Updating {found_name}...")
                
                target_folder = "\\".join(target_file.split('\\')[:-1])
                
                print(f"\nSaving to '{target_folder}' as '{found_name}.png'")
                confirm = input("Confirm? (Y/n)\n> ")
                if confirm.lower() == 'n':
                    continue
                
                if CountryName_to_png(found_name, target_folder):
                    print(f"✅ Updated {country_name}")
                else:
                    print(f"❌ Failed to update {country_name}")
            

        #country found
        print(f"✅ {country_name} found.")
        print(f"🔄 Updating {country_name}...")
        if CountryName_to_png(country_name, target_file): print(f"✅ Updated {country_name}")
        else: print(f"❌ Failed to update {country_name}")

def plot_countries():
    """
    Plot the country borders centered on the country's centroid.
    """
    if __name__ == '__main__':
        # Loop to continuously ask for user input
        while True:
            country_name = input("\nEnter the country name (or type 'exit' to quit):\n> ")
            if country_name.lower() == 'exit':
                break
            
            elif country_name == 'list':
                print("languages available : ")
                for language in languages:
                    print(f"\t- {language}")
                language = input("\n> ")
                if language not in languages:
                    print("Invalid language.")
                    continue
                
                print_country_names(language)
                    
            elif country_name != '':
                CountryName_to_png(country_name)

if __name__ == '__main__':
    while True :
        choice = input("\n1: Auto-update\n2: Manual-update\n3: Simple-plot\n4: quit\n> ")
        if choice == '1':
            update_countries(country_folder)
        elif choice == '2':
            manual_update_countries()
        elif choice == '3':
            plot_countries()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")