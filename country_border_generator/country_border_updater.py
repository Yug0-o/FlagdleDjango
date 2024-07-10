import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
import threading
import os

import GeojsonToOrthographicProjection as gtop
import png_to_webp as ptw

DEBUG_FULL = False
DEBUG_INFO = True
data_path = 'country_border_generator/custom.geojson'
if DEBUG_INFO: print(f"\n🔄 Loading Geojson '{data_path}'...")
World_gdf = gpd.read_file(data_path)
country_folder = "Flagdle/assets/country"

# list continents in country_folder
continents = gtop.continents

# retrieve the languages from the GeoDataFrame
languages = [col.split('_')[1] for col in World_gdf.columns if col.startswith('name_')]

def CountryName_to_image(country_name:str, save_path='', gdf=World_gdf):
    """
    Given a <country_name>, create an image of the country centered on the country's centroid.\n
    If <save_path> is specified, save the image to the path.
    Else, display the image.
    """
    if DEBUG_FULL: print(f"\n🔄 Searching for '{country_name}'...")
    country_gdf, country_name = gtop.filter_country_gdf(local_gdf=World_gdf, country_name=country_name, DEBUG_FULL=DEBUG_FULL, DEBUG_INFO=DEBUG_INFO)

    if country_name == False:
        if DEBUG_INFO: print("Country not found.")
        return False

    if country_gdf.empty:
        if DEBUG_INFO: print("Country GDF empty.")
        return False

    if save_path == '':
        if DEBUG_INFO: print(f"\n🔄 Plotting {country_name}...\n")

    projection, (minx, maxx, miny, maxy), (central_longitude, central_latitude) = gtop.create_projection(country_gdf=country_gdf, DEBUG_FULL=DEBUG_FULL, DEBUG_INFO=DEBUG_INFO)

    if DEBUG_FULL: print(f"\n❕ Center coordinates of {country_name}: {central_longitude:2f}, {central_latitude:2f}")

    dpi = 100

    water_color = '#070715'
    land_color = '#D0E0D0'
    line_color = '#A0A0A0'
    
    fig = plt.figure(figsize=(7, 7), facecolor=water_color)
    ax = fig.add_subplot(1, 1, 1, projection=projection )

    if miny < -90 or maxy > 90:
        ax.set_global()
    else:
        ax.set_extent([minx, maxx, miny, maxy], crs=ccrs.PlateCarree())
        
    # Plot longitude and latitude lines
    ax.gridlines(draw_labels=False, linewidth=0.75, color=line_color, alpha=0.5, linestyle='--')
    # Plot the chosen country in grey
    for _, row in country_gdf.iterrows():
        geom = row['geometry']
        ax.add_geometries([geom], ccrs.PlateCarree(), facecolor=land_color, edgecolor=water_color, linewidth=0.5, zorder=2)

    if DEBUG_FULL: print(f"❕ Extent of {country_name}:\n\tminX : {minx:.2f}\n\tmaxX : {maxx:.2f}\n\tminY : {miny:.2f}\n\tmaxY : {maxy:.2f}")
    
    #-------------saving----------------

    plt.axis('off')
    if save_path == '':
        if DEBUG_INFO: print(f"\n✅ Successfully plotted {country_name}.")
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.show(block=True)
    else:
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
        ptw.convert_png_to_webp(save_path)

    plt.close()
        
    return True


def print_country_names(language:str):
    """
    Print the names of all countries in the specified language
    """
    for name in sorted(World_gdf[f'name_{language}']):
        print(f"\t- {name}")


def update_image(country_name:str, folder:str, image:str):
    """
    Update the country borders of the images in the folder.
    """
    global failed
    
    if DEBUG_INFO: print(f"\t-🔄 Updating {country_name}...")
    if country_name == "icon":
        country_name = folder
        image = "icon.png"
        
    save_path = os.path.join(country_folder, folder, image)
    if CountryName_to_image(country_name, save_path):
        if DEBUG_FULL: print(f"\t✅ Updated {country_name}")
        if image == "icon.png":
            print(f"✅ Updated {folder}'s icon\n")
    else :
        failed.append(f"{folder} > {country_name}")
        if DEBUG_FULL: print(f"\t❌ Failed to update {country_name}")


def update_folder(country_folder:str, folder:str):
    """
    Update the country borders of the images in the folder.
    """
    if DEBUG_INFO: print(f"\n🔄 Updating folder {folder}...")
    for image in os.listdir(os.path.join(country_folder, folder)):
        country_name = image.split(".")[0]
        update_image(country_name, folder, image)


def auto_update_countries(country_folder:str, threaded:bool=False):
    """
    Given a country folder, update the country borders of the images in the folder.
    """
    global failed
    failed = []

    if DEBUG_INFO: print("🔄 Country border updater initialized.")

    for folder in os.listdir(country_folder):
        if threaded:
            thread = threading.Thread(target=update_folder, args=(country_folder, folder))
            thread.start()
            thread.join()
        else:
            update_folder(country_folder, folder)
        
    if DEBUG_INFO: print("\n\n✅ Country border updater finished.")
    
    if len(failed) == 0:
        if DEBUG_INFO: print("✅ All countries updated successfully.")
    else:
        if DEBUG_INFO: print(f"❌ Failed to update:")
        for fail in failed:
            if DEBUG_INFO: print(f"\t- {fail}")

    return failed


def manual_update_countries():
    """
    Manually update the country borders of the images in the folder.
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
        
        if gtop.filter_country_gdf(World_gdf, country_name)[1] == False:
            print("Country not found.\n")
            
            manual_update = input("Would you like to manually update the country? (Y/n)\n> ")
            if manual_update.lower() == 'n':
                continue
            else:
                print("languages available : ")
                for language in languages:
                    print(f"\t- {language}")
                    
                language = input("\n> ")
                if language not in languages:
                    print("Invalid language.")
                    continue
                
                print_country_names(language)
                    
                country_name = input("Enter the country name:\n> ")
                found_name = gtop.filter_country_gdf(World_gdf, country_name, language)[1]
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
                
                if CountryName_to_image(found_name, target_folder):
                    print(f"✅ Updated {country_name}")
                else:
                    print(f"❌ Failed to update {country_name}")
            

        print(f"✅ {country_name} found.")
        print(f"🔄 Updating {country_name}...")
        
        if CountryName_to_image(country_name, target_file):
            print(f"✅ Updated {country_name}")
        else: 
            print(f"❌ Failed to update {country_name}")


def plot_countries():
    """
    Plot the country borders of the images in the folder.
    """
    while True:
        country_name = input("\nEnter the name of the country to plot (or type 'exit' to quit, 'list' to list languages):\n> ")
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
            CountryName_to_image(country_name)


if __name__ == '__main__':
    while True :
        choice = input("\n1: Auto-update\n2: Manual-update\n3: Simple-plot\n4: quit\n> ")
        if choice == '1':
            auto_update_countries(country_folder, False)
        elif choice == '2':
            manual_update_countries()
        elif choice == '3':
            plot_countries()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")