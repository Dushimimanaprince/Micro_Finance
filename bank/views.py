from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def index(request):
    usernames = request.user
    transactions= Transactions.objects.filter(
        models.Q(sender=usernames)| models.Q(receiver=usernames)     
    ).order_by('-transaction_at').first()
    requests = Requests.objects.filter(
        (models.Q(requester=usernames) | models.Q(payer=usernames)) & models.Q(is_paid=False)
    ).order_by('-request_at')
    
    requesting = Requests.objects.filter(
        (models.Q(requester=usernames) | models.Q(payer=usernames))
    ).order_by('-request_at').first()
    
    user_wallet= get_object_or_404(UserWallet, user=request.user)
    profiles= get_object_or_404(UserProfile, user=request.user)
    total_balance= user_wallet.balance + user_wallet.loan_balance
    
    context = {
        'txn':transactions,
        'requests':requests,
        'reque':requesting,
        'usernames': usernames,
        'user_wallet': user_wallet,
        'total_balance':total_balance,
        'profiles':profiles,
    }

    return render(request, 'bank/index.html', context)


@login_required
def admin_dashboards(request):
    wallets = UserWallet.objects.all()
    transactions = Transactions.objects.all().order_by('-transaction_at')
    today = timezone.now().date()
    trans = Transactions.objects.filter(transaction_at__date=today).count()
    profiles = UserProfile.objects.all()
    users = User.objects.all().count()

    # Get logged-in user's wallet safely
    user_wallet= get_object_or_404(UserWallet, user=request.user)

    context = {
        'users': users,
        'user_wallet': user_wallet,
        'wallets': wallets,
        'trans': trans,
        'transactions': transactions,
        'profiles': profiles
    }

    return render(request, 'bank/admin.html', context)


@login_required
def add_balance(request, wallet_id):
    wallet = get_object_or_404(UserWallet, id=wallet_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = int(amount)
                if amount > 0:
                    wallet.balance += amount
                    wallet.save()
                    Transactions.objects.create(
                        sender=None,  # ADMIN
                        receiver=wallet.user,
                        amount=amount,
                        purpose="deposit"
                    )
            except ValueError:
                pass
        return redirect('admin')
    return redirect('admin')


@login_required
def add_loan(request, loans_id):
    wallet = get_object_or_404(UserWallet, id=loans_id)
    if request.method == 'POST':
        amount = request.POST.get('amounting')
        if amount:
            try:
                amount = int(amount)
                if amount > 0:
                    wallet.loan_balance += amount
                    wallet.save()
                    Transactions.objects.create(
                        sender=None,  # ADMIN
                        receiver=wallet.user,
                        amount=amount,
                        purpose="loan"
                    )
            except ValueError:
                pass
        return redirect('admin')
    return redirect('admin')

def transfer_page(request):
    wallet= get_object_or_404(UserWallet, user=request.user)
    wallet= wallet.balance + wallet.loan_balance
    context= {'wallet':wallet,}
    return render(request,'bank/transfers.html',context)

def sending(request):
    wallet_obj = get_object_or_404(UserWallet, user=request.user)

    # total available balance including loan
    total_wallet = wallet_obj.balance + wallet_obj.loan_balance

    if request.method == "POST":
        name = request.POST.get('username')
        amount = request.POST.get('amount')

        if not name or not amount:
            messages.error(request, "Please provide names and amount")
            return redirect('transfer')

        try:
            receiver_user = User.objects.get(username=name)
        except User.DoesNotExist:
            messages.error(request, "Please provide the proper username")
            return redirect('transfer')

        if receiver_user == request.user:
            messages.error(request, "You can't send money to yourself")
            return redirect('transfer')

        try:
            amount = int(amount)
        except:
            messages.error(request, "Enter a valid amount")
            return redirect("transfer")

        if amount <= 0:
            messages.error(request, "Enter amount above 0")
            return redirect("transfer")

        if total_wallet < amount:
            messages.error(request, "Insufficient fund")
            return redirect("transfer")

        # deduct from sender
        if wallet_obj.balance >= amount:
            wallet_obj.balance -= amount
        else:
            # if not enough balance, use balance + loan logic if needed
            messages.error(request, "Insufficient balance in wallet")
            return redirect("transfer")
        wallet_obj.save()

        # add to receiver
        receiver_wallet, _ = UserWallet.objects.get_or_create(user=receiver_user)
        receiver_wallet.balance += amount
        receiver_wallet.save()

        # record transaction
        Transactions.objects.create(
            sender=request.user,
            receiver=receiver_user,
            amount=amount,
            purpose="transfer"
        )

        messages.success(request, f"Successfully sent {amount} to {receiver_user.username}")
        return redirect('transfer')


def requesting(request):
    
    return render(request,'bank/requests.html')

def requesting_view(request):
    if request.method == "POST":
            name= request.POST.get("username")
            amount= request.POST.get("amount")
            purpose= request.POST.get("purpose")
        
            if not name and amount and purpose:
                messages.error("Please Provide details on every field")
                return redirect('requests')
            
            try:
                requested_payer= User.objects.get(username=name)
            except User.DoesNotExist:
                messages.error("The User you trying to reach does not exist")
                return redirect("requests")
            
            amount = int(amount)
            
            if amount < 0:
                messages.error("Minimum Should be over 0")  
                return redirect("requests")
            
            if requested_payer == request.user:
                messages.error("You can't request to yourself")
                return redirect("requests")
            
            Requests.objects.create(
                requester= request.user,
                payer= requested_payer,
                amount= amount,
                purpose= purpose,
            )   
            
            return redirect("requests")

def approve_request(request, req_id):
    req= get_object_or_404(Requests, id=req_id, is_paid=False)
    payer_wallet= get_object_or_404(UserWallet,user=request.user)
    requester_wallet= get_object_or_404(UserWallet,user=req.requester)
    
    if payer_wallet.balance >= req.amount:
        
        payer_wallet.balance -=req.amount
        payer_wallet.save()
        
        requester_wallet.balance += req.amount
        requester_wallet.save()
        
        req.is_paid= True
        req.save()
        
        Transactions.objects.create(
            sender= request.user,
            receiver= req.requester,
            amount= req.amount,
            purpose= "request_payment"             
            
        )
        
        messages.success(request,"Request Approved")
        
    else:
        messages.error(request,"Insufficient Funds")
        
    return redirect("index")
        
def reject_request(request,req_id):
    req= get_object_or_404(Requests, id=req_id, payer=request.user , is_paid=False)
    
    req.delete()
    
    return redirect("index")