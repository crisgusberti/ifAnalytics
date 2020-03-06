SELECT 

	SUM (CASE WHEN mc.porcentagem_frequencia = 100 THEN 1 ELSE 0 END) AS total_100, 
	SUM (CASE WHEN mc.porcentagem_frequencia < 100 AND mc.porcentagem_frequencia >= 95 THEN 1 ELSE 0 END) AS total_95_a_100,
	SUM (CASE WHEN mc.porcentagem_frequencia < 95 AND mc.porcentagem_frequencia >= 90 THEN 1 ELSE 0 END) AS total_90_a_95,
	SUM (CASE WHEN mc.porcentagem_frequencia < 90 AND mc.porcentagem_frequencia >= 85 THEN 1 ELSE 0 END) AS total_85_a_90,
	SUM (CASE WHEN mc.porcentagem_frequencia < 85 AND mc.porcentagem_frequencia >= 80 THEN 1 ELSE 0 END) AS total_80_a_85,
	SUM (CASE WHEN mc.porcentagem_frequencia < 80 AND mc.porcentagem_frequencia >= 75 THEN 1 ELSE 0 END) AS total_75_a_80,
	SUM (CASE WHEN mc.porcentagem_frequencia < 75 THEN 1 ELSE 0 END) AS total_menos_75,
	SUM (CASE WHEN mc.porcentagem_frequencia IS NULL THEN 1 ELSE 0 END) AS alunos_sem_frequencia

	FROM ensino.matricula_componente mc
	
	INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
  	WHERE mc.ano= 2019 AND mc.periodo = 1 --pode ser da tabela matricula_componente ou tem q ser da tabela turma?
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
	-- como ficam as disciplinas onde o status é matriculado e não tem resultado final?
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	--AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica
	
    -- turma específica
	--AND mc.id_turma = 3466 --ingles instrumental --2900 -- Algoritmos e programação I

