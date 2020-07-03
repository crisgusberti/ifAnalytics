-- Gráfico 9 (era 10): Discentes em exame

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






==============================================
--NOVA VERSÃO PARA OS GRÁFICOS (QUE ESTÁ IMPLEMENTADA NO SISTEMA!)

WITH Q1 AS (
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato
	
FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
  	
WHERE 
	nu.nota_final_unidade IS NOT NULL -- elimina alunos que ainda nao tem nota final em alguma unidade, pois caso contrario estariam abaixo da media
	
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
	-- ano
	AND t.ano = 2019 AND t.periodo = 1
		
    -- campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56))
	
    -- curso
	AND d.id_curso = 197350
	
    -- turma específica
	--AND mc.id_turma = 2892

GROUP BY d.matricula, discente, curso, disciplina, contato 
),
Q2 AS( --precisei colocar essa consulta aqui para ficar igual a consulta de detalhes. Não preciso dela, mas se eu tirar dá difereça com a consulta de detalhes, já que lá esses parametros são obrigatórios. Foi só isso que mudou da versão antiga pra essa.
SELECT matricula, discente, curso, disciplina, media_parcial, contato 
FROM Q1
GROUP BY matricula, discente, curso, disciplina, media_parcial, contato --acho que o problema está nesse group by
)
SELECT 
	SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
	SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media
FROM Q2





=====================================
--CONSULTA PARA DETALHES

WITH Q1 AS(
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato
	
FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
  	
WHERE 
	nu.nota_final_unidade IS NOT NULL -- elimina alunos que ainda nao tem nota final em alguma unidade, pois caso contrario estariam abaixo da media
	
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
	-- ano
	AND t.ano = 2019 AND t.periodo = 1
		
    -- campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56))
	
    -- curso
	AND d.id_curso =  197350
	
    -- turma específica
	--AND mc.id_turma = 2892

GROUP BY d.matricula, discente, curso, disciplina, contato 
)
SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato
FROM q1
	--parametro de detalhes. Na view vai ter duas consultas repetidas, uma com média < 7 e outra com média >= 7. O querySelector vai definir qual das duas vai ser executada
	WHERE q1.media_parcial >= 7
	--WHERE q1.media_parcial < 7
GROUP BY matricula, discente, curso, disciplina, media_parcial, contato
ORDER BY discente, media_parcial
