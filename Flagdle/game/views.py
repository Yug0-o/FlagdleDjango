import os
import random

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView, FormView

from .forms import GuessForm
from .forms import SignUpForm
from .models import Score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'homepage.html'
    login_url = 'login'  # URL to redirect if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        return context


def get_images_from_directory(directory):
    directory_path = os.path.join(ASSETS_DIR, 'country', directory)
    images = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and 'icon' not in filename:
                filename_without_extension = os.path.splitext(filename)[0]
                images.append((os.path.join('country', directory, filename), filename_without_extension))
    return images


class ImagesView(LoginRequiredMixin, TemplateView):
    template_name = 'images.html'
    login_url = 'login'  # URL to redirect if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_image = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories_image[0])
        context['images'] = get_images_from_directory(selected_category)
        context['categories'] = categories_image
        context['selected_category'] = selected_category
        return context


class FullnameView(LoginRequiredMixin, TemplateView):
    template_name = 'flags.html'
    login_url = 'login'  # URL to redirect if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        directory_path = os.path.join(ASSETS_DIR, 'flags', 'fullname')
        images = []
        for filename in os.listdir(directory_path):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                filename_without_extension = os.path.splitext(filename)[0]
                images.append((os.path.join('flags', 'fullname', filename), filename_without_extension))
        context['images'] = images
        return context


class GameView(LoginRequiredMixin, FormView):
    template_name = 'game.html'
    login_url = 'login'  # URL to redirect if the user is not logged in
    form_class = GuessForm
    success_url = reverse_lazy('game')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories[0])
        images = get_images_from_directory(selected_category)

        if not images:
            context['message'] = 'No images found in this category.'
        else:
            context['categories'] = categories
            context['selected_category'] = selected_category
            context['images'] = images
            random_image = random.choice(images)
            context['current_image'] = random_image[0]
            context['correct_answer'] = random_image[1]

        # Add the scores to the context
        username = self.request.user
        score, created = Score.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')
        context['current_score'] = getattr(score, f"{score_field_prefix}_current_score")
        context['best_score'] = getattr(score, f"{score_field_prefix}_best_score")

        return context

    def form_valid(self, form):
        current_image = form.cleaned_data['current_image']
        user_guess = form.cleaned_data['guess'].strip().lower()
        correct_answer = form.cleaned_data['correct_answer'].strip().lower()
        correct_answer_without_extension = os.path.splitext(correct_answer)[0]

        if user_guess == correct_answer_without_extension:
            message = "Correct!"
            score_increment = 1
        else:
            message = f"Incorrect. The correct answer was {correct_answer_without_extension}."
            score_increment = 0

        # Update the user's score
        username = self.request.user
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories[0])
        score, created = Score.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')

        current_score_field = f"{score_field_prefix}_current_score"
        best_score_field = f"{score_field_prefix}_best_score"

        current_score = getattr(score, current_score_field)
        new_current_score = current_score + score_increment
        setattr(score, current_score_field, new_current_score)

        best_score = getattr(score, best_score_field)
        if new_current_score > best_score:
            setattr(score, best_score_field, new_current_score)

        score.save()

        images = get_images_from_directory(selected_category)
        random_image = random.choice(images)

        return self.render_to_response(self.get_context_data(
            form=form,
            categories=categories,
            selected_category=selected_category,
            current_image=random_image[0],
            correct_answer=random_image[1],
            message=message
        ))


@csrf_exempt
def reset_current_score(request):
    if request.method == 'POST':
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        username = request.user.username

        try:
            score = Score.objects.get(username=username)
        except Score.DoesNotExist:
            score = Score(username=username)

        # Itérer sur chaque catégorie et réinitialiser le score correspondant
        for category in categories:
            score_field_prefix = category.lower().replace('-', '_')
            current_score_field = f"{score_field_prefix}_current_score"
            if hasattr(score, current_score_field):
                setattr(score, current_score_field, 0)

        score.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'}, status=400)
