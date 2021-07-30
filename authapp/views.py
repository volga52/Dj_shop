from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, HttpResponseRedirect
from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm
from django.contrib import auth
from django.urls import reverse

from authapp.forms import ShopUserEditForm, ShopUserProfileEditForm
from authapp.models import ShopUser


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main'))
    title = 'вход'
    
    login_form = ShopUserLoginForm(data=request.POST or None)
    
    next = request.GET['next'] if 'next' in request.GET.keys() else ''
    #print('next', next)
    
    if request.method == 'POST' and login_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if 'next' in request.POST.keys():
                #print('redirect next', request.POST['next'])
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse('main'))

    content = {
        'title': title, 
        'login_form': login_form, 
        'next': next
    }
    
    return render(request, 'authapp/login.html', content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main'))
    

def register(request):
    title = 'регистрация'
    
    if request.method == 'POST':
        register_form = ShopUserRegisterForm(request.POST, request.FILES)
    
        if register_form.is_valid():
            user = register_form.save()
            send_verify_link(user)
            return HttpResponseRedirect(reverse('auth:login'))
    else:
        register_form = ShopUserRegisterForm()
    
    content = {'title': title, 'register_form': register_form}
    
    return render(request, 'authapp/register.html', content)
    

@login_required
@transaction.atomic
def edit(request):
    title = 'редактирование'
    
    if request.method == 'POST':
        edit_form = ShopUserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = ShopUserProfileEditForm(request.POST,instance=request.user.shopuserprofile)
        if edit_form.is_valid() and profile_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('auth:edit'))
    else:
        edit_form = ShopUserEditForm(instance=request.user)
        profile_form = ShopUserProfileEditForm(instance=request.user.shopuserprofile)
    
    content = {'title': title, 'edit_form': edit_form, 'profile_form': profile_form}
    
    return render(request, 'authapp/edit.html', content)


def send_verify_link(user):
    verify_link = reverse('auth:verify', args=[user.email, user.activation_key])
    subject = 'Account verify'
    message = f'Your link for account activation: {settings.DOMAIN_NAME}{verify_link}'
    return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def verify(request, email, key):
    try:
        user = ShopUser.objects.filter(email=email).first()
        if user and user.activation_key == key and not user.is_activation_key_expired():
            user.is_active = True
            user.activation_key = ''
            user.activation_key_created = None
            user.save()
            # auth.login(request, user)
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        else:
            print(f'key error activation user: {user}')

        return render(request, 'authapp/verify.html')

    except Exception as e:
        print(f'error activation user: {e.args}')

    return HttpResponseRedirect(reverse('main'))
