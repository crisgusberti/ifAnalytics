-- Consulta 7
-- Discentes Evadidos


-- GRADUAÇÃO
-- filtrando por campus e ano
SELECT COUNT(mc.id_discente) AS matricula_turma, mc.id_turma, cc.codigo, cc.nivel FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	--INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	--INNER JOIN graduacao.curriculo cur on cur.id_curriculo = ccu.id_curriculo
	--INNER JOIN curso c ON c.id_curso = {id_curso}

	WHERE  mc.id_situacao_matricula = 2
	    -- filtra por ano 
	    AND t.ano = {2020} 
	
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)
		-- filtra por cursos do campus
		--AND c.id_curso = {id_curso};
	GROUP BY mc.id_turma, cc.codigo, cc.nivel
	ORDER BY matricula_turma


--filtrando por curso
