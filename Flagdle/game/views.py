from django.shortcuts import render
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

def get_images_from_directory(directory):
    directory_path = os.path.join(ASSETS_DIR, 'country', directory)
    images = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append((os.path.join('country', directory, filename), filename))
    return images

# Country view available in-game
def images_view(request):
    categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
    selected_category = request.GET.get('category', categories[0])
    images = get_images_from_directory(selected_category)
    return render(request, 'images.html', {
        'images': images,
        'categories': categories,
        'selected_category': selected_category
    })

# Flag view available in-game
def fullname_view(request):
    directory_path = os.path.join(ASSETS_DIR, 'flags', 'fullname')
    images = []
    for filename in os.listdir(directory_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append((os.path.join('flags', 'fullname', filename), filename))
    return render(request, 'flags.html', {'images': images})
