import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
import os

import GeojsonToOrthographicProjection as gtop

print("\n🔄 Loading country data...")
World_gdf = gpd.read_file('country_border_generator/custom.geojson')
country_folder = "Flagdle/assets/country"

# retrieve the languages from the GeoDataFrame
languages = [col.split('_')[1] for col in World_gdf.columns if col.startswith('name_')]

def CountryName_to_png(country_name:str, save_path=''):
    """
    Given a <country_name>, create an image of the country centered on the country's centroid.\n
    If <save_path> is specified, save the image to the path.
    Else, display the image.
    """
    country_gdf, country_name = gtop.filter_country_gdf(World_gdf, country_name)

    if country_name == False:
        print("Country not found.")
        return False

    if country_gdf.empty:
        print("Country not found.")
        return False

    if save_path == '': print(f"🔄 Plotting {country_name}...\n")

    projection, (minx, maxx, miny, maxy), (central_longitude, central_latitude) = gtop.create_projection(country_gdf)

    print(f"❕ Center coordinates of {country_name}: {central_longitude}, {central_latitude}")
    
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    
    # Plot longitude and latitude lines
    ax.gridlines(draw_labels=False, linewidth=0.75, color='gray', alpha=0.5, linestyle='-')

    # Plot the chosen country in grey
    for _, row in country_gdf.iterrows():
        geom = row['geometry']
        ax.add_geometries([geom], ccrs.PlateCarree(), facecolor='#505060', edgecolor='#000000', linewidth=0.5, zorder=2)

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
    Print the names of all countries in the specified language
    """
    for name in sorted(World_gdf[f'name_{language}']):
        print(f"\t- {name}")
    
def auto_update_countries(country_folder:str):
    """
    Given a country folder, update the country borders of the images in the folder.
    """
    failed = []

    print("🔄 Country border updater initialized.")

    for folder in os.listdir(country_folder):
        print(f"\n🔄 Updating {folder}...")
        
        for image in os.listdir(os.path.join(country_folder, folder)):
            country_name = image.split(".")[0]
            save_path = os.path.join(country_folder, folder, image)
            
            print(f"\n🔄 Updating {country_name}...")

            if CountryName_to_png(country_name, save_path):
                print(f"✅ Updated {country_name}")
            else :
                failed.append(f"{folder} > {country_name}")
                print(f"❌ Failed to update {country_name}")
            
    print("\n\n✅ Country border updater finished.")
    
    if len(failed) == 0:
        print("✅All countries updated successfully.")
    else:
        print(f"❌ Failed to update:")
        for fail in failed:
            print(f"\t- {fail}")

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
                
                if CountryName_to_png(found_name, target_folder):
                    print(f"✅ Updated {country_name}")
                else:
                    print(f"❌ Failed to update {country_name}")
            

        print(f"✅ {country_name} found.")
        print(f"🔄 Updating {country_name}...")
        if CountryName_to_png(country_name, target_file): print(f"✅ Updated {country_name}")
        else: print(f"❌ Failed to update {country_name}")

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
            CountryName_to_png(country_name)


if __name__ == '__main__':
    while True :
        choice = input("\n1: Auto-update\n2: Manual-update\n3: Simple-plot\n4: quit\n> ")
        if choice == '1':
            auto_update_countries(country_folder)
        elif choice == '2':
            manual_update_countries()
        elif choice == '3':
            plot_countries()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")