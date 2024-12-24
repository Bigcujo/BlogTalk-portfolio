
#views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import (LoginView, 
                                        PasswordResetView, 
                                        PasswordResetDoneView,
                                        PasswordResetConfirmView,
                                        PasswordResetCompleteView)
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Profile, CustomUser, Follow
from blog.models import Post
from django.views.generic import ListView
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Views for the user app

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created successfully for {user_name}!, You can login now')
            form.save()
            return redirect('user-login')  # Redirect to login after successful registration
        else:
            print("Form is invalid")
            print(form.errors)
    else:
        form = UserRegistrationForm()
        print("GET request")

    return render(request, 'user/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'user/login.html'
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('blog-home')
    
class UserPostListView(ListView):
    model = Post
    template_name = 'user/user_posts.html'
    context_object_name = "posts"
    ordering = ['-date_posted']
    paginate_by = 4

    def get_queryset(self):
        user = CustomUser.objects.get(username=self.kwargs['username'])
        return Post.objects.filter(author=user).order_by('-date_posted')

class UserPasswordResetView(PasswordResetView):
    template_name = "user/password_reset.html"
    email_template_name = "user/password_reset_email.html"
    subject_template_name = "user/password_reset_subject.txt"
    success_url = reverse_lazy('password_reset_done')
    token_generator = default_token_generator
    form_class = PasswordResetForm
    from_email = None

    def get_email_context(self, user):
        context = {
            'email': user.email,
            'domain': self.request.META['HTTP_HOST'],
            'site_name': 'Your Site Name',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': self.token_generator.make_token(user),
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
        context['reset_url'] = self.request.build_absolute_uri(
            reverse_lazy('password_reset_confirm', kwargs={
                'uidb64': context['uid'],
                'token': context['token'],
            })
        )
        return context

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
        }
        for user in form.get_users(form.cleaned_data['email']):
            context = self.get_email_context(user)
            self.send_mail(
                self.subject_template_name, 
                self.email_template_name,
                context, 
                opts['from_email'], 
                user.email,
                html_email_template_name=self.html_email_template_name,
            )
        return super().form_valid(form)

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "user/password_reset_confirm.html"
    success_url = reverse_lazy('password_reset_complete')

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user/password_reset_complete.html'

@login_required
def profile(request, username=None):
    """
    View for updating your own profile or viewing another user's profile.
    """
    # If a username is provided, display that user's profile
    if username:
        user = get_object_or_404(CustomUser, username=username)
    else:
        user = request.user  # Default to current user's profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('user-profile', username=user.username)  # Redirect to the updated profile page
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user
    }
    return render(request, 'user/profile.html', context)

@login_required
def profile_dashboard(request, username):
    """
    Display the dashboard for viewing the profile, either own or of another user.
    """
    user = get_object_or_404(CustomUser, username=username)

    if request.method == 'GET':
        return render(request, 'user/profile_dashboard.html', {'user': user})
    else:
        return render(request, 'user/profile_dashboard.html', {'user': user, 'is_self': False})

@login_required
@csrf_exempt
def follow_user(request, username):
    user_to_follow = get_object_or_404(CustomUser, username=username)

    if request.user == user_to_follow:
        return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

    follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    
    if not created:
        follow.delete()
        button_text = "Follow"
        message = f"You have unfollowed {user_to_follow.username}."
    else:
        button_text = "Unfollow"
        message = f"You are now following {user_to_follow.username}."
    
    return JsonResponse({
        'button_text': button_text,
        'message': message
    })