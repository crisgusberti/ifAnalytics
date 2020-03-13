from django.urls import path
from ifAnalytics.views import geral
from ifAnalytics.views import notas
from ifAnalytics.views import frequencias
from ifAnalytics.views import suporte
from ifAnalytics.views import detalhes
from ifAnalytics.views import consulta_cursos
from ifAnalytics.views import consulta_campus
from ifAnalytics.views import consulta_periodos
from ifAnalytics.views import consulta_turmas
from ifAnalytics.views import get_data_forma_ingresso
from ifAnalytics.views import get_data_status_discente
from ifAnalytics.views import get_data_total_matriculas
from ifAnalytics.views import get_data_concluintes
from ifAnalytics.views import get_data_tamanho_turmas
from ifAnalytics.views import get_data_discentes_evadidos
from ifAnalytics.views import get_data_notas_parciais
from ifAnalytics.views import get_data_medias_finais


urlpatterns = [
	# Cada uma das views definidas deve ser registrada aqui (lembrar de importar acima)
	# Na ordem: 'ENDEREÇO', 'FUNÇÃO(nome da view)', 'NAME=(opcional. Variável que referencia a view') 
	path('geral/', geral, name='geral'),
	path('notas/', notas, name='notas'),
	path('frequencias/', frequencias, name='frequencias'),
	path('suporte/', suporte, name='suporte'),
	path('detalhes/', detalhes, name='detalhes'),
	path('consulta_cursos/', consulta_cursos, name='consulta_cursos'),
	path('consulta_campus/', consulta_campus, name='consulta_campus'),
	path('consulta_periodos/', consulta_periodos, name='consulta_periodos'),
	path('consulta_turmas/', consulta_turmas, name='consulta_turmas'),
	path('get_data_forma_ingresso/', get_data_forma_ingresso, name='get_data_forma_ingresso'),
	path('get_data_status_discente/', get_data_status_discente, name='get_data_status_discente'),
	path('get_data_total_matriculas/', get_data_total_matriculas, name='get_data_total_matriculas'),
	path('get_data_concluintes/', get_data_concluintes, name='get_data_concluintes'),
	path('get_data_tamanho_turmas/', get_data_tamanho_turmas, name='get_data_tamanho_turmas'),
	path('get_data_discentes_evadidos/', get_data_discentes_evadidos, name='get_data_discentes_evadidos'),
	path('get_data_notas_parciais/', get_data_notas_parciais, name='get_data_notas_parciais'),
	path('get_data_medias_finais/', get_data_medias_finais, name='get_data_medias_finais'),
]
    