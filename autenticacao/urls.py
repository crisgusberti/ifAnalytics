from django.urls import path
  
from autenticacao.views import index
from autenticacao.views import logout

urlpatterns = [
    path('index/', index, name='index'),
    path('logout/', logout, name='logout'),
]
