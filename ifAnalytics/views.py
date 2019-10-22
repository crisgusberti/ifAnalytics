from django.shortcuts import render
from django.db import connection

def geral(request):
	return render(request, 'ifAnalytics/geral.html')

def notas(request):
	return render(request, 'ifAnalytics/notas.html')

def frequencias(request):
	return render(request, 'ifAnalytics/frequencias.html')

def suporte(request):
	return render(request, 'ifAnalytics/suporte.html')

# def campus_choices_ajax (request):
# 	campus = request.GET.get('campus')
#     cursos = City.objects.filter(campus=campus)  #fazer a consulta dos cursos daquele campus
#
#	  cursos = consulta_cursos(campus) #mais ou menos assim?
#
#     context = {'cursos': cursos}
#     return render(request, 'includes/_cities_choices.html', context) #inclui oque está no context dentro dos campus do select de curso


# Mais ou menos assim lá no select do curso no HTML:
# # {% for city in cities %}
#   <option value="{{ city.pk }}">{{ city.name }}</option>
# {% endfor %}


def consulta_cursos(self):
    with connection.cursor() as cursor:
        cursor.execute("SELECT curso_nome FROM cursos WHERE campus = %s", [self.campus])
        rows = cursor.fetchall()
    return rows

# esse link é referencia importante: https://docs.djangoproject.com/pt-br/2.2/topics/db/sql/#executing-custom-sql-directly