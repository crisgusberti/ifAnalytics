-- Consulta gráfico 3: Quantidade de Matriculados
--(TA MOSTRANDO QUANTIDADE EM NUMERO DE ALUNOS QUE ESTÃO MATRICULADOS EM x DISCIPLINAS)

--GRADUAÇÃO
-- filtrando por campus e ano
WITH q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo
	INNER JOIN curso c ON c.id_curso = cur.id_curso

	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27)
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)

	GROUP BY id_discente
	ORDER BY total_matricula_discente
)
SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
FROM q1
GROUP BY total_disciplinas_ano
ORDER BY total_disciplinas_ano



--filtrando por curso e ano
WITH q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo
	INNER JOIN curso c ON c.id_curso = cur.id_curso

	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 and t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27)
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)
		-- filtra por cursos do campus
		AND c.id_curso = {id_curso}

	GROUP BY id_discente
	ORDER BY total_matricula_discente
)
SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
FROM q1
GROUP BY total_disciplinas_ano
ORDER BY total_disciplinas_ano



-- Filtrando por turmas (versão original by Bryan)
		-- WITH q_disciplinas_curso AS (
		-- 		SELECT cu.id_disciplina, 'G' AS nivel 
		-- 		FROM graduacao.curriculo cur
		-- 		INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo
		-- 		INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina
		-- 		WHERE cur.id_curso = 379430

		-- 		UNION

		-- 		SELECT md.id_disciplina, 'T' AS nivel 
		-- 		FROM tecnico.modulo_curricular mc
		-- 		INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular
		-- 		INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo
		-- 		INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo
		-- 		WHERE ect.id_curso = 379430
		-- )
		-- , q1 AS (
		-- 	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc
		-- 	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
		-- 	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
			
		-- 	WHERE 
		-- 	    -- filtra por ano 
		-- 	    t.ano = 2019 AND t.periodo = 1
		-- 	    -- alunos matriculados
		-- 		AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27)
		-- 	    -- filtra o campus
		-- 	    AND cc.id_unidade  IN (
		--   			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		-- 		)
		-- 		-- filtra por cursos do campus
		-- 		--AND c.id_curso = {id_curso};
				
		-- 		-- filtrando por disciplinas
		-- 		AND t.id_disciplina IN (
		-- 			SELECT id_disciplina FROM q_disciplinas_curso
		-- 		)
		-- 	GROUP BY id_discente
		-- 	ORDER BY total_matricula_discente
		-- )
		-- SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
		-- FROM q1
		-- GROUP BY total_disciplinas_ano
		-- ORDER BY total_disciplinas_ano


--Filtrando pela turma (minha versão)
WITH q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
		AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	    -- filtra o campus
		   --AND cc.id_unidade  IN (
	  		--	 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)
			--)
		-- filtrando por disciplinas
		AND t.id_turma = 2900
	
	GROUP BY mc.id_discente
)
SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
FROM q1
GROUP BY total_disciplinas_ano




================================================================
--NOVA VERSÃO PARA TODAS AS CONSULTAS QUE MONTAM OS GRÁFICOS (FEITA POR MIM)
-- !!!!!!!!!!!!!!=====ESSA É A CONSULTA QUE ESTÁ IMPLEMENTADA NO SISTEMA========!!!!!!!!!!!!!!!!!!!!!!!
--a mesma consulta serve para campus/curso/turma

WITH q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente
	
	FROM ensino.matricula_componente mc
	
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
	WHERE 
	
		d.nivel IN ('G')
	
		AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
		
		AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)	
	
	-- filtra o campus
		AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56))
	
		-- filtra por ano 
	    AND t.ano = 2019 AND t.periodo = 1
	    
		--passando curso
		--AND d.id_curso =  197350
		
		-- filtrando por disciplinas
		--AND t.id_turma = 2900
	
	GROUP BY mc.id_discente
)
SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
	FROM q1
	GROUP BY total_disciplinas_ano
	ORDER BY total_disciplinas_ano


=========================================================
--CONSULTA PARA TABELA DE DETALHES (FEITA POR MIM)
--a mesma consulta serve para campus/curso/turma (é a mesma consulta acima, apenas trazendo mais dados)
WITH q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email, translate(('55' || CAST(p.codigo_area_nacional_telefone_celular AS varchar) || p.telefone_celular), '-', '') AS celular
	
	FROM ensino.matricula_componente mc
	
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	
	WHERE 
	
		d.nivel IN ('G')
	
		AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
		
		AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)	
	
	-- filtra o campus
		AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56))
	
		-- filtra por ano 
	    AND t.ano = 2019 AND t.periodo = 1
	    
		--passando curso
		--AND d.id_curso =  197350
		
		-- filtrando por disciplinas
		--AND t.id_turma = 2900
	
	GROUP BY mc.id_discente, d.matricula, discente, curso, p.email, celular
)
SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, email, celular
	FROM q1
	WHERE total_matricula_discente = 6 --por turma não precisa colocar esse parametro pq ele precisa listar todos os alunos daquela turma de qlqr jeito, já que só tem uma.
GROUP BY matricula, discente, curso, total_disciplinas_ano, email, celular
ORDER BY discente
