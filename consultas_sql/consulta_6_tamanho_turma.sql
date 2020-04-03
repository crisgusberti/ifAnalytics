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

GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, mc.id_situacao_matricula, ccd.nome
)
SELECT
	nome AS disciplina,
	COUNT(id_discente) AS total_matriculados
FROM q1
GROUP BY disciplina, id_turma



=======================================
--NOVA VERSÃO FEITA POR MIM E QUE ESTÁ IMPLEMENTADA NO SISTEMA!!	
--serve para CAMPUS/CURSO/TURMA

WITH q1 AS(
SELECT 
	mc.id_matricula_componente,
	mc.id_discente,
	mc.id_turma,
	ccd.nome

FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
	
WHERE d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
	
    -- busca o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
		
	AND mc.ano= 2019 AND mc.periodo = 2
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica
	
    -- turma específica
	--AND mc.id_turma = 4673 --ingles instrumental --2900 -- Algoritmos e programação I

GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome
)
SELECT
	nome AS disciplina, COUNT(id_discente) AS total_matriculados
FROM q1
GROUP BY disciplina, id_turma
order by disciplina


=======================================
--CONSULTA DETALHES
--serve para campus/curso/turma

SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato 
	
FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	
WHERE d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) -- 2 é matriculado, do 6 ao 27 são todos os tipos de reprovação e do 4 ao 24 aprovações incluindo cert. conhecimento e aprov. estudos.
	
    -- busca o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
	--passando periodo
	AND mc.ano= 2019 AND mc.periodo = 2
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica
	
    -- turma específica
	--AND mc.id_turma = 4673 --ingles instrumental --2900 -- Algoritmos e programação I

	-- detalhe
	--AND ccd.nome = 'METALURGIA FÍSICA I'
GROUP BY d.matricula, discente, curso, disciplina, contato
ORDER BY discente


