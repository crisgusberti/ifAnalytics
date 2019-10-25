from django.shortcuts import render
from django.db import connection
from collections import namedtuple
from django.http import JsonResponse


#Renderiza as paginas HTML para acesso pelos links do menu da direita
def geral(request):
	return render(request, 'ifAnalytics/geral.html')

def notas(request):
	return render(request, 'ifAnalytics/notas.html')

def frequencias(request):
	return render(request, 'ifAnalytics/frequencias.html')

def suporte(request):
	return render(request, 'ifAnalytics/suporte.html')

# A função namedtuplefetchall é da documentação do Django e serve
# para consultas cruas SQL, mas retona elas em um array de tuplas (nome: valor)
def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

# As funções consulta_campus, consulta_cursos, consulta_periodos e consulta_turmas servem para 
# montagem dos combobox que filtram os dados dos gráficos
def consulta_campus(request):
    with connection.cursor() as cursor: # o metodo cursos() do Django serve para fazer consultas SQL cruas
        cursor.execute("SELECT id_unidade, nome FROM comum.unidade WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 605, 723) ORDER BY nome")
        rows = namedtuplefetchall(cursor); # retorma o resultado da consulta SQL em tuplas nomeadas
        context = {'campus': rows} # armazena em conxtext o resultado das consultas em um array "campus"
    return render(request, 'ifAnalytics/consulta_campus.html', context) # carrega no arquivo html o conteúdo de context

def consulta_cursos(request):
    campus_id = request.GET.get('campus_id') # aqui eu pego o campus_ID que vem da base.html na função Jquery/ajax que chama a URL "consulta_cursos" 
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_curso, nome FROM curso WHERE ativo IS TRUE AND id_unidade IN( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))", [campus_id]) # o campus_id pego na variavel acima serve de parametro para a consulta SQL e é substituído em "%s"
        rows = namedtuplefetchall(cursor);
        context = {'cursos': rows}
    return render(request, 'ifAnalytics/consulta_cursos.html', context)

def consulta_periodos(request):
    campus_id = request.GET.get('campus_id')
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT ano, periodo, (ano || '/' || periodo) AS periodo_formatado FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND cc.nivel = 'G' ORDER BY ano DESC, periodo DESC", [campus_id])
        rows = namedtuplefetchall(cursor);
        context = {'periodos': rows}
    return render(request, 'ifAnalytics/consulta_periodos.html', context)

def consulta_turmas(request):
    campus_id = request.GET.get('campus_id') #pegando as variáveis passads por ajax da base.html no jquery de consulta_turmas
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    with connection.cursor() as cursor:
        cursor.execute("SELECT ano, periodo, t.id_turma, t.codigo AS codigo_turma, cc.codigo AS codigo_disciplina, ccd.nome FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND cc.nivel = 'G' AND ano = %s AND periodo = %s", [campus_id, ano_turma, semestre_turma])
        rows = namedtuplefetchall(cursor);
        context = {'turmas': rows}
    return render(request, 'ifAnalytics/consulta_turmas.html', context)

#views que fazem as consultas e retornam os dados dos gráficos
# def get_data_forma_ingresso(request):
#     campus_id = request.GET.get('campus_id') 
#     ano_turma = request.GET.get('ano_turma')
#     semestre_turma = request.GET.get('semestre_turma')
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao")
#         rows = cursor.fetchall();
#     return JsonResponse(rows, safe=False)
################



def get_data_forma_ingresso(request):
    campus_id = request.GET.get('campus_id') 
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    
    # curso_id = 0
    # id_turma = 0

    # if id_turma is not None:
    #     cursor.execute("SELECT  mi.descricao, COUNT(distinct d.id_discente) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND mc.id_turma = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [id_turma]) 
    #     rows = cursor.fetchall();
    #     return JsonResponse(rows, safe=False) 
    # if ano_turma is not None:
    #     with connection.cursor() as cursor:
    #         cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND d.id_curso = 509023", [ano_turma, semestre_turma]) 
    #         rows = cursor.fetchall();
    #     return JsonResponse(rows, safe=False) 
    # if curso_id is not None:
    #     with connection.cursor() as cursor:
    #             cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.id_curso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [curso_id]) 
    #             rows = cursor.fetchall();
    #         return JsonResponse(rows, safe=False)
    if campus_id is not None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.id_gestora_academica IN ( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s) ) GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [campus_id]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)     










#######################################
def get_data_status_discente(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT sd.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status WHERE d.nivel IN ('G') GROUP BY sd.status ORDER BY sd.descricao")
        rows = cursor.fetchall();
    return JsonResponse(rows, safe=False)




