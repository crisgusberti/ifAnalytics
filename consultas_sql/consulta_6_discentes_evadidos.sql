-- Consulta Gráfico 6 (era 7): Discentes Evadidos 


-- GRADUAÇÃO
-- filtrando por campus e ano (vai mostrar x cancelados por curso)
SELECT c.nome AS curso, COUNT(DISTINCT mc.id_discente) AS discentes_evadidos
FROM ensino.matricula_componente mc
	
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma 
INNER JOIN discente d ON d.id_discente = mc.id_discente 
INNER JOIN curso c ON c.id_curso = d.id_curso
	
	WHERE  mc.id_situacao_matricula = 3 
	
	AND t.ano = 2019 AND t.periodo = 1 
	
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)
	) 
	
GROUP BY c.nome


--filtrando por curso (vai mostrar X cancelados por disciplina) --VERSÃO ANTIGA BRYAN
SELECT COUNT(mc.*) AS total_cancelamento_discente, cc.codigo FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo
	INNER JOIN curso c ON c.id_curso = cur.id_curso

	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula = 3
	    -- filtra o campus
	    --AND cc.id_unidade  IN (
  		--	 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		--)
		-- filtra por cursos do campus
		AND c.id_curso = 509023

	GROUP BY cc.codigo
	ORDER BY total_cancelamento_discente


-- outra versao por curso (falta colocar integrado/lato/strictu) --VERSÃO ANTIGA BRYAN
WITH q_disciplinas_curso AS (
	SELECT cu.id_disciplina, 'G' AS nivel 
	FROM graduacao.curriculo cur
	INNER JOIN graduacao.curriculo_componente cc ON cc.id_curriculo = cur.id_curriculo
	INNER JOIN ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina
	WHERE cur.id_curso = 216925

	UNION

	SELECT md.id_disciplina, 'T' AS nivel 
	FROM tecnico.modulo_curricular mc
	INNER JOIN tecnico.estrutura_curricular_tecnica ect ON ect.id_estrutura_curricular = mc.id_estrutura_curricular
	INNER JOIN tecnico.modulo m ON m.id_modulo = mc.id_modulo
	INNER JOIN tecnico.modulo_disciplina md ON md.id_modulo = m.id_modulo
	WHERE ect.id_curso = 216925
	)
	SELECT cc.codigo, COUNT(mc.*) AS total_cancelamento_discente
	FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	WHERE 
	    -- filtra por ano 
	    t.ano = 2019 AND t.periodo = 1
	    -- alunos matriculados
		AND mc.id_situacao_matricula = 3
	    -- filtra por disciplinas que estao na grade do curso
	    AND t.id_disciplina IN (
			SELECT id_disciplina FROM q_disciplinas_curso	
		)	
	GROUP BY cc.codigo
	ORDER BY total_cancelamento_discente



======================
--nova versão feita por mim para CAMPUS, CURSO e TURMA --É ESSA QUE ESTÁ SENDO USADA NO SISTEMA

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
	AND mc.id_situacao_matricula IN (3) -- CANCELADO
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56) --vera
	)
	
	AND mc.ano = 2019 AND mc.periodo = 1
	
    -- curso
	--AND d.id_curso =  197350 --ads
	
    -- turma específica (para a consulta de turma, descomentar essa e comentar a busca por campus e por curso.)
	--AND mc.id_turma = 2900 --Algoritmos e programação I

GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome
)
SELECT
	nome AS disciplina,
	COUNT(id_discente) AS total_evadidos
FROM q1
GROUP BY disciplina, id_turma
ORDER BY total_evadidos


===============================================
--CONSULTA DETALHES

SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato 

FROM ensino.matricula_componente mc
	INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso
	
WHERE d.nivel = 'G'
	AND mc.id_situacao_matricula IN (3) -- CANCELADO
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56) --vera
	)
	
	AND mc.ano = 2019 AND mc.periodo = 1
	
    -- curso
	--AND d.id_curso =  197350 --ads
	
    -- turma específica (para a consulta de turma, descomentar essa e comentar a busca por campus e por curso.)
	--AND mc.id_turma = 2900 --Algoritmos e programação I

	-- detalhe
	--AND ccd.nome = 'BANCO DE DADOS II'
	
GROUP BY d.matricula, discente, curso, disciplina, contato
ORDER BY discente
