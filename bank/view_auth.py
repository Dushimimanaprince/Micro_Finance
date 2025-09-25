from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from .forms import *

def register(request):
    if request.method == 'POST':
        form= SignupForm(request.POST,request.FILES)
        if form.is_valid():
            user=form.save()
            UserWallet.objects.create(user=user, balance=0,loan_balance=0)
            login(request,user)
            return redirect('index')
        
    else:
        form= SignupForm()
        
    context={'form':form}
    return render(request,'bank/signup.html',context)

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # ✅ Log the user in
            login(request, user)

            # ✅ Handle next parameter first
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            # ✅ Fallback: redirect by role
            if user.is_superuser or user.is_staff:
                return redirect('admin')   # make sure 'admin' matches your urls.py
            else:
                return redirect('index')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'bank/login.html', context)


def logedout(request):
    logout(request)
    return redirect('login')
