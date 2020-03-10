--GRAFICO 12: APROVADOS E REPROVADOS

SELECT 
	SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, 
	SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados

FROM ensino.matricula_componente mc
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
WHERE mc.ano= 2019 AND mc.periodo = 1
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica
	
    -- turma específica
	--AND mc.id_turma = 3466 --ingles instrumental --2900 -- Algoritmos e programação I