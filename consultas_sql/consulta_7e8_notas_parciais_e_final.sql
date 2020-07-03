--Consulta Gráfico 7 e 8 (era 8 e 9): Notas Parciais e Média Final

WITH Q1 AS (
SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente

FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
  
    -- ano de inicio da turma
WHERE t.ano = 2019 AND t.periodo = 2

	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
    -- busca o campus  -- busca o campus --para curso não estou usando pq não precisa pelo q testei
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)) 
	
    -- curso
	--AND d.id_curso = 197350
	
    -- turma específica
	--AND mc.id_turma = 2900
	
	ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade
)
SELECT 
		SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
		SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media--,
		--q1.unidade
FROM q1
-- unidade = 1 ou 2
WHERE q1.unidade = 1
GROUP BY q1.unidade



=====================================
CONSULTA DETALHES - MÉDIAS PARCIAIS

SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato

FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
  
    -- ano de inicio da turma
WHERE t.ano = 2019 AND t.periodo = 1
	
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.

    -- busca o campus --para curso não estou usando pq não precisa pelo q testei
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)
	)
	
    -- curso
	AND d.id_curso = 197350
	
    -- turma específica
	--AND mc.id_turma = 2900
	
	--unidade
	AND nu.unidade = 1
	
	--parametro detalhes >=7 ou <7 IMPORTANTE!!!!!!!! ESSE PARAMETRO ESTÁ FIXO NA VIEW. EXISTEM DUAS CONSULTAS UMA PARA >=7 E OUTRA PARA <7. O QUERYSELECTOR DEFINE QUAL CONSULTA VAI SER EXECUTADA
	AND nu.nota_final_unidade >= 7
	
	ORDER BY discente, nu.nota_final_unidade



=============================================================================
==================================================================================================================
------------CONSULTA 9 - MEDIAS FINAIS
SELECT 
	SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, 
	SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media
	--OBS: a média final é 7 se vc passar direto, mas se vc fizer o exame a média pra aprovação é 5
		
FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
WHERE d.nivel = 'G'

	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)

	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.

	AND t.ano = 2019 AND t.periodo = 1

	--passando o campus -- não estou usando pra curso!
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)
	)
	
	--passando o curso
    AND d.id_curso = 194730

    --passando a turma
	AND mc.id_turma = 3402



=================================
CONSULTA DETALHES - MÉDIAS FINAIS
--a consulta para cada um dos parametros será repetida, um com AND mc.media_final >= 5 e outra com AND mc.media_final < 5 quem define vai ser o querySelector

SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato
		
FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
	
WHERE d.nivel = 'G'

	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)

	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.

	AND t.ano = 2019 AND t.periodo = 2

	--passando o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)) --não estou usando pra curso
	
	--passando o curso
   -- AND d.id_curso = 194730

    --passando a turma
	--AND mc.id_turma = 3402
	
	--parametro de detalhe
	--AND mc.media_final < 5
	--AND mc.media_final >= 5
	
	ORDER BY discente, mc.media_final

	