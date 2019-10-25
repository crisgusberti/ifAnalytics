from django.urls import path
from ifAnalytics.views import geral
from ifAnalytics.views import notas
from ifAnalytics.views import frequencias
from ifAnalytics.views import suporte
from ifAnalytics.views import consulta_cursos
from ifAnalytics.views import consulta_campus
from ifAnalytics.views import consulta_periodos
from ifAnalytics.views import consulta_turmas
from ifAnalytics.views import get_data_forma_ingresso
from ifAnalytics.views import get_data_status_discente


urlpatterns = [
	# Cada uma das views definidas deve ser registrada aqui (lembrar de importar acima)
	# Na ordem: 'ENDEREÇO', 'FUNÇÃO(nome da view)', 'NAME=(opcional. Variável que referencia a view') 
	path('geral/', geral, name='geral'),
	path('notas/', notas, name='notas'),
	path('frequencias/', frequencias, name='frequencias'),
	path('suporte/', suporte, name='suporte'),
	path('consulta_cursos/', consulta_cursos, name='consulta_cursos'),
	path('consulta_campus/', consulta_campus, name='consulta_campus'),
	path('consulta_periodos/', consulta_periodos, name='consulta_periodos'),
	path('consulta_turmas/', consulta_turmas, name='consulta_turmas'),
	path('get_data_forma_ingresso/', get_data_forma_ingresso, name='get_data_forma_ingresso'),
	path('get_data_status_discente/', get_data_status_discente, name='get_data_status_discente'),
]
    