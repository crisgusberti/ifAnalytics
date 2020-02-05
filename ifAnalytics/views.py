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
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    with connection.cursor() as cursor:
        cursor.execute("SELECT ano, periodo, t.id_turma, t.codigo AS codigo_turma, cc.codigo AS codigo_disciplina, ccd.nome FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe WHERE cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND cc.nivel = 'G' AND ano = %s AND periodo = %s", [campus_id, ano_turma, semestre_turma])
        rows = namedtuplefetchall(cursor);
        context = {'turmas': rows}
    return render(request, 'ifAnalytics/consulta_turmas.html', context)

#views que fazem as consultas e retornam os dados dos gráficos
def get_data_forma_ingresso(request):
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    turma_id = request.GET.get('turma_id')
    query_selector = request.GET.get('querySelector')

    if query_selector == "turma":
        with connection.cursor() as cursor:
            cursor.execute("SELECT  mi.descricao, COUNT(distinct d.id_discente) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND mc.id_turma = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [turma_id])
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "campus" or query_selector == "periodo":
        with connection.cursor() as cursor:
            cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.id_gestora_academica IN ( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s) ) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [campus_id, ano_turma, semestre_turma]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            cursor.execute("SELECT mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L') AND d.id_curso = %s AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [curso_id, ano_turma, semestre_turma]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_status_discente(request):
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
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
            parametros = [campus_id, ano_turma, semestre_turma]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if query_selector == "curso":
        with connection.cursor() as cursor:
            sql_string = "SELECT sd.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status WHERE d.id_curso = %s AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY sd.status ORDER BY sd.descricao"
            parametros = [curso_id, ano_turma, semestre_turma]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)

def get_data_total_matriculas(request):
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    turma_id = request.GET.get('turma_id') 

    if turma_id is not None:
        with connection.cursor() as cursor:
            cursor.execute("WITH q_disciplinas_curso AS (SELECT cu.id_disciplina, 'G' AS nivel FROM graduacao.curriculo cur INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina WHERE cur.id_curso = %s UNION SELECT md.id_disciplina, 'T' AS nivel FROM tecnico.modulo_curricular mc INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo WHERE ect.id_curso = {%s} ) WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE t.ano =%s AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27) AND cc.id_unidade  IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%S)) AND t.id_disciplina IN (SELECT id_disciplina FROM q_disciplinas_curso) GROUP BY id_discente ORDER BY total_matricula_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano", [curso_id, curso_id, ano_turma, campus_id])
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if ano_turma is not None and campus_id is not None:
        with connection.cursor() as cursor:
            cursor.execute("WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo INNER JOIN curso c ON c.id_curso = cur.id_curso WHERE t.ano = %s AND t.periodo = %s AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27) AND cc.id_unidade  IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY id_discente ORDER BY total_matricula_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano", [ano_turma, semestre_turma, campus_id]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    if curso_id is not None:
        with connection.cursor() as cursor:
            cursor.execute("WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo INNER JOIN curso c ON c.id_curso = cur.id_curso WHERE t.ano = %s AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27) AND cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND c.id_curso = %s GROUP BY id_discente ORDER BY total_matricula_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano", [ano_turma, campus_id, curso_id]) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    #if campus_id is not None:
        #as consultas de ano_turma e campus_id são iguais, pq eu preciso desses dois parametros pra executar a consulta
        #então não repliquei ela aqui. O gráfico só aparece qnd o combo do curso for selecionado.


    # não sei se qnd seleciona a turma algo muda nesse gráfico. Tem uma consulta ali, mas não sei se ela faz algo!





def get_data_discentes_evadidos(request): #esse é o grafico 7, lembrar de jogar ele pra baixo
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    turma_id = request.GET.get('turma_id') 

    #Não tem turma, pq ao selecionar o curso ele já traz a informação por turma!
    if ano_turma is not None:
        with connection.cursor() as cursor:
            sql_string="SELECT COUNT(DISTINCT mc.id_discente) AS matricula_turma, c.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  mc.id_situacao_matricula = 3 AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY c.nome"
            parametros=[ano_turma, semestre_turma, curso_id]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    # if ano_turma is not None and campus_id is not None:
    #     with connection.cursor() as cursor:
    #         cursor.execute("SELECT COUNT(DISTINCT mc.id_discente) AS matricula_turma, c.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  mc.id_situacao_matricula = 3 AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY c.nome", [ano_turma, semestre_turma, curso_id]) 
    #         rows = cursor.fetchall();
    #     return JsonResponse(rows, safe=False) 
    if curso_id is not None:
        with connection.cursor() as cursor:
            sql_string = "WITH q_disciplinas_curso AS (SELECT cu.id_disciplina, 'G' AS nivel FROM graduacao.curriculo cur INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina WHERE cur.id_curso = %s UNION SELECT md.id_disciplina, 'T' AS nivel FROM tecnico.modulo_curricular mc INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo WHERE ect.id_curso = %s) SELECT COUNT(mc.*) AS total_cancelamento_discente, cc.codigo FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE t.ano = %s AND t.periodo = %s AND mc.id_situacao_matricula = 3 AND t.id_disciplina IN (SELECT id_disciplina FROM q_disciplinas_curso) GROUP BY cc.codigo ORDER BY total_cancelamento_discente"
            parametros = [curso_id, curso_id, ano_turma, semestre_turma]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if campus_id is not None:
        with connection.cursor() as cursor:
            sql_string="SELECT COUNT(DISTINCT mc.id_discente) AS matricula_turma, c.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  mc.id_situacao_matricula = 3 AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY c.nome"
            parametros=[ano_turma, semestre_turma, curso_id]
            cursor.execute(sql_string, parametros)
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    # o ano deve ser sempre o ano atual
    #####
    # import datetime
    # now = datetime.datetime.now()
    # print now.year, now.month, now.day, now.hour, now.minute, now.second
    # 2015 5 6 8 53 40
    #####
    # campus_id e ano_turma devem ser a mesma consulta, pq preciso dos dois para realizar a consulta


    ###############################################
    #usar o and ou o or como foi feito na consulta do grafico assim para o caso de campus_id e ano_turma
       #if campus_id is not None:
        #as consultas de ano_turma e campus_id são iguais, pq eu preciso desses dois parametros pra executar a consulta
        #então não repliquei ela aqui. O gráfico só aparece qnd o combo do curso for selecionado.

#Página de notas
def get_data_notas_parciais(request):
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    turma_id = request.GET.get('turma_id')
    unidade = request.GET.get('unidade') 

    if turma_id is not None:
        with connection.cursor() as cursor:
            sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND mc.id_turma = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota) SELECT SUM (CASE WHEN q1.nota >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN q1.nota < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP by q1.unidade"
            parametros=[ano_turma, semestre_turma, turma_id, unidade]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if curso_id is not None:
        with connection.cursor() as cursor:
            sql_string = "WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.id_curso = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota) SELECT SUM (CASE WHEN q1.nota >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN q1.nota < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media  FROM q1 WHERE q1.unidade = %s GROUP by q1.unidade"
            parametros = [ano_turma, semestre_turma, curso_id, unidade]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    #Campus e ano tem a mesma consulta pq preciso dos dois pra efetuar a consulta em si
    if ano_turma is not None and campus_id is not None:
        with connection.cursor() as cursor:
            sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota) SELECT SUM (CASE WHEN q1.nota >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN q1.nota < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP by q1.unidade"
            parametros=[ano_turma, semestre_turma, campus_id, unidade]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 

def get_data_medias_finais(request):
    campus_id = request.GET.get('campus_id') 
    curso_id  = request.GET.get('curso_id')
    ano_turma = request.GET.get('ano_turma')
    semestre_turma = request.GET.get('semestre_turma')
    turma_id = request.GET.get('turma_id')

    if turma_id is not None:
        with connection.cursor() as cursor:
            sql_string="SELECT SUM (CASE WHEN mc.media_final >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.id_turma = %s"
            parametros=[ano_turma, semestre_turma, campus_id, turma_id] #não sei se o campus é necessario na consulta
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    if curso_id is not None:
        with connection.cursor() as cursor:
            sql_string = "SELECT SUM (CASE WHEN mc.media_final >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s"
            parametros = [ano_turma, semestre_turma, campus_id, curso_id] #não sei se o campus é necessario na consulta
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False)
    #Campus e ano tem a mesma consulta pq preciso dos dois pra efetuar a consulta em si
    if ano_turma is not None and campus_id is not None:
        with connection.cursor() as cursor:
            sql_string="SELECT SUM (CASE WHEN mc.media_final >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))"
            parametros=[ano_turma, semestre_turma, campus_id]
            cursor.execute(sql_string, parametros) 
            rows = cursor.fetchall();
        return JsonResponse(rows, safe=False) 
    