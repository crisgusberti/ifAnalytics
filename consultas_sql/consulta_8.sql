-- Consulta notas parciais ()
WITH Q1 AS (
		SELECT 
			mc.id_matricula_componente,
			nu.nota,
			nu.unidade,
			mc.id_discente

	FROM ensino.matricula_componente mc

	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	--INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
  
    -- ano de inicio da turma
	WHERE t.ano = 2019

    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
	)
	
    -- curso
	AND d.id_curso = {ID_CURSO}
	
    -- turma específica
	AND mc.id_turma = {ID_TURMA}
	
	ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota
)
SELECT 
		SUM (CASE WHEN q1.nota >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
		SUM(CASE WHEN q1.nota < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media,
		q1.unidade
FROM q1
--WHERE q1.unidade = 1
GROUP by q1.unidade


------------ MEDIAS FINAIS

SELECT 
		SUM (CASE WHEN mc.media_final >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
		SUM (CASE WHEN mc.media_final < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media
		
FROM ensino.matricula_componente mc

	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
	WHERE t.ano = 2019

	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
	)
	
    AND d.id_curso = {ID_CURSO}
	AND mc.id_turma = 5012


