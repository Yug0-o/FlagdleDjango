from django.shortcuts import render
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Homepage
def home_view(request):
    categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
    return render(request, 'homepage.html', {'categories': categories})

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


def game_view(request):
    categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
    selected_category = request.GET.get('category', categories[0])
    images = get_images_from_directory(selected_category)

    if not images:
        return render(request, 'game.html', {
            'categories': categories,
            'selected_category': selected_category,
            'message': 'No images found in this category.'
        })

    if request.method == 'POST':
        current_image = request.POST.get('current_image')
        user_guess = request.POST.get('guess').strip().lower()
        correct_answer = request.POST.get('correct_answer').strip().lower()

        if user_guess == correct_answer:
            message = "Correct!"
        else:
            message = f"Incorrect. The correct answer was {correct_answer}."

        random_image = random.choice(images)
        return render(request, 'game.html', {
            'categories': categories,
            'selected_category': selected_category,
            'current_image': random_image[0],
            'correct_answer': random_image[1],
            'message': message
        })

    random_image = random.choice(images)
    return render(request, 'game.html', {
        'categories': categories,
        'selected_category': selected_category,
        'current_image': random_image[0],
        'correct_answer': random_image[1]
    })