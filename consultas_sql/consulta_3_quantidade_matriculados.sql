-- Consulta gráfico 3: Quantidade de Matriculados
--(TA MOSTRANDO QUANTIDADE NUMERO E ALUNOS QUE ESTÃO MATRICULADOS EM x DISCIPLINAS)

--GRADUAÇÃO
-- filtrando por campus e ano (TA MOSTRANDO QUANTIDADE NUMERO E ALUNOS QUE ESTÃO MATRICULADOS EM x DISCIPLINAS)
WITH q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo
	INNER JOIN curso c ON c.id_curso = cur.id_curso

	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 
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



--filtrando por curso
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



-- Filtrando por turmas
WITH q_disciplinas_curso AS (
		SELECT cu.id_disciplina, 'G' AS nivel 
		FROM graduacao.curriculo cur
		INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo
		INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina
		WHERE cur.id_curso = 379430

		UNION

		SELECT md.id_disciplina, 'T' AS nivel 
		FROM tecnico.modulo_curricular mc
		INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular
		INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo
		INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo
		WHERE ect.id_curso = 379430
)
, q1 AS (
	SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27)
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)
		-- filtra por cursos do campus
		--AND c.id_curso = {id_curso};
		
		-- filtrando por disciplinas
		AND t.id_disciplina IN (
			SELECT id_disciplina FROM q_disciplinas_curso
		)
	GROUP BY id_discente
	ORDER BY total_matricula_discente
)
SELECT total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
FROM q1
GROUP BY total_disciplinas_ano
ORDER BY total_disciplinas_ano
