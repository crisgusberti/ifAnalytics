--Grafico 13: status dos alunos nas disciplinas

WITH Q1 AS (
SELECT 
	mc.id_situacao_matricula,
	sm.descricao AS status_disciplina

FROM ensino.matricula_componente mc
	INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
WHERE mc.ano= 2019 AND mc.periodo =1
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
		
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos    --70640 --eng metalurgica
	
    -- turma específica
	--AND mc.id_turma = 3466 --ingles instrumental --2900 -- Algoritmos e programação I
)
SELECT 
	COUNT (q1.status_disciplina) AS total, q1.status_disciplina
FROM q1
GROUP BY q1.status_disciplina