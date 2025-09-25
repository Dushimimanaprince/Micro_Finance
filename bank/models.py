from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    phone= models.CharField(max_length=100)
    profile= models.ImageField(upload_to='images' ,blank=True, null=True)
    added_at= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} --> {self.phone} "
    

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)  
    loan_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} balance {self.balance} | loan {self.loan_balance}"

    @property
    def total_balance(self):
        return self.balance + self.loan_balance

    
    
class Requests(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests_made")
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests_to_pay")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    purpose = models.CharField(max_length=100)
    request_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.requester.username} requested {self.amount} from {self.payer.username}"

    
    
class Transactions(models.Model):
    PURPOSE_CHOICES = [
        ("deposit", "Deposit"),
        ("loan", "Loan"),
        ("transfer", "Transfer"),
        ("request_payment", "Request Payment"),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_transactions", null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="deposit")


    def __str__(self):
        sender_name = self.sender.username if self.sender else "ADMIN"
        return f"{sender_name} -> {self.receiver.username} ({self.amount})"

    

       