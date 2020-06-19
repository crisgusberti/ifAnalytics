from django.urls import path
  
from autenticacao.views import login
from autenticacao.views import logout

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]
