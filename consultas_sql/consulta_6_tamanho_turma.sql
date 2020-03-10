--Consulta Gráfico 6: Tamanho da Turma

WITH q1 AS(
SELECT 
	mc.id_matricula_componente,
	mc.id_discente,
	mc.id_turma,
	mc.id_situacao_matricula,
	ccd.nome

FROM ensino.matricula_componente mc
	INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = cc.id_detalhe
	
WHERE mc.ano= 2019 AND mc.periodo = 2
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
	--AND mc.id_turma = 4673 --ingles instrumental --2900 -- Algoritmos e programação I

GROUP by mc.id_matricula_componente, mc.id_discente, mc.id_turma, mc.id_situacao_matricula, ccd.nome
)
SELECT
	nome as disciplina,
	COUNT(id_discente) AS total_matriculados
FROM q1
GROUP BY disciplina, id_turma
