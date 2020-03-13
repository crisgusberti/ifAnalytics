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

def detalhes(request):
    return render(request, 'ifAnalytics/detalhes.html')

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
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    with connection.cursor() as cursor:
        cursor.execute("SELECT ano, periodo, t.id_turma, t.codigo AS codigo_turma, cc.codigo AS codigo_disciplina, ccd.nome FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND cc.nivel = 'G' AND ano = %s AND periodo = %s", [campus_id, ano, semestre])
        rows = namedtuplefetchall(cursor);
        context = {'turmas': rows}
    return render(request, 'ifAnalytics/consulta_turmas.html', context)

#views que fazem as consultas e retornam os dados dos gráficos
def get_data_forma_ingresso(request): #Gráfico 1
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            cursor.execute("SELECT  mi.descricao, COUNT(distinct d.id_discente) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND mc.id_turma = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [turma_id])
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.id_gestora_academica IN ( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s) ) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [campus_id, ano, semestre]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.id_curso = %s AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [curso_id, ano, semestre]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_status_discente(request): #Gráfico 2
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            sql_string = "SELECT sd.descricao, COUNT(distinct d.id_discente) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status  INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND mc.id_turma = %s GROUP BY sd.status ORDER BY sd.descricao"
            parametros = [turma_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string = "SELECT sd.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status WHERE d.nivel IN ('G') AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY sd.status ORDER BY sd.descricao"
            parametros = [campus_id, ano, semestre]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "SELECT sd.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status WHERE d.id_curso = %s AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY sd.status ORDER BY sd.descricao"
            parametros = [curso_id, ano, semestre]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_total_matriculas(request): #Gráfico 3
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            sql_string = "WITH q_disciplinas_curso AS (SELECT cu.id_disciplina, 'G' AS nivel FROM graduacao.curriculo cur INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina WHERE cur.id_curso = %s UNION SELECT md.id_disciplina, 'T' AS nivel FROM tecnico.modulo_curricular mc INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo WHERE ect.id_curso = %s), q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE t.ano = %s AND t.periodo = %s AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27) AND cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND t.id_disciplina IN (SELECT id_disciplina FROM q_disciplinas_curso) GROUP BY id_discente ORDER BY total_matricula_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
            parametros = [curso_id, curso_id, ano, semestre, campus_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo INNER JOIN curso c ON c.id_curso = cur.id_curso WHERE t.ano = %s AND t.periodo = %s AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27) AND cc.id_unidade  IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY id_discente ORDER BY total_matricula_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
            parametros = [ano, semestre, campus_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo INNER JOIN curso c ON c.id_curso = cur.id_curso WHERE t.ano = %s AND t.periodo = %s AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27) AND cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND c.id_curso = %s GROUP BY id_discente ORDER BY total_matricula_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
            parametros = [ano, semestre, campus_id, curso_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_concluintes(request): #Gráfico 4 e 5
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    anoSemestre = request.GET.get('ano')+request.GET.get('semestre') #foi concatenado pq no banco o prazo de conclusão é assim
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            sql_string = "SELECT SUM (CASE WHEN d.prazo_conclusao < %s AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.prazo_conclusao < %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s"
            parametros = [anoSemestre, anoSemestre, turma_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string = "SELECT SUM (CASE WHEN d.prazo_conclusao < %s AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano FROM discente d WHERE d.prazo_conclusao < %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN ( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))"
            parametros = [anoSemestre, anoSemestre, campus_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "SELECT SUM (CASE WHEN d.prazo_conclusao < %s AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano FROM discente d WHERE d.prazo_conclusao < %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN ( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s "
            parametros = [anoSemestre, anoSemestre, campus_id, curso_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_tamanho_turmas(request): #Gráfico 6
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma,  mc.id_situacao_matricula, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina  INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, mc.id_situacao_matricula, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma"
            parametros = [ano, semestre, turma_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma,    mc.id_situacao_matricula, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, mc.id_situacao_matricula, ccd.nome ) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma"
            parametros = [ano, semestre, campus_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "WITH q1 AS( SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma,   mc.id_situacao_matricula, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, mc.id_situacao_matricula, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma"
            parametros = [ano, semestre, campus_id, curso_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_discentes_evadidos(request): #Gráfico 7
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    #Não tem turma, pq ao selecionar o curso ele já traz a informação por turma!
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string="SELECT c.nome AS curso, COUNT(DISTINCT mc.id_discente) AS discentes_evadidos FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN curso c ON c.id_curso = d.id_curso WHERE mc.id_situacao_matricula = 3 AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY c.nome"
            parametros=[ano, semestre, campus_id]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "WITH q_disciplinas_curso AS (SELECT cu.id_disciplina, 'G' AS nivel FROM graduacao.curriculo cur INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina WHERE cur.id_curso = %s UNION SELECT md.id_disciplina, 'T' AS nivel FROM tecnico.modulo_curricular mc INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo WHERE ect.id_curso = %s) SELECT cc.codigo, COUNT(mc.*) AS total_cancelamento_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE t.ano = %s AND t.periodo = %s AND mc.id_situacao_matricula = 3 AND t.id_disciplina IN (SELECT id_disciplina FROM q_disciplinas_curso) GROUP BY cc.codigo ORDER BY total_cancelamento_discente"
            parametros = [curso_id, curso_id, ano, semestre]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

#Página de notas
def get_data_notas_parciais(request): #Gráfico 8
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    unidade = request.GET.get('unidade')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND mc.id_turma = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP by q1.unidade"
            parametros=[ano, semestre, turma_id, unidade]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.id_curso = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media  FROM q1 WHERE q1.unidade = %s GROUP by q1.unidade"
            parametros = [ano, semestre, curso_id, unidade]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP by q1.unidade"
            parametros=[ano, semestre, campus_id, unidade]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 

def get_data_medias_finais(request): #Gráfico 9
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano = request.GET.get('ano')
    semestre = request.GET.get('semestre')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE t.ano = %s AND t.periodo = %s AND mc.id_turma = %s"
            parametros=[ano, semestre, turma_id]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE t.ano = %s AND t.periodo = %s AND d.id_curso = %s"
            parametros = [ano, semestre, curso_id]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))"
            parametros=[ano, semestre, campus_id]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    