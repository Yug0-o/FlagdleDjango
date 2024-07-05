import os
import random

from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django import forms

from .forms import GuessForm


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


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
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')) and 'icon' not in filename:
                filename_without_extension = os.path.splitext(filename)[0]
                images.append((os.path.join('country', directory, filename), filename_without_extension))
    return images

class ImagesView(LoginRequiredMixin, TemplateView):
    template_name = 'images.html'
    login_url = 'login'  # URL to redirect if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories[0])
        context['images'] = get_images_from_directory(selected_category)
        context['categories'] = categories
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
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
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

        return context

    def form_valid(self, form):
        current_image = form.cleaned_data['current_image']
        user_guess = form.cleaned_data['guess'].strip().lower()
        correct_answer = form.cleaned_data['correct_answer'].strip().lower()
        correct_answer_without_extension = os.path.splitext(correct_answer)[0]

        if user_guess == correct_answer_without_extension:
            message = "Correct!"
        else:
            message = f"Incorrect. The correct answer was {correct_answer_without_extension}."

        categories = ['Afrique', 'Amerique', 'Asie', 'Europe', 'Moyen-Orient', 'Oceanie']
        selected_category = self.request.GET.get('category', categories[0])
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
