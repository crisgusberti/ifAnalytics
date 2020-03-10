-- Gráfico 10: Discentes em exame

WITH Q1 AS (
SELECT 
	mc.id_matricula_componente,
	SUM(nu.nota_final_unidade) / 2 AS media_parcial
	
FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
  	
WHERE 
	nu.nota_final_unidade IS NOT NULL -- elimina alunos que ainda nao tem nota final em alguma unidade, pois caso contrario estariam abaixo da media
	
	-- ano
	AND t.ano = 2019 AND t.periodo = 1

	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
		
    -- campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos
	
    -- turma específica
	--AND mc.id_turma = 3466 --ingles instrumental --2900 -- Algoritmos e programação I

GROUP BY mc.id_matricula_componente
)

SELECT 		
	SUM (CASE WHEN q1.media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
	SUM (CASE WHEN q1.media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media
FROM q1