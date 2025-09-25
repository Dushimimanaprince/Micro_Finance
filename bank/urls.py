from django.urls import path
from . import views, view_auth

urlpatterns = [
    path('',views.index, name='index'),
    path('Signup',view_auth.register, name='signup'),
    path('login/',view_auth.signin, name='login'),
    path('logout',view_auth.logedout, name='logout'),
    path('admin-dashboard',views.admin_dashboards, name='admin'),
    path('Transfer-Page',views.transfer_page, name='transfer'),
    path('Sending',views.sending, name='sending'),
    path('Request',views.requesting, name='requests'),
    path('Requests',views.requesting_view, name='requesting'),
    path('Approve/<int:req_id>/',views.approve_request, name='approve'),
    path('Reject/<int:req_id>/',views.reject_request, name='reject'),
    path('add_balance/<int:wallet_id>/',views.add_balance, name='add_balance'),
    path('add_loan/<int:loans_id>/',views.add_loan, name='add_loan'),
]
