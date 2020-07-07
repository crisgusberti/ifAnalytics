from django.shortcuts import render, redirect
from django.db import connection
from collections import namedtuple
from django.http import JsonResponse


#Renderiza as paginas HTML para acesso pelos links do menu da direita
def geral(request):
	if not request.session.get('username'): #verifica autenticação
		return redirect('login') #se não está autenticado, redireciona para a página de login
	else:
		return render(request, 'ifAnalytics/geral.html') #só vai carregar a página se o usuário esta autenticado

def notas(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
		return render(request, 'ifAnalytics/notas.html')

def frequencias(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
		return render(request, 'ifAnalytics/frequencias.html')

def suporte(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
		return render(request, 'ifAnalytics/suporte.html')

def detalhes(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
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
	if not request.session.get('username'):
		return redirect('login')
	else:
		if request.session['campus'] == 'FULL_ACCESS': #request.session['campus'] vem da view de autenticação e define o campus de quem fez login. Se o campus for FULL_ACCESS a pessoa tem acesso a todos os campus.
			with connection.cursor() as cursor: # o metodo cursos() do Django serve para fazer consultas SQL cruas
				cursor.execute("SELECT id_unidade, nome FROM comum.unidade WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 723) ORDER BY CASE WHEN nome = 'INSTITUTO FEDERAL RIO GRANDE DO SUL' THEN 1 ELSE 2 END, nome")
				rows = namedtuplefetchall(cursor); # retorma o resultado da consulta SQL em tuplas nomeadas
				context = {'campus': rows} # armazena em conxtext o resultado das consultas em um array "campus"
			return render(request, 'ifAnalytics/consulta_campus.html', context) # carrega no arquivo html o conteúdo de context
		else:  #Se não for FULL_ACCESS o acesso é restrito a apenas o campus específico ao qual essa pessoa foi cadastrada no arquivo json
			id_unidade = request.session['campus']
			with connection.cursor() as cursor: 
				cursor.execute("SELECT id_unidade, nome FROM comum.unidade WHERE unidade_responsavel = %s AND id_unidade = %s ORDER BY nome", [id_unidade, id_unidade])
				rows = namedtuplefetchall(cursor); 
				context = {'campus': rows} 
			return render(request, 'ifAnalytics/consulta_campus.html', context) 

def consulta_cursos(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') # aqui eu pego o campus_ID que vem da base.html na função Jquery/ajax que chama a URL "consulta_cursos" 
		if campus_id == '605': #se for IFRS lista todos os cursos de todos os campi
				with connection.cursor() as cursor:
					cursor.execute("SELECT c.id_curso, c.id_unidade, right(u.sigla, 3) AS campus, c.nome FROM curso c INNER JOIN comum.unidade u ON c.id_unidade = u.id_unidade WHERE c.ativo IS TRUE AND c.nivel = 'G' ORDER BY u.sigla, c.nome") #Lista todos os cursos do IFRS
					rows = namedtuplefetchall(cursor);
					context = {'cursos': rows, "mostrar_campus": "True"} #envia um segundo parametro ("mostrar_campus": "True") p/ o template
				return render(request, 'ifAnalytics/consulta_cursos.html', context)
		else: #se não for IFRS faz as verificações de acordo com as permissões cadastradas no json.
			if request.session['curso'] == 'FULL_ACCESS': #request.session['curso'] vem da view de autenticação e define o curso de quem fez login (no caso de um coordenador). Se o curso for FULL_ACCESS a pessoa tem acesso a todos os cursos de um campus específico.
				with connection.cursor() as cursor:
					cursor.execute("SELECT id_curso, nome FROM curso WHERE ativo IS TRUE AND nivel = 'G' AND id_unidade IN( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))", [campus_id]) # o campus_id pego na variavel acima serve de parametro para a consulta SQL e é substituído em "%s"
					rows = namedtuplefetchall(cursor);
					context = {'cursos': rows}
				return render(request, 'ifAnalytics/consulta_cursos.html', context)
			else: #Se o curso não for FULL_ACCESS, o acesso é restrigo apenas ao curso ao qual a pessoa foi cadastrada no arquivo json.
				id_curso = request.session['curso']
				with connection.cursor() as cursor:
					cursor.execute("SELECT id_curso, nome FROM curso WHERE ativo IS TRUE AND nivel = 'G' AND id_unidade IN( SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND id_curso = %s", [campus_id, id_curso]) # o campus_id e o id_curso pego na variavel acima servem de parametros para a consulta SQL e é substituído em "%s"
					rows = namedtuplefetchall(cursor);
					context = {'cursos': rows}
				return render(request, 'ifAnalytics/consulta_cursos.html', context)

def consulta_periodos(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id')
		if campus_id == '605': #se for IFRS lista todos os períodos de todos os campi
			with connection.cursor() as cursor:
				cursor.execute("SELECT DISTINCT ano, periodo, (ano || '/' || periodo) AS periodo_formatado FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE cc.nivel = 'G' ORDER BY ano DESC, periodo DESC")
				rows = namedtuplefetchall(cursor);
				context = {'periodos': rows}
			return render(request, 'ifAnalytics/consulta_periodos.html', context)
		else: #Se não for IFRS lista apenas os períodos do campus especificado.
			with connection.cursor() as cursor:
				cursor.execute("SELECT DISTINCT ano, periodo, (ano || '/' || periodo) AS periodo_formatado FROM ensino.turma t INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina WHERE cc.id_unidade IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND cc.nivel = 'G' ORDER BY ano DESC, periodo DESC", [campus_id])
				rows = namedtuplefetchall(cursor);
				context = {'periodos': rows}
			return render(request, 'ifAnalytics/consulta_periodos.html', context)

def consulta_turmas(request):
	if not request.session.get('username'):
		return redirect('login')
	else:
		ano = request.GET.get('ano') #pegando as variáveis passads por ajax da base.html no jquery de consulta_turmas
		semestre = request.GET.get('semestre')
		curso_id  = request.GET.get('curso_id')
		with connection.cursor() as cursor:
			cursor.execute("SELECT t.ano, t.periodo, mc.id_turma, t.codigo AS codigo_turma, cc.codigo as codigo_disciplina, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina INNER JOIN ensino.componente_curricular_detalhes ccd on ccd.id_componente_detalhes = cc.id_detalhe INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo INNER JOIN curso c ON c.id_curso = cur.id_curso WHERE t.ano = %s and t.periodo = %s AND cc.nivel = 'G' AND c.id_curso = %s GROUP BY t.ano, t.periodo, mc.id_turma, codigo_turma, codigo_disciplina, ccd.nome", [ano, semestre, curso_id])
			rows = namedtuplefetchall(cursor);
			context = {'turmas': rows}
		return render(request, 'ifAnalytics/consulta_turmas.html', context)

#views que fazem as consultas e retornam os dados dos gráficos
def get_data_forma_ingresso(request): #Gráfico 1
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [ano, semestre]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND d.id_curso =  %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [ano, semestre, curso_id]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [turma_id])
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 

			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					cursor.execute("SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')'), mi.descricao AS forma_ingresso, p.email AS contato FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND mi.descricao = %s ORDER BY discente", [ano, semestre, parametro_detalhe]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					cursor.execute("SELECT d.matricula, p.nome AS discente, c.nome AS curso, mi.descricao AS forma_ingresso, p.email AS contato FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND d.id_curso =  %s AND mi.descricao = %s ORDER BY discente", [ano, semestre, curso_id, parametro_detalhe]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					cursor.execute("SELECT d.matricula, p.nome AS discente, c.nome AS curso, mi.descricao AS forma_ingresso, p.email AS contato FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND AND mc.id_turma = %s AND mi.descricao = %s ORDER BY discente", [turma_id, parametro_detalhe]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
		
		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [campus_id, ano, semestre]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND d.id_curso = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [campus_id, ano, semestre, curso_id]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					cursor.execute("SELECT  mi.descricao, COUNT(d.*) AS total_alunos FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY mi.id_modalidade_ingresso ORDER BY mi.descricao", [turma_id])
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					cursor.execute("SELECT d.matricula, p.nome AS discente, c.nome AS curso, mi.descricao AS forma_ingresso, p.email AS contato FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND mi.descricao = %s ORDER BY discente", [campus_id, ano, semestre, parametro_detalhe]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					cursor.execute("SELECT d.matricula, p.nome AS discente, c.nome AS curso, mi.descricao AS forma_ingresso, p.email AS contato FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.ano_ingresso = %s AND d.periodo_ingresso = %s AND d.id_curso =  %s AND mi.descricao = %s ORDER BY discente", [campus_id, ano, semestre, curso_id, parametro_detalhe]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					cursor.execute("SELECT d.matricula, p.nome AS discente, c.nome AS curso, mi.descricao AS forma_ingresso, p.email AS contato FROM discente d INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s AND mi.descricao = %s ORDER BY discente", [turma_id, parametro_detalhe]) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_status_discente(request): #Gráfico 2
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s GROUP BY sd.status ORDER BY sd.descricao"
					parametros = [ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND d.id_curso = %s GROUP BY sd.status ORDER BY sd.descricao"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND mc.id_turma = %s GROUP BY sd.status ORDER BY sd.descricao"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 

			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, sd.descricao AS status, p.email AS contato FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND sd.descricao = %s GROUP BY d.matricula, discente, curso, sd.descricao, contato ORDER BY discente"
					parametros = [ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND d.id_curso = %s AND sd.descricao = %s GROUP BY d.matricula, discente, curso, sd.descricao, contato ORDER BY discente"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND mc.id_turma = %s AND sd.descricao = %s GROUP BY d.matricula, discente, curso, sd.descricao, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY sd.status ORDER BY sd.descricao"
					parametros = [ ano, semestre, campus_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY sd.status ORDER BY sd.descricao"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND mc.id_turma = %s GROUP BY sd.status ORDER BY sd.descricao"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 

			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND sd.descricao = %s GROUP BY d.matricula, discente, curso, sd.descricao, contato ORDER BY discente"
					parametros = [ano, semestre, campus_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s AND sd.descricao = %s GROUP BY d.matricula, discente, curso, sd.descricao, contato ORDER BY discente"
					parametros = [ano, semestre, campus_id, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato FROM discente d INNER JOIN status_discente sd ON sd.status = d.status INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa WHERE d.nivel IN ('G') AND t.ano = %s and t.periodo = %s AND mc.id_turma = %s AND sd.descricao = %s GROUP BY d.matricula, discente, curso, sd.descricao, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_total_matriculas(request): #Gráfico 3
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s GROUP BY mc.id_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
					parametros = [ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY mc.id_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND t.id_turma = %s GROUP BY mc.id_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s GROUP BY mc.id_discente, d.matricula, discente, curso, contato) SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato FROM q1 WHERE total_matricula_discente = %s GROUP BY matricula, discente, curso, total_disciplinas_ano, contato ORDER BY discente"
					parametros = [ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY mc.id_discente, d.matricula, discente, curso, contato) SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato FROM q1 WHERE total_matricula_discente = %s GROUP BY matricula, discente, curso, total_disciplinas_ano, contato ORDER BY discente"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND t.id_turma = %s GROUP BY mc.id_discente, d.matricula, discente, curso, contato) SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato FROM q1 GROUP BY matricula, discente, curso, total_disciplinas_ano, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND t.ano = %s AND t.periodo = %s GROUP BY mc.id_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
					parametros = [campus_id, ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY mc.id_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
					parametros = [campus_id, ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND t.id_turma = %s GROUP BY mc.id_discente) SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos FROM q1 GROUP BY total_disciplinas_ano ORDER BY total_disciplinas_ano"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND t.ano = %s AND t.periodo = %s GROUP BY mc.id_discente, d.matricula, discente, curso, contato) SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato FROM q1 WHERE total_matricula_discente = %s GROUP BY matricula, discente, curso, total_disciplinas_ano, contato ORDER BY discente"
					parametros = [campus_id, ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY mc.id_discente, d.matricula, discente, curso, contato) SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato FROM q1 WHERE total_matricula_discente = %s GROUP BY matricula, discente, curso, total_disciplinas_ano, contato ORDER BY discente"
					parametros = [campus_id, ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS (SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel IN ('G') AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND t.id_turma = %s GROUP BY mc.id_discente, d.matricula, discente, curso, contato) SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato FROM q1 GROUP BY matricula, discente, curso, total_disciplinas_ano, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_concluintes(request): #Gráfico 4
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		anoSemestre = request.GET.get('ano')+request.GET.get('semestre') #foi concatenado pq no banco o prazo de conclusão é assim
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')
		coluna_selecionada = request.GET.get('colunaSelecionada')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT d.id_discente, d.prazo_conclusao, d.status FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) GROUP BY d.id_discente) SELECT SUM (CASE WHEN prazo_conclusao < %s THEN 1 ELSE 0 END) AS alunos_jubilados, SUM (CASE WHEN prazo_conclusao = %s AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, SUM (CASE WHEN status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') THEN 1 ELSE 0 END) AS alunos_formandos FROM q1"
					parametros = [anoSemestre, anoSemestre, anoSemestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT d.id_discente, d.prazo_conclusao, d.status FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_curso = %s GROUP BY d.id_discente) SELECT SUM (CASE WHEN prazo_conclusao < %s THEN 1 ELSE 0 END) AS alunos_jubilados, SUM (CASE WHEN prazo_conclusao = %s AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, SUM (CASE WHEN status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') THEN 1 ELSE 0 END) AS alunos_formandos FROM q1"
					parametros = [curso_id, anoSemestre, anoSemestre, anoSemestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT d.id_discente, d.prazo_conclusao, d.status FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY d.id_discente) SELECT SUM (CASE WHEN prazo_conclusao < %s THEN 1 ELSE 0 END) AS alunos_jubilados, SUM (CASE WHEN prazo_conclusao = %s AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, SUM (CASE WHEN status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') THEN 1 ELSE 0 END) AS alunos_formandos FROM q1"
					parametros = [turma_id, anoSemestre, anoSemestre, anoSemestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			
			#Consultas para montar a tabela da página de detalhes
			if coluna_selecionada == "Alunos Formandos": #detalhes para coluna de CONCLUINTES
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "curso_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') AND d.id_curso = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, curso_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "turma_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') AND mc.id_turma = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, turma_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False) 
			elif coluna_selecionada == "Alunos em Vias de Jubilar": #detalhes para a coluna de EM VIAS DE JUBILAR
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND  d.prazo_conclusao = %s AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato ORDER BY discente"
						parametros = [anoSemestre]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "curso_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao = %s AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_curso = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato ORDER BY discente"
						parametros = [anoSemestre, curso_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "turma_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao = %s AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato ORDER BY discente"
						parametros = [anoSemestre, turma_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False) 
			elif coluna_selecionada == "Alunos Jubilados": #detalhes para a coluna de NÃO CONCLUINTES
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND  d.prazo_conclusao < %s AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "curso_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao < %s AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_curso = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, curso_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "turma_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao < %s AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, turma_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False) 

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT d.id_discente, d.prazo_conclusao, d.status FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) group by d.id_discente) SELECT SUM (CASE WHEN prazo_conclusao < %s THEN 1 ELSE 0 END) AS alunos_jubilados, SUM (CASE WHEN prazo_conclusao = %s AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, SUM (CASE WHEN status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') THEN 1 ELSE 0 END) AS alunos_formandos FROM q1"
					parametros = [campus_id, anoSemestre, anoSemestre, anoSemestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT d.id_discente, d.prazo_conclusao, d.status FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s group by d.id_discente) SELECT SUM (CASE WHEN prazo_conclusao < %s THEN 1 ELSE 0 END) AS alunos_jubilados, SUM (CASE WHEN prazo_conclusao = %s AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, SUM (CASE WHEN status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') THEN 1 ELSE 0 END) AS alunos_formandos FROM q1"
					parametros = [campus_id, curso_id, anoSemestre, anoSemestre, anoSemestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT d.id_discente, d.prazo_conclusao, d.status FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s group by d.id_discente) SELECT SUM (CASE WHEN prazo_conclusao < %s THEN 1 ELSE 0 END) AS alunos_jubilados, SUM (CASE WHEN prazo_conclusao = %s AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, SUM (CASE WHEN status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') THEN 1 ELSE 0 END) AS alunos_formandos FROM q1"
					parametros = [turma_id, anoSemestre, anoSemestre, anoSemestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			
			#Consultas para montar a tabela da página de detalhes
			if coluna_selecionada == "Alunos Formandos": #detalhes para coluna de CONCLUINTES
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, campus_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "curso_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, campus_id, curso_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "turma_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status = 8 AND %s = (SELECT cast(cast(ano as varchar) || cast(periodo as varchar) as integer) as ano_periodo FROM comum.calendario_academico WHERE nivel = 'G' AND id_unidade = 605 AND vigente = 'true') AND mc.id_turma = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, turma_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False) 
			elif coluna_selecionada == "Alunos em Vias de Jubilar": #detalhes para a coluna de EM VIAS DE JUBILAR
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao = %s AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato ORDER BY discente"
						parametros = [anoSemestre, campus_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "curso_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao = %s AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato ORDER BY discente"
						parametros = [anoSemestre, campus_id, curso_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "turma_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao = %s AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato ORDER BY discente"
						parametros = [anoSemestre, turma_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False) 
			elif coluna_selecionada == "Alunos Jubilados": #detalhes para a coluna de NÃO CONCLUINTES
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao < %s AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, campus_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "curso_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao < %s AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, campus_id, curso_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False)
				if query_selector == "turma_detalhes":
					with connection.cursor() as cursor:
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND  d.prazo_conclusao < %s AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s GROUP BY matricula, discente, curso, d.prazo_conclusao, contato ORDER BY discente"
						parametros = [anoSemestre, turma_id]
						cursor.execute(sql_string, parametros)
						rows = cursor.fetchall();
					return JsonResponse(rows, safe=False) 

def get_data_tamanho_turmas(request): #Gráfico 5
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS( SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma ORDER BY total_matriculados"
					parametros = [ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma ORDER BY total_matriculados"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma ORDER BY total_matriculados"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)  
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma ORDER BY total_matriculados"
					parametros = [campus_id, ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma ORDER BY total_matriculados"
					parametros = [campus_id, ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_matriculados FROM q1 GROUP BY disciplina, id_turma ORDER BY total_matriculados"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)  
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [campus_id, ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [campus_id, ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_discentes_evadidos(request): #Gráfico 6
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_evadidos FROM q1 GROUP BY disciplina, id_turma ORDER BY total_evadidos"
					parametros=[ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso =  %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_evadidos FROM q1 GROUP BY disciplina, id_turma ORDER BY total_evadidos"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_evadidos FROM q1 GROUP BY disciplina, id_turma ORDER BY total_evadidos"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso =  %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_evadidos FROM q1 GROUP BY disciplina, id_turma ORDER BY total_evadidos"
					parametros=[campus_id, ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_evadidos FROM q1 GROUP BY disciplina, id_turma ORDER BY total_evadidos"
					parametros = [campus_id, ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string = "WITH q1 AS(SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome) SELECT nome AS disciplina, COUNT(id_discente) AS total_evadidos FROM q1 GROUP BY disciplina, id_turma ORDER BY total_evadidos"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [campus_id, ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [campus_id, ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND mc.id_situacao_matricula IN (3) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s AND ccd.nome = %s GROUP BY d.matricula, discente, curso, disciplina, contato ORDER BY discente"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)


#Página de notas
def get_data_notas_parciais(request): #Gráfico 7
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		unidade = request.GET.get('unidade')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP BY q1.unidade"
					parametros=[ano, semestre, unidade]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP BY q1.unidade"
					parametros = [ano, semestre, curso_id, unidade]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP BY q1.unidade"
					parametros=[ano, semestre, turma_id, unidade]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é "nu.nota_final_unidade <7" (abaixo da média) ou "nu.nota_final_unidade >=7" (acima da média)
					if parametro_detalhe == "ABAIXO DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND nu.unidade = %s AND nu.nota_final_unidade < 7 ORDER BY discente, nu.nota_final_unidade"
					elif parametro_detalhe == "ACIMA DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND nu.unidade = %s AND nu.nota_final_unidade >= 7 ORDER BY discente, nu.nota_final_unidade"
					parametros = [ano, semestre, unidade]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s AND nu.unidade = %s AND nu.nota_final_unidade < 7 ORDER BY discente, nu.nota_final_unidade"
					elif parametro_detalhe == "ACIMA DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s AND nu.unidade = %s AND nu.nota_final_unidade >= 7 ORDER BY discente, nu.nota_final_unidade"
					parametros = [ano, semestre, curso_id, unidade]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s AND nu.unidade = %s AND nu.nota_final_unidade < 7 ORDER BY discente, nu.nota_final_unidade"
					elif parametro_detalhe == "ACIMA DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s AND nu.unidade = %s AND nu.nota_final_unidade >= 7 ORDER BY discente, nu.nota_final_unidade"
					parametros = [ano, semestre, turma_id, unidade]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP BY q1.unidade"
					parametros=[ano, semestre, campus_id, unidade]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP BY q1.unidade"
					parametros = [ano, semestre, curso_id, unidade]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade) SELECT SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM q1 WHERE q1.unidade = %s GROUP BY q1.unidade"
					parametros=[ano, semestre, turma_id, unidade]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é "nu.nota_final_unidade <7" (abaixo da média) ou "nu.nota_final_unidade >=7" (acima da média)
					if parametro_detalhe == "ABAIXO DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND nu.unidade = %s AND nu.nota_final_unidade <7 ORDER BY discente, nu.nota_final_unidade"
					elif parametro_detalhe == "ACIMA DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND nu.unidade = %s AND nu.nota_final_unidade >=7 ORDER BY discente, nu.nota_final_unidade"
					parametros = [ano, semestre, campus_id, unidade]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s AND nu.unidade = %s AND nu.nota_final_unidade <7 ORDER BY discente, nu.nota_final_unidade"
					elif parametro_detalhe == "ACIMA DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s AND nu.unidade = %s AND nu.nota_final_unidade >=7 ORDER BY discente, nu.nota_final_unidade"
					parametros = [ano, semestre, curso_id, unidade]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s AND nu.unidade = %s AND nu.nota_final_unidade <7 ORDER BY discente, nu.nota_final_unidade"
					elif parametro_detalhe == "ACIMA DE 7":
						sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE t.ano = %s AND t.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s AND nu.unidade = %s AND nu.nota_final_unidade >=7 ORDER BY discente, nu.nota_final_unidade"
					parametros = [ano, semestre, turma_id, unidade]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_medias_finais(request): #Gráfico 8
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s"
					parametros=[ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é "nu.media_final <5" (abaixo da média) ou "nu.media_final >=5" (acima da média)
					if parametro_detalhe == "ABAIXO DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.media_final < 5 ORDER BY discente, mc.media_final"
					elif parametro_detalhe == "ACIMA DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.media_final >= 5 ORDER BY discente, mc.media_final"
					parametros = [ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s AND mc.media_final < 5 ORDER BY discente, mc.media_final"
					elif parametro_detalhe == "ACIMA DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s AND mc.media_final >= 5 ORDER BY discente, mc.media_final"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s AND mc.media_final < 5 ORDER BY discente, mc.media_final"
					elif parametro_detalhe == "ACIMA DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s AND mc.media_final >= 5 ORDER BY discente, mc.media_final"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))"
					parametros=[ano, semestre, campus_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é "nu.media_final <5" (abaixo da média) ou "nu.media_final >=5" (acima da média)
					if parametro_detalhe == "ABAIXO DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.media_final < 5 ORDER BY discente, mc.media_final"
					elif parametro_detalhe == "ACIMA DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.media_final >= 5 ORDER BY discente, mc.media_final"
					parametros = [ano, semestre, campus_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s AND mc.media_final < 5 ORDER BY discente, mc.media_final"
					elif parametro_detalhe == "ACIMA DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s AND mc.media_final >= 5 ORDER BY discente, mc.media_final"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "ABAIXO DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s AND mc.media_final < 5 ORDER BY discente, mc.media_final"
					elif parametro_detalhe == "ACIMA DE 5":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s AND mc.media_final >= 5 ORDER BY discente, mc.media_final"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
 
def get_data_discentes_exame(request): #Gráfico 9
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s GROUP BY d.matricula, discente, curso, disciplina, contato), Q2 AS(SELECT matricula, discente, curso, disciplina, media_parcial, contato FROM Q1 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato) SELECT SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM Q2"
					parametros=[ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY d.matricula, discente, curso, disciplina, contato), Q2 AS(SELECT matricula, discente, curso, disciplina, media_parcial, contato FROM Q1 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato) SELECT SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM Q2"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s GROUP BY d.matricula, discente, curso, disciplina, contato), Q2 AS(SELECT matricula, discente, curso, disciplina, media_parcial, contato FROM Q1 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato) SELECT SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM Q2"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)  
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é "media_parcial <7" (em exame) ou "media_parcial >=7" (sem exame)
					if parametro_detalhe == "DISCENTES EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial < 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					elif parametro_detalhe == "DISCENTES QUE NÃO ESTÃO EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial >= 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					parametros = [ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial < 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					elif parametro_detalhe == "DISCENTES QUE NÃO ESTÃO EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_curso = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial >= 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial < 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					elif parametro_detalhe == "DISCENTES QUE NÃO ESTÃO EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial >= 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY d.matricula, discente, curso, disciplina, contato), Q2 AS(SELECT matricula, discente, curso, disciplina, media_parcial, contato FROM Q1 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato) SELECT SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM Q2"
					parametros=[ano, semestre, campus_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False) 
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY d.matricula, discente, curso, disciplina, contato), Q2 AS(SELECT matricula, discente, curso, disciplina, media_parcial, contato FROM Q1 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato) SELECT SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM Q2"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s GROUP BY d.matricula, discente, curso, disciplina, contato), Q2 AS(SELECT matricula, discente, curso, disciplina, media_parcial, contato FROM Q1 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato) SELECT SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media FROM Q2"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)  
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é "media_parcial <7" (em exame) ou "media_parcial >=7" (sem exame)
					if parametro_detalhe == "DISCENTES EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial < 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					elif parametro_detalhe == "DISCENTES QUE NÃO ESTÃO EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial >= 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					parametros = [ano, semestre, campus_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial < 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					elif parametro_detalhe == "DISCENTES QUE NÃO ESTÃO EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial >= 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial <7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					elif parametro_detalhe == "DISCENTES QUE NÃO ESTÃO EM EXAME":
						sql_string="WITH Q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes WHERE nu.nota_final_unidade IS NOT NULL AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND t.ano = %s AND t.periodo = %s AND mc.id_turma = %s GROUP BY d.matricula, discente, curso, disciplina, contato) SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato FROM q1 WHERE q1.media_parcial >= 7 GROUP BY matricula, discente, curso, disciplina, media_parcial, contato ORDER BY discente, media_parcial"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_aprovados_reprovados(request): #Gráfico 10
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)"
					parametros=[ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "SELECT SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é mc.id_situacao_matricula para aprovado e reprovado
					if parametro_detalhe == "DISCENTES REPROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					elif parametro_detalhe == "DISCENTES APROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_situacao_matricula IN (4, 21, 22, 24) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES REPROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_curso =  %s AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					elif parametro_detalhe == "DISCENTES APROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_curso =  %s AND mc.id_situacao_matricula IN (4, 21, 22, 24) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES REPROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					elif parametro_detalhe == "DISCENTES APROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s AND mc.id_situacao_matricula IN (4, 21, 22, 24) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados		
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))"
					parametros=[ano, semestre, campus_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "SELECT SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					#O if abaixo define qual consulta vai ser executada. A unica diferença entre elas é mc.id_situacao_matricula para aprovado e reprovado
					if parametro_detalhe == "DISCENTES REPROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					elif parametro_detalhe == "DISCENTES APROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND mc.id_situacao_matricula IN (4, 21, 22, 24) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, campus_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES REPROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					elif parametro_detalhe == "DISCENTES APROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s AND mc.id_situacao_matricula IN (4, 21, 22, 24) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					if parametro_detalhe == "DISCENTES REPROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					elif parametro_detalhe == "DISCENTES APROVADOS":
						sql_string="SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE  d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s AND mc.id_situacao_matricula IN (4, 21, 22, 24) GROUP BY matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, turma_id]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

def get_data_status_disciplina(request): #Gráfico 11
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)) SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos FROM q1 GROUP BY q1.status_disciplina ORDER BY q1.status_disciplina"
					parametros=[ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH Q1 AS (SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_curso = %s) SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos FROM q1 GROUP BY q1.status_disciplina ORDER BY q1.status_disciplina"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s) SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos FROM q1 GROUP BY q1.status_disciplina ORDER BY q1.status_disciplina"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.ano = %s AND mc.periodo = %s AND sm.descricao = %s GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso = %s AND sm.descricao = %s GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s AND sm.descricao = %s GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))) SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos FROM q1 GROUP BY q1.status_disciplina ORDER BY q1.status_disciplina"
					parametros=[ano, semestre, campus_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "WITH Q1 AS (SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s) SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos FROM q1 GROUP BY q1.status_disciplina ORDER BY q1.status_disciplina"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="WITH Q1 AS (SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_turma = %s) SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos FROM q1 GROUP BY q1.status_disciplina ORDER BY q1.status_disciplina"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.ano = %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND sm.descricao = %s GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, campus_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.ano = %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s AND sm.descricao = %s GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, campus_id, curso_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma_detalhes":
				with connection.cursor() as cursor:
					sql_string = "SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s AND sm.descricao = %s GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato ORDER BY discente, situacao"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
					cursor.execute(sql_string, parametros)
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)	

#Página de Frequências
def get_data_percentuais_frequencia(request): #Gráfico 12
	if not request.session.get('username'):
		return redirect('login')
	else:
		campus_id = request.GET.get('campus_id') 
		curso_id  = request.GET.get('curso_id')
		ano = request.GET.get('ano')
		semestre = request.GET.get('semestre')
		turma_id = request.GET.get('turma_id')
		query_selector = request.GET.get('querySelector')
		parametro_detalhe = request.GET.get('parametroDetalhes')

		if campus_id == '605': #lista de todo o IFRS
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100, SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95, SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90, SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85, SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80, SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75, SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)"
					parametros=[ano, semestre]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "SELECT SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100, SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95, SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90, SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85, SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80, SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75, SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_curso = %s"
					parametros = [ano, semestre, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100, SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95, SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90, SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85, SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80, SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75, SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano = %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			#as consultas para 100%, menos de 75% e frequencia null são diferentes da consulta para os demais percentuais, por isso a lógica abaixo
			sql_string = "" #precisco criar as variaveis sql_string e parametros aqui, fora dos blocos if/else para que o escopo delas seja acessível lá embaixo onde executo a consulta
			parametros = []
			
			if parametro_detalhe == "100":
				#consulta para cem por cento
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia = %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, parametro_detalhe]
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia = %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia = %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
			elif parametro_detalhe == "75":
				#consulta para 75 por cento
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, parametro_detalhe]            
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, curso_id, parametro_detalhe]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
			elif parametro_detalhe == "null":
				#consulta pra sem frequencia
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia IS NULL ORDER BY discente, frequencia"
					parametros = [ano, semestre]  
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia IS NULL ORDER BY discente, frequencia"
					parametros = [ano, semestre, curso_id]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia IS NULL ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id]
			else:
				#consulta para os demais percentuais de frequencia
				frequencia_minima_maxima = parametro_detalhe.split(",")
				frequencia_minima = frequencia_minima_maxima[0]
				frequencia_maxima = frequencia_minima_maxima[1]

				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s AND frequencia >= %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, frequencia_maxima, frequencia_minima]
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s AND frequencia >= %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, curso_id, frequencia_maxima, frequencia_minima]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano = %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s AND frequencia >= %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id, frequencia_maxima, frequencia_minima]
			
			#executa a consulta e os parametros definidos acima
			with connection.cursor() as cursor:
				cursor.execute(sql_string, parametros)
				rows = cursor.fetchall();
			return JsonResponse(rows, safe=False)

		else: #lista apenas dos parametros especificados
			if query_selector == "campus" or query_selector == "periodo":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100, SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95, SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90, SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85, SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80, SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75, SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))"
					parametros=[ano, semestre, campus_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "curso":
				with connection.cursor() as cursor:
					sql_string = "SELECT SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100, SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95, SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90, SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85, SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80, SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75, SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso = %s"
					parametros = [ano, semestre, campus_id, curso_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			if query_selector == "turma":
				with connection.cursor() as cursor:
					sql_string="SELECT SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100, SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95, SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90, SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85, SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80, SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75, SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente WHERE mc.ano= %s AND mc.periodo = %s AND d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.id_turma = %s"
					parametros=[ano, semestre, turma_id]
					cursor.execute(sql_string, parametros) 
					rows = cursor.fetchall();
				return JsonResponse(rows, safe=False)
			
			#Consultas para montar a tabela da página de detalhes
			#as consultas para 100%, menos de 75% e frequencia null são diferentes da consulta para os demais percentuais, por isso a lógica abaixo
			sql_string = "" #precisco criar as variaveis sql_string e parametros aqui, fora dos blocos if/else para que o escopo delas seja acessível lá embaixo onde executo a consulta
			parametros = []
			
			if parametro_detalhe == "100":
				#consulta para cem por cento
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia = %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, parametro_detalhe]
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia = %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, curso_id, parametro_detalhe]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia = %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
			elif parametro_detalhe == "75":
				#consulta para 75 por cento
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, parametro_detalhe]            
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, curso_id, parametro_detalhe]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id, parametro_detalhe]
			elif parametro_detalhe == "null":
				#consulta pra sem frequencia
				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia IS NULL ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id]  
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia IS NULL ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, curso_id]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia IS NULL ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id]
			else:
				#consulta para os demais percentuais de frequencia
				frequencia_minima_maxima = parametro_detalhe.split(",")
				frequencia_minima = frequencia_minima_maxima[0]
				frequencia_maxima = frequencia_minima_maxima[1]

				if query_selector == "campus_detalhes" or query_selector == "periodo_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s))) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s AND frequencia >= %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, frequencia_maxima, frequencia_minima]
				elif query_selector == "curso_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(%s)) AND d.id_curso =  %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s AND frequencia >= %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, campus_id, curso_id, frequencia_maxima, frequencia_minima]
				elif query_selector == "turma_detalhes":
					sql_string = "WITH q1 AS(SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato FROM ensino.matricula_componente mc INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma INNER JOIN discente d ON d.id_discente = mc.id_discente INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa INNER JOIN curso c ON c.id_curso = d.id_curso WHERE d.nivel = 'G' AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) AND mc.ano= %s AND mc.periodo = %s AND mc.id_turma = %s) SELECT matricula, discente, curso, disciplina, frequencia, contato FROM q1 WHERE frequencia < %s AND frequencia >= %s ORDER BY discente, frequencia"
					parametros = [ano, semestre, turma_id, frequencia_maxima, frequencia_minima]
			
			#executa a consulta e os parametros definidos acima
			with connection.cursor() as cursor:
				cursor.execute(sql_string, parametros)
				rows = cursor.fetchall();
			return JsonResponse(rows, safe=False)
