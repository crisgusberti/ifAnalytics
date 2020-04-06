--Gráfico 14 e 15 e 16: Percentuais de Frequências

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
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma --Embora esse join não está sendo usado, se eu comentar ele, muda o resultado dos alunos sem frequencia.
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
WHERE mc.ano= 2019 AND mc.periodo = 1
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica
	
    -- turma específica
	--AND mc.id_turma = 3466 --ingles instrumental --2900 -- Algoritmos e programação I



=================================================
CONSULTA DETALHES
-- Para consulta de 100%, menos de 75% e frequencia nulla, substituir o ultimo WHERE por: WHERE frequencia = 100 ou WHERE frequencia < 75 ou WHERE frequencia IS NULL. Para os demais percentuais a consulta é padronizada conforme abaixo

WITH q1 AS(
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato

FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma --Embora esse join não está sendo usado, se eu comentar ele, muda o resultado dos alunos sem frequencia.
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	
WHERE d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos. 
	
	AND mc.ano= 2019 AND mc.periodo = 1
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)
	)
	
    -- curso
	AND d.id_curso =  197350
	
    -- turma específica
	--AND mc.id_turma = 2892
)
SELECT matricula, discente, curso, disciplina, frequencia, contato
FROM q1
--	WHERE frequencia = 100
--	WHERE frequencia < 100 AND frequencia >= 95
--	WHERE frequencia < 95 AND frequencia >= 90
--	WHERE frequencia < 90 AND frequencia >= 85
--	WHERE frequencia < 85 AND frequencia >= 80
	WHERE frequencia < 80 AND frequencia >= 75
--	WHERE frequencia < 75
--	WHERE frequencia IS NULL
ORDER BY discente, frequencia