from django.urls import path
from ifAnalytics.views import geral, notas, frequencias, suporte, consulta_campus, consulta_cursos, consulta_periodos, consulta_turmas
# from ifAnalytics.views import notas
# from ifAnalytics.views import frequencias
# from ifAnalytics.views import suporte
# from ifAnalytics.views import consulta_cursos
# from ifAnalytics.views import consulta_campus
# from ifAnalytics.views import consulta_periodos

urlpatterns = [
	path('geral/', geral, name='geral'),
	path('notas/', notas, name='notas'),
	path('frequencias/', frequencias, name='frequencias'),
	path('suporte/', suporte, name='suporte'),
	path('consulta_cursos/', consulta_cursos, name='consulta_cursos'),
	path('consulta_campus/', consulta_campus, name='consulta_campus'),
	path('consulta_periodos/', consulta_periodos, name='consulta_periodos'),
	path('consulta_turmas/', consulta_turmas, name='consulta_turmas'),
]
    