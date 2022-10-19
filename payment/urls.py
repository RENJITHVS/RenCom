from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('selectaddresses/', views.selectAddresses, name='add-address'),
    path('setdefaultaddress/', views.set_default_address, name='set-default-address'),
    path('addbilling/', views.add_billing_details, name='add_billing_details'),
    path('setpaymentmethod/', views.set_payment_method, name='set-payment-method'),
    path('razorpay_payment_complete/', views.razorpay_payment_complete, name='razorpay_payment_complete'),
    path('paypal_payment_complete/', views.paypal_payment_complete, name='paypal_payment_complete'),
    path('payment_successful/', views.payment_successful, name='payment_successful'),
    

]
