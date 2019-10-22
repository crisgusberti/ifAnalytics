from django.urls import path
from ifAnalytics.views import geral
from ifAnalytics.views import notas
from ifAnalytics.views import frequencias
from ifAnalytics.views import suporte


urlpatterns = [
	path('geral/', geral, name='geral'), #esse name='geral' serve para referenciar o link ao arquivo geral.html
	path('notas/', notas, name='notas'),
	path('frequencias/', frequencias, name='frequencias'),
	path('suporte/', suporte, name='suporte'),
	#path('campus/choices/ajax', campus_choices_ajax, name='campus_choices_ajax'),
]
    