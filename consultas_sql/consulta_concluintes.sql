--


-----  CONSIDERANDO CURSO/CAMPUS

SELECT 

	SUM (CASE WHEN d.prazo_conclusao < 20281 AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, 
	SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano--, não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.
FROM discente d
WHERE d.prazo_conclusao < 20281  -- esse formato de numero???
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica

-- CONSIDERANDO A TURMA

--talvez possa ser a mesma consulta, como as demais consultas novas que nao foram separadas.

SELECT 

	SUM (CASE WHEN d.prazo_conclusao < 20281 AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, 
	SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano--, não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.

	FROM ensino.matricula_componente mc --pq não pode ser from discente?
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
  	WHERE d.prazo_conclusao < 20281  -- esse formato de numero???
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- turma específica
	 AND mc.id_turma = 4277 --2900 -- Algoritmos e programação I
