-- Consulta Gráfico 7: Discentes Evadidos 


-- GRADUAÇÃO
-- filtrando por campus e ano (vai mostrar x cancelados por curso)
SELECT c.nome AS curso, COUNT(DISTINCT mc.id_discente) AS discentes_evadidos
FROM ensino.matricula_componente mc
	
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma 
INNER JOIN discente d ON d.id_discente = mc.id_discente 
INNER JOIN curso c ON c.id_curso = d.id_curso
	
	WHERE  mc.id_situacao_matricula = 3 
	
	AND t.ano = 2019 AND t.periodo = 1 
	
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)
	) 
	
GROUP BY c.nome


--filtrando por curso (vai mostrar X cancelados por disciplina)
SELECT COUNT(mc.*) AS total_cancelamento_discente, cc.codigo FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo
	INNER JOIN curso c ON c.id_curso = cur.id_curso

	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula = 3
	    -- filtra o campus
	    --AND cc.id_unidade  IN (
  		--	 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		--)
		-- filtra por cursos do campus
		AND c.id_curso = 509023

	GROUP BY cc.codigo
	ORDER BY total_cancelamento_discente

-- nova versao por curso (falta colocar integrado/lato/strictu)

WITH q_disciplinas_curso AS (
		SELECT cu.id_disciplina, 'G' AS nivel 
		FROM graduacao.curriculo cur
		INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo
		INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina
		WHERE cur.id_curso = 216925

		UNION

		SELECT md.id_disciplina, 'T' AS nivel 
		FROM tecnico.modulo_curricular mc
		INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular
		INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo
		INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo
		WHERE ect.id_curso = 216925

)
	SELECT cc.codigo, COUNT(mc.*) AS total_cancelamento_discente
	FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula = 3
	    -- filtra por disciplinas que estao na grade do curso
	    AND t.id_disciplina IN (
			SELECT id_disciplina FROM q_disciplinas_curso	
		)	
		GROUP BY cc.codigo
	ORDER BY total_cancelamento_discente

--não tem filtro por turma pq essa informação não seria relevante. Esse gráfico para no curso que mostra as informações já por disciplina