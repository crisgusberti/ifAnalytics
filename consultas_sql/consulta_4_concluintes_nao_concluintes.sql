-- Consulta Gráficos 4 (era 4 e 5): Concluíntes e não concluíntes

-----  CONSIDERANDO CAMPUS/CURSO
SELECT 
	--ano/período sendo informado aqui no prazo_conclusão
	SUM (CASE WHEN d.prazo_conclusao < 20281 AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, 
	SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano--, não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.

FROM discente d

WHERE d.prazo_conclusao < 20281 --passando aqui tbm ano/periodo
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- busca o campus
	AND d.id_gestora_academica IN (
		SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49) --caxias
	)
	
    -- curso
	AND d.id_curso =  156478 --tec. prc. metalurgicos


-- CONSIDERANDO A TURMA (poderia ser uma consulta só, como as demais)
SELECT 
	--ano/período sendo informado aqui no prazo_conclusão
	SUM (CASE WHEN d.prazo_conclusao < 20281 AND d.status != 8 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, 
	SUM (CASE WHEN d.status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano--, não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	
WHERE d.prazo_conclusao < 20281 --passando aqui tbm ano/periodo
	AND d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- turma específica
	AND mc.id_turma = 4277 



============================================================================
--NOVAS VERSÕES FEITAS POR MIM

--CONSULTA PARA TODOS OS GRÁFICOS (SERVE PARA CAMPUS/CURSO/TURMA) (NÃO ESTÁ MAIS IMPLEMENTADA.)
-- FOI SUBSTITUIDA PELA VERSÃO ABAIXO DE 3 COLUNAS
WITH q1 AS(
SELECT d.id_discente, d.prazo_conclusao, d.status --preciso do ID pra grupar e não contar repetido e das outras duas colunas pq são elas que vão ser somadas no select abaixo
	

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente


WHERE d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- busca o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	AND d.id_curso = 156478 --tec. prc. metalurgicos
   
   -- turma específica
	--AND mc.id_turma = 4277
group by d.id_discente
)
SELECT 
	SUM (CASE WHEN prazo_conclusao < 20281 THEN 1 ELSE 0 END) AS alunos_passaram_prazo_conclusao, --passar mesmo ano e periodo somente aqui
	SUM (CASE WHEN status = 8 THEN 1 ELSE 0 END) AS alunos_formandos_este_ano --não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.
FROM q1
	
	

================================================ --VERSÃO IMPLANTADA NO SISTEMA!!!!!!
--CONSULTA OFICIAL DO GRÁFICO COM 3 COLUAS, UMA PARA CADA INDICADOR (JUBILADOS. EM VIAS DE JUBILAR. FORMANDOS)
-- da versão  anterior para essa apenas foi adicionado a linha do SUM CASE prazo_conclusão = XXX AND status != 8

WITH q1 AS(
SELECT d.id_discente, d.prazo_conclusao, d.status --preciso do ID pra grupar e não contar repetido e das outras duas colunas pq são elas que vão ser somadas no select abaixo
	

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente


WHERE d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- busca o campus
	--AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	--AND d.id_curso = 156478 --tec. prc. metalurgicos
	
	-- turma específica
	--AND mc.id_turma = 4277
group by d.id_discente
)
SELECT 
	SUM (CASE WHEN prazo_conclusao < 20201 THEN 1 ELSE 0 END) AS alunos_jubilados, --passar mesmo ano e periodo somente aqui
	SUM (CASE WHEN prazo_conclusao = 20201 AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, --alunos q tem prazo de conclusão o ano/semestre atual e não são formandos
	SUM (CASE WHEN status = 8 THEN 1 ELSE 0 END) AS alunos_formandos --não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.
FROM q1






--DETALHES	
============================================
--precisei de consultas diferentes para os detalhes pq o gráfico possui dois indicadores diferentes embutidos(alunos que passaram do prazo de conclusão (jubilados) e alunos formandos (concluintes)). Então a consulta de detalhes é diferente para cada indicador
--CONSULTA PARA DETALHES (específica para a coluna de NÃO CONCLUINTES)

SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso

WHERE d.nivel = 'G'
	
	--ano/periodo
	AND  d.prazo_conclusao < 20281 
	
	AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) e 8 (formando)
	
    -- busca o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	AND d.id_curso = 156478 --tec. prc. metalurgicos
   
   -- turma específica
	--AND mc.id_turma = 4277
	
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato
ORDER BY discente


==========================================================
--CONSULTA PARA DETALHES (específica para a coluna de CONCLUINTES)

SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso

WHERE d.nivel = 'G'
	
	AND d.status = 8 --não considero o prazo_conclusão pq só quero saber os alunos que são formandos, independente de prazo.
	
    -- busca o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	AND d.id_curso = 156478 --tec. prc. metalurgicos
   
   -- turma específica
	--AND mc.id_turma = 4277
	
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato
ORDER BY discente


===================================================
--CONSULTA PARA DETALHES (específica para a coluna de EM VIAS DE JUBILAR)

SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso

WHERE d.nivel = 'G'
	
	--ano/periodo
	AND  d.prazo_conclusao = 20201 
	
	AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo) SE ELE FOR FORMANDO NÃO ENTRA PQ AI JÁ ESTÁ MATRICULADO EM TODAS DISCIPLINAS
	
    -- busca o campus
	AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	AND d.id_curso = 156478 --tec. prc. metalurgicos
   
   -- turma específica
	--AND mc.id_turma = 4277
	
GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato
ORDER BY discente






==================================================================================
--outra forma de fazer, que foi criada do zero, também funciona, mas não sei se sempre da o mesmo resultado que a consulta oficial utilizada

--------------------
--OUTRA FORMA USANDO A GRADUACAO.DISCENTE_GRADUACAO
-- consulta dos quase formandos pronta

WITH q1 AS(
SELECT d.id_discente, d.prazo_conclusao

FROM graduacao.discente_graduacao dg
	INNER JOIN discente d ON d.id_discente = dg.id_discente_graduacao
	INNER JOIN ensino.matricula_componente mc ON mc.id_discente = dg.id_discente_graduacao --só precisa pra turma

WHERE d.nivel = 'G'
	AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo). SE ELE FOR FORMANDO NÃO ENTRA PQ AI JÁ ESTÁ MATRICULADO EM TODAS DISCIPLINAS

	AND d.prazo_conclusao = 20201
	
	AND (dg.ch_aula_pendente != 0 OR dg.ch_atividade_obrig_pendente != 0 OR dg.ch_optativa_pendente != 0 OR dg.ch_total_pendente != 0 OR dg.ch_complementar_pendente != 0)

     -- busca o campus
	--AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	--AND d.id_curso = 156478 --tec. prc. metalurgicos
   
   -- turma específica
	--AND mc.id_turma = 4277
GROUP BY d.id_discente
)
SELECT COUNT (*) AS alunos_quase_formandos FROM q1 



----------------------
-- consulta dos quase formandos - DETALHES

SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_atividade_obrig_pendente, dg.ch_optativa_pendente, dg.ch_total_pendente, dg.ch_complementar_pendente, p.email AS contato

FROM ensino.matricula_componente mc 
	INNER JOIN discente d ON d.id_discente = mc.id_discente
	INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente
	INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
	INNER JOIN curso c ON c.id_curso = d.id_curso

WHERE d.nivel = 'G'
	
	AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) --só está considerando status 1 (ativo). SE ELE FOR FORMANDO NÃO ENTRA PQ AI JÁ ESTÁ MATRICULADO EM TODAS DISCIPLINAS
	
	--ano/periodo
	AND  d.prazo_conclusao = 20201
	
	AND (dg.ch_aula_pendente != 0 OR dg.ch_atividade_obrig_pendente != 0 OR dg.ch_optativa_pendente != 0 OR dg.ch_total_pendente != 0 OR dg.ch_complementar_pendente != 0)
	
    -- busca o campus
	--AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)) --caxias
	
    -- curso
	--AND d.id_curso = 156478 --tec. prc. metalurgicos
   
   -- turma específica
	--AND mc.id_turma = 4277
	
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato, dg.ch_atividade_obrig_pendente, dg.ch_optativa_pendente, dg.ch_total_pendente, dg.ch_complementar_pendente
ORDER BY discente







