from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    #path('', auth_views.LoginView.as_view(template_name="pricing_app/login.html"), name='login'),
    path('', views.superuser_login, name='superuser_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quote/', views.quote_form, name='quote_form'),
    path("quote_description/", views.quote_description, name="quote_description")
    #path("predict/", views.predict_view, name="predict_price"),
]
