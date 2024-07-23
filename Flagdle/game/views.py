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
from .Base32EncoderDecoder import base32_to_utf8

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
        self.request.session['guesses'] = []
        # reset the shown images in the session
        for category in context['categories']:
            self.request.session[f'shown_images_{category}'] = []
        for category in context['flag_categories']:
            self.request.session[f'shown_images_{category}'] = []
        
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
        transformed_images = [(image, base32_to_utf8(filename)) for image, filename in images]

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
        transformed_images = [(image, base32_to_utf8(filename)) for image, filename in images]

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
        transformed_images = [(image, base32_to_utf8(filename)) for image, filename in images]

        if not transformed_images:
            context['message'] = 'No images found in this category.'
        else:
            context['categories'] = categories
            context['selected_category'] = selected_category

            # Get already shown images from the session
            shown_images = self.request.session.get(f'shown_images_{selected_category}', [])
            remaining_images = [img for img in transformed_images if img[0] not in shown_images]

            if not remaining_images:
                context['message'] = 'Congratulations! You have guessed all the images in this category.'
                context['all_guessed'] = True
                self.request.session[f'shown_images_{selected_category}'] = []
            else:    
                context['images'] = remaining_images
                random_image = random.choice(remaining_images)
                context['current_image'] = random_image[0]
                context['correct_answer'] = random_image[1]

        # Add the scores to the context
        username = self.request.user

        best_score, best_created = BestScore.objects.get_or_create(username=username)
        current_score, current_created = CurrentScore.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')

        # if the remaining_images is the same number as the max score, reset the current score
        if len(remaining_images) == len(transformed_images):
            setattr(current_score, f"{score_field_prefix}_current_score", 0)
            current_score.save()
        
        context['current_score'] = getattr(current_score, f"{score_field_prefix}_current_score", 0)
        context['best_score'] = getattr(best_score, f"{score_field_prefix}_best_score", 0)
        return context

    def form_valid(self, form):
        user_guess = form.cleaned_data['guess'].strip().lower()

        guesses = self.request.session.get('guesses', [])
        if not guesses:
            self.request.session['guesses'] = []
            guesses = []

        correct_answer = form.cleaned_data['correct_answer'].strip().lower()
        correct_answer_without_extension = os.path.splitext(correct_answer)[0]

        message = ""
        score_increment = 0
        if user_guess not in guesses:
            if user_guess == correct_answer_without_extension:
                message = "Correct!"
                guesses.append(user_guess)
                self.request.session['guesses'] = guesses
                score_increment = 1
            else:
                if user_guess not in guesses:
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

        max_score = len(get_from_directory("country", selected_category))

        current_score_val = getattr(current_score, current_score_field, 0)/100 * max_score

        new_current_score = round(current_score_val + score_increment)
        new_current_score_percentage = round(new_current_score/max_score * 100)

        setattr(current_score, current_score_field, new_current_score_percentage)
        current_score.save()

        best_score_percentage = getattr(best_score, best_score_field, 0)
        if new_current_score_percentage > best_score_percentage:
            setattr(best_score, best_score_field, new_current_score_percentage)
            best_score.save()

        images = get_from_directory("country", selected_category)

        # Transform filenames
        transformed_images = [(image, base32_to_utf8(filename)) for image, filename in images]

        # Update shown images in the session
        shown_images = self.request.session.get(f'shown_images_{selected_category}', [])
        shown_images.append(form.cleaned_data['current_image'])
        self.request.session[f'shown_images_{selected_category}'] = shown_images

        remaining_images = [img for img in transformed_images if img[0] not in shown_images]

        if not remaining_images:
            self.request.session['guesses'] = []
            message = 'Congratulations! You have guessed all the images in this category.'
            self.request.session[f'shown_images_{selected_category}'] = []
            context = self.get_context_data(
                form=form,
                categories=categories,
                selected_category=selected_category,
                message=message,
                all_guessed=True
            )
        else:   
            random_image = random.choice(remaining_images)
            context = self.get_context_data(
                form=form,
                categories=categories,
                selected_category=selected_category,
                current_image=random_image[0],
                correct_answer=random_image[1],
                message=message,
                all_guessed=False
            )

        return self.render_to_response(context)


class FlagsGameView(LoginRequiredMixin, FormView):
    template_name = 'flag_game.html'
    login_url = 'login'  # URL to redirect if the user is not logged in
    form_class = GuessForm
    success_url = reverse_lazy('flag_game')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = ['Pride', 'World']
        selected_category = self.request.GET.get('category', categories[0])
        images = get_from_directory("flags", selected_category)

        # Transform filenames
        transformed_images = [(image, base32_to_utf8(filename)) for image, filename in images]

        if not transformed_images:
            context['message'] = 'No images found in this category.'
        else:
            context['categories'] = categories
            context['selected_category'] = selected_category

            # Get already shown images from the session
            shown_images = self.request.session.get(f'shown_images_{selected_category}', [])
            remaining_images = [img for img in transformed_images if img[0] not in shown_images]

            if not remaining_images:
                context['message'] = 'Congratulations! You have guessed all the images in this category.'
                context['all_guessed'] = True
                self.request.session[f'shown_images_{selected_category}'] = []
            else:
                context['images'] = remaining_images
                random_image = random.choice(remaining_images)
                context['current_image'] = random_image[0]
                context['correct_answer'] = random_image[1]

        # Add the scores to the context
        username = self.request.user

        best_score, best_created = BestScore.objects.get_or_create(username=username)
        current_score, current_created = CurrentScore.objects.get_or_create(username=username)
        score_field_prefix = selected_category.lower().replace('-', '_')

        # if the remaining_images is the same number as the max score, reset the current score
        if len(remaining_images) == len(transformed_images):
            setattr(current_score, f"{score_field_prefix}_current_score", 0)
            current_score.save()

        context['current_score'] = getattr(current_score, f"{score_field_prefix}_current_score", 0)
        context['best_score'] = getattr(best_score, f"{score_field_prefix}_best_score", 0)
        return context

    def form_valid(self, form):
        user_guess = form.cleaned_data['guess'].strip().lower()

        guesses = self.request.session.get('guesses', [])
        if not guesses:
            self.request.session['guesses'] = []
            guesses = []

        correct_answer = form.cleaned_data['correct_answer'].strip().lower()
        correct_answer_without_extension = os.path.splitext(correct_answer)[0]

        message = ""
        score_increment = 0
        if user_guess not in guesses:
            if user_guess == correct_answer_without_extension:
                score_increment = 1
                message = "Correct!"
                guesses.append(user_guess)
                self.request.session['guesses'] = guesses
            else:
                if user_guess not in guesses:
                    message = f"Incorrect. The correct answer was {correct_answer_without_extension}."
                score_increment = 0

        # Update the user's score
        username = self.request.user

        categories = ['Pride', 'World']

        selected_category = self.request.GET.get('category', categories[0])

        best_score, best_created = BestScore.objects.get_or_create(username=username)

        current_score, current_created = CurrentScore.objects.get_or_create(username=username)

        score_field_prefix = selected_category.lower().replace('-', '_')

        current_score_field = f"{score_field_prefix}_current_score"
        best_score_field = f"{score_field_prefix}_best_score"

        max_score = len(get_from_directory("flags", selected_category))

        current_score_val = getattr(current_score, current_score_field, 0) / 100 * max_score  # return 0.0, not normal

        new_current_score = round(current_score_val + score_increment)
        new_current_score_percentage = round(new_current_score / max_score * 100)

        setattr(current_score, current_score_field, new_current_score_percentage)
        current_score.save()

        best_score_percentage = getattr(best_score, best_score_field, 0)
        if new_current_score_percentage > best_score_percentage:
            setattr(best_score, best_score_field, new_current_score_percentage)
            best_score.save()

        images = get_from_directory("flags", selected_category)

        # Transform filenames
        transformed_images = [(image, base32_to_utf8(filename)) for image, filename in images]

        # Update shown images in the session
        shown_images = self.request.session.get(f'shown_images_{selected_category}', [])
        shown_images.append(form.cleaned_data['current_image'])
        self.request.session[f'shown_images_{selected_category}'] = shown_images

        remaining_images = [img for img in transformed_images if img[0] not in shown_images]

        if not remaining_images:
            self.request.session['guesses'] = []
            message = 'Congratulations! You have guessed all the images in this category.'
            self.request.session[f'shown_images_{selected_category}'] = []
            context = self.get_context_data(
                form=form,
                categories=categories,
                selected_category=selected_category,
                message=message,
                all_guessed=True
            )
        else:
            random_image = random.choice(remaining_images)
            context = self.get_context_data(
                form=form,
                categories=categories,
                selected_category=selected_category,
                current_image=random_image[0],
                correct_answer=random_image[1],
                message=message,
                all_guessed=False
            )

        return self.render_to_response(context)


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
                    'scores': {},
                    'categories_count': 0
                }

                for category in categories:
                    best_score_field = f"{category.lower().replace('-', '_')}_best_score"
                    best_score = getattr(score, best_score_field, 0)
                    user_scores['scores'][category] = best_score
                    user_scores['total_best_score'] += best_score
                    user_scores['categories_count'] += 1

                if user_scores['categories_count'] > 0:
                    user_scores['average_best_score'] = round(user_scores['total_best_score'] / user_scores['categories_count'])
                else:
                    user_scores['average_best_score'] = 0  # Handle case where user has no scores

                leaderboard.append(user_scores)

        # Sort users by the average score in descending order
        leaderboard = sorted(leaderboard, key=lambda x: x['average_best_score'], reverse=True)

        context['leaderboard'] = leaderboard
        context['categories'] = categories

        return context
