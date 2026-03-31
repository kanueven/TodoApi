from django.urls import path
from .views import login_view,register_view,logout_view

app_name = 'todos'

urlpatterns = [
 #template views
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', login_view, name='profile'),
    path('lists/', login_view, name='lists'),
    path('logout/', logout_view, name='logout'),
]