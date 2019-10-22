from django.shortcuts import render
from django.db import connection
from collections import namedtuple

def geral(request):
	return render(request, 'ifAnalytics/geral.html')

def notas(request):
	return render(request, 'ifAnalytics/notas.html')

def frequencias(request):
	return render(request, 'ifAnalytics/frequencias.html')

def suporte(request):
	return render(request, 'ifAnalytics/suporte.html')

def namedtuplefetchall(cursor):
    #"Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def consulta_campus(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_unidade, nome FROM comum.unidade WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 605, 723) ORDER BY nome")
        rows = namedtuplefetchall(cursor);
        context = {'campus': rows}
    return render(request, 'ifAnalytics/consulta_campus.html', context)

def consulta_cursos(request):
    campus_id = request.GET.get('campus_id')
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_curso, nome FROM curso WHERE ativo IS TRUE AND id_unidade IN( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))", [campus_id])
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
    campus_id = request.GET.get('campus_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    with connection.cursor() as cursor:
        cursor.execute("SELECT ano, periodo, t.id_turma, t.codigo AS codigo_turma, cc.codigo AS codigo_disciplina, ccd.nome FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND cc.nivel = 'G' AND ano = %s AND periodo = %s", [campus_id, ano_turma, semestre_turma])
        rows = namedtuplefetchall(cursor);
        context = {'turmas': rows}
    return render(request, 'ifAnalytics/consulta_turmas.html', context)





