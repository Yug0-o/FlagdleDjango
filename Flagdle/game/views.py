import os
import random

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView, FormView

from .forms import GuessForm, SignUpForm
from .models import BestScore, CurrentScore
from .Base64EncoderDecoder import base64_to_utf8

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


class HomeView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        context['flag_categories'] = ['World', 'Pride']
        return context


def get_from_directory(directory, subdirectory):
    directory_path = os.path.join(ASSETS_DIR, directory, subdirectory)
    images = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and 'icon' not in filename:
                filename_without_extension = os.path.splitext(filename)[0]
                images.append((os.path.join(ASSETS_DIR, directory, subdirectory, filename), filename_without_extension))
    return images


class ImagesView(TemplateView):
    template_name = 'images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_image = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories_image[0])
        images = get_from_directory("country", selected_category)

        # Transform filenames
        transformed_images = [(image, base64_to_utf8(filename)) for image, filename in images]

        context['images'] = transformed_images
        context['categories'] = categories_image
        context['selected_category'] = selected_category
        return context


class FlagView(TemplateView):
    template_name = 'flags.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_image = ['World', 'Pride']
        selected_category = self.request.GET.get('category', categories_image[0])
        images = get_from_directory("flags", selected_category)

        # Transform filenames
        transformed_images = [(image, base64_to_utf8(filename)) for image, filename in images]

        context['images'] = transformed_images
        context['categories'] = categories_image
        context['selected_category'] = selected_category
        return context


class CountryGameView(LoginRequiredMixin, FormView):
    template_name = 'country_game.html'
    login_url = 'login'  # URL to redirect if the user is not logged in
    form_class = GuessForm
    success_url = reverse_lazy('country_game')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories[0])
        images = get_from_directory("country", selected_category)

        # Transform filenames
        transformed_images = [(image, base64_to_utf8(filename)) for image, filename in images]

        if not transformed_images:
            context['message'] = 'No images found in this category.'
        else:
            context['categories'] = categories
            context['selected_category'] = selected_category
            context['images'] = transformed_images
            random_image = random.choice(transformed_images)
            context['current_image'] = random_image[0]
            context['correct_answer'] = random_image[1]

        # Add the scores to the context
        username = self.request.user

        best_score, best_created = BestScore.objects.get_or_create(username=username)
        current_score, current_created = CurrentScore.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')
        context['current_score'] = getattr(current_score, f"{score_field_prefix}_current_score", 0)
        context['best_score'] = getattr(best_score, f"{score_field_prefix}_best_score", 0)

        return context

    def form_valid(self, form):
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
        best_score, best_created = BestScore.objects.get_or_create(username=username)
        current_score, current_created = CurrentScore.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')

        current_score_field = f"{score_field_prefix}_current_score"
        best_score_field = f"{score_field_prefix}_best_score"

        current_score_val = getattr(current_score, current_score_field, 0)
        new_current_score = current_score_val + score_increment
        setattr(current_score, current_score_field, new_current_score)
        current_score.save()

        best_score_val = getattr(best_score, best_score_field, 0)
        if new_current_score > best_score_val:
            setattr(best_score, best_score_field, new_current_score)
            best_score.save()

        images = get_from_directory("country", selected_category)

        # Transform filenames
        transformed_images = [(image, base64_to_utf8(filename)) for image, filename in images]

        random_image = random.choice(transformed_images)

        return self.render_to_response(self.get_context_data(
            form=form,
            categories=categories,
            selected_category=selected_category,
            current_image=random_image[0],
            correct_answer=random_image[1],
            message=message
        ))


class FlagsGameView(LoginRequiredMixin, FormView):
    template_name = 'flag_game.html'
    login_url = 'login'  # URL to redirect if the user is not logged in
    form_class = GuessForm
    success_url = reverse_lazy('flag_game')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flag_categories = ['World', 'Pride']
        selected_category = self.request.GET.get('flag_category', flag_categories[0])
        images = get_from_directory("flags", selected_category)

        # Transform filenames
        transformed_images = [(image, base64_to_utf8(filename)) for image, filename in images]

        if not transformed_images:
            context['message'] = 'No images found in this category.'
        else:
            context['flag_categories'] = flag_categories
            context['selected_category'] = selected_category
            context['images'] = transformed_images
            random_image = random.choice(transformed_images)
            context['current_image'] = random_image[0]
            context['correct_answer'] = random_image[1]

        # Add the scores to the context
        username = self.request.user

        best_score, best_created = BestScore.objects.get_or_create(username=username)
        current_score, current_created = CurrentScore.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')
        context['current_score'] = getattr(current_score, f"{score_field_prefix}_current_score", 0)
        context['best_score'] = getattr(best_score, f"{score_field_prefix}_best_score", 0)

        return context

    def form_valid(self, form):
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
        flag_categories = ['World', 'Pride']
        selected_category = self.request.GET.get('flag_category', flag_categories[0])
        best_score, best_created = BestScore.objects.get_or_create(username=username)
        current_score, current_created = CurrentScore.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')

        current_score_field = f"{score_field_prefix}_current_score"
        best_score_field = f"{score_field_prefix}_best_score"

        current_score_val = getattr(current_score, current_score_field, 0)
        new_current_score = current_score_val + score_increment
        setattr(current_score, current_score_field, new_current_score)
        current_score.save()

        best_score_val = getattr(best_score, best_score_field, 0)
        if new_current_score > best_score_val:
            setattr(best_score, best_score_field, new_current_score)
            best_score.save()

        images = get_from_directory("flags", selected_category)

        # Transform filenames
        transformed_images = [(image, base64_to_utf8(filename)) for image, filename in images]

        random_image = random.choice(transformed_images)

        return self.render_to_response(self.get_context_data(
            form=form,
            flag_categories=flag_categories,
            selected_category=selected_category,
            current_image=random_image[0],
            correct_answer=random_image[1],
            message=message
        ))


# file deepcode ignore DisablesCSRFProtection: <not a security issue>
@csrf_exempt
def reset_current_score(request):
    if request.method == 'POST':
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie', 'World', 'Pride']
        username = request.user.username

        try:
            score = CurrentScore.objects.get(username=username)
        except CurrentScore.DoesNotExist:
            score = CurrentScore(username=username)

        # Iterate over each category and reset the corresponding score
        for category in categories:
            score_field_prefix = category.lower().replace('-', '_')
            current_score_field = f"{score_field_prefix}_current_score"
            if hasattr(score, current_score_field):
                setattr(score, current_score_field, 0)

        score.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'}, status=400)


class LeaderboardView(TemplateView):
    template_name = 'leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie', 'World', 'Pride']
        scores = BestScore.objects.all()

        leaderboard = []

        for score in scores:
            if score.username:
                user_scores = {
                    'username': score.username,
                    'total_best_score': 0,
                    'scores': {}
                }

                for category in categories:
                    best_score_field = f"{category.lower().replace('-', '_')}_best_score"
                    best_score = getattr(score, best_score_field, 0)
                    user_scores['scores'][category] = best_score
                    user_scores['total_best_score'] += best_score

                leaderboard.append(user_scores)

        # Tri des utilisateurs par le score total décroissant
        leaderboard = sorted(leaderboard, key=lambda x: x['total_best_score'], reverse=True)

        context['leaderboard'] = leaderboard
        context['categories'] = categories

        return context
