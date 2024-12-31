from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import EmailConfirmation


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                redirect_url = request.GET.get('next', 'home')
                return redirect(redirect_url)
            else:
                messages.error(
                    request, 
                    "Please confirm your email before logging in.",
                    extra_tags='alert alert-warning alert-dismissible fade show'
                )
        else:
            messages.error(
                request, 
                "Username Or Password is incorrect!",
                extra_tags='alert alert-warning alert-dismissible fade show'
            )

    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user but don't activate yet
            user = form.save()
            
            # Create email confirmation token
            confirmation = EmailConfirmation.objects.create(user=user)
            
            # Build confirmation link
            confirm_url = request.build_absolute_uri(
                f'/accounts/confirm/{confirmation.token}/'
            )
            
            # Prepare email
            html_message = render_to_string('accounts/confirmation_email.html', {
                'user': user,
                'confirm_url': confirm_url
            })
            plain_message = strip_tags(html_message)
            
            # Send confirmation email
            send_mail(
                'Confirm your registration',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Registration successful! Please check your email to confirm your account.',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def confirm_email(request, token):
    confirmation = get_object_or_404(EmailConfirmation, token=token, is_confirmed=False)
    
    # Activate user
    user = confirmation.user
    user.is_active = True
    user.save()
    
    # Mark confirmation as complete
    confirmation.is_confirmed = True
    confirmation.save()
    
    messages.success(
        request,
        'Email confirmed! You can now login to your account.',
        extra_tags='alert alert-success alert-dismissible fade show'
    )
    return redirect('login')


def logout_view(request):
    logout(request)
    messages.success(
        request, 
        "You have been successfully logged out!", 
        extra_tags='alert alert-success alert-dismissible fade show'
    )
    return redirect('home')
