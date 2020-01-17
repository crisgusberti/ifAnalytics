-- consulta 7
-- total de alunos matriculados por turma


select count(mc.id_discente) as matricula_turma, mc.id_turma, cc.codigo, cc.nivel from ensino.matricula_componente mc
	inner join ensino.turma t on t.id_turma = mc.id_turma
	inner join ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	--inner join graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	--inner join graduacao.curriculo cur on cur.id_curriculo = ccu.id_curriculo
	--inner join curso c ON c.id_curso = {id_curso}

	where  mc.id_situacao_matricula = 2
	    -- filtra por ano 
	    AND t.ano = {2020} 
	
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)
		-- filtra por cursos do campus
		--AND c.id_curso = {id_curso};
	group by mc.id_turma, cc.codigo, cc.nivel
	order by matricula_turma