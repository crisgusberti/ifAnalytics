-- Consultas específicas para quando for selecionado IFRS

===========
-- Consulta CAMPUS:
SELECT id_unidade, nome FROM comum.unidade WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 723)
ORDER BY CASE WHEN nome = 'INSTITUTO FEDERAL RIO GRANDE DO SUL' THEN 1 ELSE 2 END, nome --ordena deixando IFRS por primeiro

===========
-- Consulta CURSOS:
SELECT c.id_curso, c.id_unidade, right(u.sigla, 3) AS campus, c.nome FROM curso c
INNER JOIN comum.unidade u ON c.id_unidade = u.id_unidade
WHERE c.ativo IS TRUE AND c.nivel = 'G'
ORDER BY u.sigla, c.nome

===========
-- Consulta PERÍODO
SELECT DISTINCT ano, periodo, (ano || '/' || periodo) AS periodo_formatado 
FROM ensino.turma t 
INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina 
WHERE cc.nivel = 'G' ORDER BY ano DESC, periodo DESC

===========
-- Consulta TURMAS (NÃO ESTOU USANDO ESSA, ESTOU USANDO A QUE ESTÁ NO consultas_combo.sql - embora elas sejam praticamente iguais )
SELECT t.ano, t.periodo, mc.id_turma, t.codigo AS codigo_turma, cc.codigo as codigo_disciplina, ccd.nome 
FROM ensino.matricula_componente mc 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma 
INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina 
INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina 
INNER JOIN ensino.componente_curricular_detalhes ccd on ccd.id_componente_detalhes = cc.id_detalhe 
INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo 
INNER JOIN curso c ON c.id_curso = cur.id_curso 
WHERE cc.nivel = 'G'
AND t.ano = 2019 and t.periodo = 1 --passar ano
AND c.id_curso = 197350 --passar curso
GROUP BY t.ano, t.periodo, mc.id_turma, codigo_turma, codigo_disciplina, ccd.nome
ORDER BY codigo_disciplina

===========
-- Consulta FORMA DE INGRESSO
SELECT  mi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
--para a consulta da turma, decomentar o join abaixo
--INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
--comentar ano e semestre qnd fizer a consulta da turma. Senão algumas consultas vem zeradas, não sei pq.
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
--AND d.id_curso =  197350
--AND mc.id_turma = 2892
GROUP BY mi.id_modalidade_ingresso
ORDER BY CAST (SUBSTR(mi.descricao, 1, 2) AS integer) --ordena de acordo com os numeros da descrição, assim aparece corretamente na legenda do gráfico (o "10 - Portador de deficiência" por ultimo não antes do "1 - Acesso universal")

------------------------
-- Consulta DETALHES FORMA DE INGRESSO (para Campus)
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, mi.descricao AS forma_ingresso, p.email AS contato
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
AND mi.descricao = '1 -  ACESSO UNIVERSAL' --passa parametro detalhe
ORDER BY discente

--DETALHES para curso e turma
SELECT d.matricula, p.nome AS discente, c.nome AS curso, mi.descricao AS forma_ingresso, p.email AS contato
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
--INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente --somente para turma preciso de um join com MC
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1 --para turma decidi não usar ANO e periodo
--AND d.id_curso =  197350 --passa curso
--AND mc.id_turma = 2889 --passa turma
AND mi.descricao = '1 -  ACESSO UNIVERSAL' --passa parametro detalhe
ORDER BY discente

===========
-- Consulta STATUS DISCENTE
SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
WHERE d.nivel IN ('G')
AND t.ano = 2019 and t.periodo = 1
--AND d.id_curso = 211165 --lic matematica
--AND mc.id_turma = 3511
GROUP BY sd.status
ORDER BY sd.descricao

-----------------------
-- Consulta DETALHES STATUS DISCENTE (PARA CAMPUS)
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, sd.descricao AS status, p.email AS contato
SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato
FROM discente d
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('G')
AND t.ano = 2019 and t.periodo = 1
--AND d.id_curso =  211165 --lic matematica
--AND mc.id_turma = 3511
AND sd.descricao = 'ATIVO'
GROUP BY d.matricula, discente, curso, sd.descricao, contato
ORDER BY discente


--DETALHES para curso e turma
SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato
FROM discente d
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('G')
AND t.ano = 2019 and t.periodo = 1
--AND d.id_curso =  211165 --lic matematica
--AND mc.id_turma = 3511
AND sd.descricao = 'ATIVO'
GROUP BY d.matricula, discente, curso, sd.descricao, contato
ORDER BY discente


===========
-- Consulta QUANTIDADE MATRICULADOS
WITH q1 AS (
SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
WHERE d.nivel IN ('G')
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) 
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND t.ano = 2019 AND t.periodo = 1 	-- passa período 
--AND d.id_curso =  197350 	--passa curso
--AND t.id_turma = 2900 	--passa turma
GROUP BY mc.id_discente
)
SELECT 
total_matricula_discente AS total_disciplinas_ano, COUNT(*) AS total_alunos
FROM q1
GROUP BY total_disciplinas_ano
ORDER BY total_disciplinas_ano

------------------------
-- Consulta DETALHES QUANTIDADE MATRICULADOS (para campus)
WITH q1 AS (
SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel IN ('G')
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) 
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND t.ano = 2019 AND t.periodo = 1 --passando período
GROUP BY mc.id_discente, d.matricula, discente, curso, contato
)
SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato
FROM q1
WHERE total_matricula_discente = 6 --passa parametro detalhes -por turma não precisa colocar esse parametro pq ele precisa listar todos os alunos daquela turma de qlqr jeito, já que só tem uma.
GROUP BY matricula, discente, curso, total_disciplinas_ano, contato
ORDER BY discente

-- DETALHES PARA CURSO E TURMA
WITH q1 AS (
SELECT COUNT(mc.*) AS total_matricula_discente, mc.id_discente, d.matricula, p.nome AS discente, c.nome AS curso, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel IN ('G')
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) 
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND t.ano = 2019 AND t.periodo = 1 --passando período
--AND d.id_curso =  197350 --passando curso
--AND t.id_turma = 2900 --passando turma
GROUP BY mc.id_discente, d.matricula, discente, curso, contato
)
SELECT matricula, discente, curso, total_matricula_discente AS total_disciplinas_ano, contato
FROM q1
WHERE total_matricula_discente = 6 --passa parametro detalhes -por turma não precisa colocar esse parametro pq ele precisa listar todos os alunos daquela turma de qlqr jeito, já que só tem uma.
GROUP BY matricula, discente, curso, total_disciplinas_ano, contato
ORDER BY discente

===========
-- Consulta CONCLUÍNTES
WITH q1 AS(
SELECT d.id_discente, d.prazo_conclusao, d.status 
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
--AND d.id_curso = 156478 --passa curso
--AND mc.id_turma = 4277 --passa turma
GROUP BY d.id_discente
)
SELECT 
SUM (CASE WHEN prazo_conclusao < 20201 THEN 1 ELSE 0 END) AS alunos_jubilados, --passa período aqui
SUM (CASE WHEN prazo_conclusao = 20201 AND status !=8 THEN 1 ELSE 0 END) AS alunos_quase_formandos, --passa período aqui
SUM (CASE WHEN status = 8 THEN 1 ELSE 0 END) AS alunos_formandos
FROM q1

------------------------
-- Consulta DETALHES CONCLUÍNTES (específica para a coluna de NÃO CONCLUINTES)
-- DETALHES ara CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, d.prazo_conclusao, p.email AS contato
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND  d.prazo_conclusao < 20281 --passa período
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato
ORDER BY discente

-- DETALHES Para CURSO e TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND  d.prazo_conclusao < 20281 --passa período
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
--AND d.id_curso = 156478 --passa curso
--AND mc.id_turma = 4277 --passa turma
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato
ORDER BY discente

------------------------
-- Consulta DETALHES CONCLUÍNTES (específica para a coluna de CONCLUINTES)
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, d.prazo_conclusao, p.email AS contato
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND d.status = 8 --esse é o paramentro de detalhe
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato
ORDER BY discente

-- DETALHES para CURSO e TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, p.email AS contato
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND d.status = 8 --esse é o paramentro de detalhe
--AND d.id_curso = 156478 --passa curso
--AND mc.id_turma = 4277 --passa turma
GROUP BY matricula, discente, curso, d.prazo_conclusao, contato
ORDER BY discente

---------------------------
-- Consulta DETALHES CONCLUÍNTES (específica para a coluna de EM VIAS DE JUBILAR)
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND  d.prazo_conclusao = 20201 --passa período
AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) --esse é o parametro detalhe
GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato
ORDER BY discente

-- DETALHES para CURSO E TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, d.prazo_conclusao, dg.ch_nao_atividade_obrig_pendente AS ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, p.email AS contato
FROM ensino.matricula_componente mc 
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN graduacao.discente_graduacao dg ON dg.id_discente_graduacao = d.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND  d.prazo_conclusao = 20201 --passa período
AND d.status NOT IN (-1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16) --esse é o parametro detalhe
--AND d.id_curso = 156478 --passa curso
--AND mc.id_turma = 4277 --passa turma
GROUP BY matricula, discente, curso, d.prazo_conclusao, ch_componente_obrig_pendente, dg.ch_optativa_pendente, dg.ch_complementar_pendente, dg.ch_total_pendente, contato
ORDER BY discente

===========
-- Consulta TAMANHO TURMAS
WITH q1 AS(
SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
AND mc.ano= 2019 AND mc.periodo = 2 --passa período
--AND d.id_curso =  156478 --passa curso
--AND mc.id_turma = 4673 --passa turma
GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome
)
SELECT
nome AS disciplina, COUNT(id_discente) AS total_matriculados
FROM q1
GROUP BY disciplina, id_turma
ORDER BY total_matriculados

------------------------
-- Consulta DETALHES TAMANHO TURMAS
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, p.email AS contato 
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
AND mc.ano= 2019 AND mc.periodo = 2 --passa período
--AND ccd.nome = 'METALURGIA FÍSICA I' --passa parametro detalhe
GROUP BY d.matricula, discente, curso, disciplina, contato
ORDER BY discente

-- DETALHES para CAMPUS E TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato 
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
AND mc.ano= 2019 AND mc.periodo = 2 --passa período
--AND d.id_curso =  156478 --passa curso
--AND mc.id_turma = 4673 --passa turma
--AND ccd.nome = 'METALURGIA FÍSICA I' --passa parametro detalhe
GROUP BY d.matricula, discente, curso, disciplina, contato
ORDER BY discente

===========
-- Consulta DISCENTES EVADIDOS
WITH q1 AS(
SELECT mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE d.nivel = 'G'
AND mc.id_situacao_matricula IN (3)
AND mc.ano = 2019 AND mc.periodo = 1 --passa período
--AND d.id_curso =  197350 --passa curso
--AND mc.id_turma = 2900 --passa turma
GROUP BY mc.id_matricula_componente, mc.id_discente, mc.id_turma, ccd.nome
)
SELECT
nome AS disciplina,
COUNT(id_discente) AS total_evadidos
FROM q1
GROUP BY disciplina, id_turma
ORDER BY total_evadidos

-------------------------
-- Consulta DETALHES DISCENTES EVADIDOS
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, p.email AS contato 
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND mc.id_situacao_matricula IN (3)
AND mc.ano = 2019 AND mc.periodo = 1 --passa período
--AND ccd.nome = 'BANCO DE DADOS II' --passa detalhes
GROUP BY d.matricula, discente, curso, disciplina, contato
ORDER BY discente

-- DETALHES para CURSO E TURMAS
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, p.email AS contato 
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND mc.id_situacao_matricula IN (3)
AND mc.ano = 2019 AND mc.periodo = 1 --passa período
--AND d.id_curso =  197350 --passa curso
--AND mc.id_turma = 2900 --passa turma descomentar essa e comentar a busca por campus e por curso.
--AND ccd.nome = 'BANCO DE DADOS II' --passa detalhes
GROUP BY d.matricula, discente, curso, disciplina, contato
ORDER BY discente

===========
-- Consulta NOTAS PARCIAIS/FINAIS
WITH Q1 AS (
SELECT mc.id_matricula_componente, nu.nota_final_unidade, nu.unidade, mc.id_discente
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
WHERE t.ano = 2019 AND t.periodo = 2 --passa período
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
--AND d.id_curso = 197350 --passa curso
--AND mc.id_turma = 2900 --passa turma
ORDER BY mc.id_matricula_componente, nu.unidade, nu.nota_final_unidade
)
SELECT 
SUM (CASE WHEN q1.nota_final_unidade >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
SUM(CASE WHEN q1.nota_final_unidade < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media
FROM q1
WHERE q1.unidade = 1 --passa unidade
GROUP BY q1.unidade

-------------------------
-- Consulta DETALHES MÉDIAS PARCIAIS
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE t.ano = 2019 AND t.periodo = 1 --passa período
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
AND nu.unidade = 1 --passa unidade
AND nu.nota_final_unidade >= 7 --esse é o parametro detalhe fixo (essa consulta vai ser repetida para maior q sete e outra para menor que 7)
ORDER BY discente, nu.nota_final_unidade

-- DETALHES para CURSO e TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, nu.nota_final_unidade, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE t.ano = 2019 AND t.periodo = 1 --passa período
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
--AND d.id_curso = 197350 --passa curso
--AND mc.id_turma = 2900 --passa turma
AND nu.unidade = 1 --passa unidade
AND nu.nota_final_unidade >= 7 --esse é o parametro detalhe fixo (essa consulta vai ser repetida para maior q sete e outra para menor que 7)
ORDER BY discente, nu.nota_final_unidade

===========
-- Constulta MÉDIAS FINAIS
SELECT 
SUM (CASE WHEN mc.media_final >= 5 THEN 1 ELSE 0 END) AS notas_acima_media, 
SUM (CASE WHEN mc.media_final < 5 THEN 1 ELSE 0 END) AS notas_abaixo_media
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) 
AND t.ano = 2019 AND t.periodo = 1 --passa período
--AND d.id_curso = 194730 --passa curso
--AND mc.id_turma = 3402 --passa turma

---------------------
-- Consulta DETALHES MÉDIA FINAL
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) 
AND t.ano = 2019 AND t.periodo = 2 --passa período
--AND mc.media_final < 5 --esse é o parametro detalhe fixo (consulta duplicada, uma pra menor q 5 e uma pra maior q 5)
--AND mc.media_final >= 5
ORDER BY discente, mc.media_final

--DETALHES para CURSOS e TURMAS
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.media_final, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24) 
AND t.ano = 2019 AND t.periodo = 2 --passa período
-- AND d.id_curso = 194730 --passa curso
--AND mc.id_turma = 3402 --passa turma
--AND mc.media_final < 5 --esse é o parametro detalhe fixo (consulta duplicada, uma pra menor q 5 e uma pra maior q 5)
--AND mc.media_final >= 5
ORDER BY discente, mc.media_final

===========
-- Consulta DISCENTES EM EXAME
WITH Q1 AS (
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE nu.nota_final_unidade IS NOT NULL
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND t.ano = 2019 AND t.periodo = 1 --passa período
--AND d.id_curso = 197350 --passa curso
--AND mc.id_turma = 2892 --passa turma
GROUP BY d.matricula, discente, curso, disciplina, contato 
),
Q2 AS(
SELECT matricula, discente, curso, disciplina, media_parcial, contato 
FROM Q1
GROUP BY matricula, discente, curso, disciplina, media_parcial, contato
)
SELECT 
SUM (CASE WHEN media_parcial >= 7 THEN 1 ELSE 0 END) AS notas_acima_media, 
SUM (CASE WHEN media_parcial < 7 THEN 1 ELSE 0 END) AS notas_abaixo_media
FROM Q2

-------------------------
-- Consulta DETALHES DISCENTES EM EXAME
-- DETALHES para CAMPUS
WITH Q1 AS(
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE nu.nota_final_unidade IS NOT NULL
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND t.ano = 2019 AND t.periodo = 1 --passa período
GROUP BY d.matricula, discente, curso, disciplina, contato 
)
SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato
FROM q1
WHERE q1.media_parcial >= 7 --parametro de detalhes. Na view vai ter duas consultas repetidas, uma com média < 7 e outra com média >= 7
--WHERE q1.media_parcial < 7
GROUP BY matricula, discente, curso, disciplina, media_parcial, contato
ORDER BY discente, media_parcial

--DETALHES para CURSO e TURMA
WITH Q1 AS(
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, SUM(nu.nota_final_unidade) / 2 AS media_parcial, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.nota_unidade nu ON nu.id_matricula_componente = mc.id_matricula_componente
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
WHERE nu.nota_final_unidade IS NOT NULL
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND t.ano = 2019 AND t.periodo = 1 --passa período
--AND d.id_curso =  197350 --passa curso
--AND mc.id_turma = 2892 --passa turma
GROUP BY d.matricula, discente, curso, disciplina, contato 
)
SELECT matricula, discente, curso, disciplina, ROUND (CAST(media_parcial AS numeric),2) AS media_final, contato
FROM q1
WHERE q1.media_parcial >= 7 --parametro de detalhes. Na view vai ter duas consultas repetidas, uma com média < 7 e outra com média >= 7
--WHERE q1.media_parcial < 7
GROUP BY matricula, discente, curso, disciplina, media_parcial, contato
ORDER BY discente, media_parcial

===========
-- Consulta APROVADOS/REPROVADOS
SELECT 
SUM (CASE WHEN mc.id_situacao_matricula IN (4, 21, 22, 24) THEN 1 ELSE 0 END) AS alunos_aprovados, 
SUM (CASE WHEN mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) THEN 1 ELSE 0 END) AS alunos_reprovados
FROM ensino.matricula_componente mc
INNER JOIN discente d ON d.id_discente = mc.id_discente
WHERE mc.ano= 2019 AND mc.periodo = 1 --passa período
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
--AND d.id_curso =  156478 --passa curso
--AND mc.id_turma = 3466 passa turma

-------------------------------
-- Consulta DETALHES APROVADOS/REPROVADOS
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE  d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
AND mc.ano= 2019 AND mc.periodo = 1 --passa período
AND mc.id_situacao_matricula IN (4, 21, 22, 24) --parametro detalhes - para os aprovados
--AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) --para os reprovados
GROUP BY matricula, discente, curso, disciplina, situacao, contato
ORDER BY discente, situacao

-- DETALHES para CAMPUS e TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE  d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
AND mc.ano= 2019 AND mc.periodo = 1 --passa período
--AND d.id_curso =  197350 --passa curso
--AND mc.id_turma = 2892 --passa turma
AND mc.id_situacao_matricula IN (4, 21, 22, 24) --parametro detalhes - para os aprovados
--AND mc.id_situacao_matricula IN (6, 7 , 9, 25, 26, 27) --para os reprovados
GROUP BY matricula, discente, curso, disciplina, situacao, contato
ORDER BY discente, situacao

===========
-- Consulta STATUS DISCIPLINAS
WITH Q1 AS (
SELECT mc.id_situacao_matricula, sm.descricao AS status_disciplina
FROM ensino.matricula_componente mc
INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
INNER JOIN discente d ON d.id_discente = mc.id_discente
WHERE mc.ano= 2019 AND mc.periodo =1 -- passa período
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
--AND d.id_curso =  156478 --passa curso
--AND mc.id_turma = 3466 --passa turma
)
SELECT q1.status_disciplina, COUNT (q1.status_disciplina) AS total_alunos
FROM q1
GROUP BY q1.status_disciplina
ORDER BY q1.status_disciplina

---------------------------
-- Consulta DETALHES STATUS DISCIPLINAS
-- DETALHES para CAMPUS
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.ano = 2019 AND mc.periodo = 1 --passa período
AND sm.descricao = 'APROVADO' --passa parametro detalhe
GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato --esse id_matricula_componente está aqui pq sem ele da diferença entre o numero de 'EXCLUIDAS' no gráfico de contagem e de 'EXCLUIDAS' na tabela detalhes (não entendi pq, mas assim como está funciona)
ORDER BY discente, situacao

--DETALHES para CURSO E TURMA
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, sm.descricao AS situacao, p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.situacao_matricula sm ON sm.id_situacao_matricula = mc.id_situacao_matricula
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.ano = 2019 AND mc.periodo = 1 --passa período
--AND d.id_curso = 197350 --passa curso
--AND mc.id_turma = 2892 --passa turma
AND sm.descricao = 'APROVADO' --passa parametro detalhe
GROUP BY id_matricula_componente, matricula, discente, curso, disciplina, situacao, contato --esse id_matricula_componente está aqui pq sem ele da diferença entre o numero de 'EXCLUIDAS' no gráfico de contagem e de 'EXCLUIDAS' na tabela detalhes (não entendi pq, mas assim como está funciona)
ORDER BY discente, situacao

===========
-- Consulta FREQUÊNCIAS
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
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma 
INNER JOIN discente d ON d.id_discente = mc.id_discente
WHERE mc.ano= 2019 AND mc.periodo = 1 --passa período
AND d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16) 
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)
--AND d.id_curso =  156478 --passa curso
--AND mc.id_turma = 3466 --passa turma

---------------------------
-- Consulta DETALHES FREQUÊNCIAS
-- DETALHES para CAMPUS
WITH q1 AS(
SELECT d.matricula, p.nome AS discente, (c.nome || ' (' || m.nome || ')') AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma --Embora esse join não está sendo usado, se eu comentar ele, muda o resultado dos alunos sem frequencia.
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.municipio m ON c.id_municipio = m.id_municipio
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)  
AND mc.ano= 2019 AND mc.periodo = 1 --passa período
)
SELECT matricula, discente, curso, disciplina, frequencia, contato
FROM q1
-- Para consulta de 100%, menos de 75% e frequencia nulla, substituir o ultimo WHERE por: WHERE frequencia = 100 ou WHERE frequencia < 75 ou WHERE frequencia IS NULL. Para os demais percentuais a consulta é padronizada conforme abaixo
--	WHERE frequencia = 100
--	WHERE frequencia < 100 AND frequencia >= 95
--	WHERE frequencia < 95 AND frequencia >= 90
--	WHERE frequencia < 90 AND frequencia >= 85
--	WHERE frequencia < 85 AND frequencia >= 80
	WHERE frequencia < 80 AND frequencia >= 75
--	WHERE frequencia < 75
--	WHERE frequencia IS NULL
ORDER BY discente, frequencia


--DETALHES para CURSO e TURMA
WITH q1 AS(
SELECT d.matricula, p.nome AS discente, c.nome AS curso, ccd.nome AS disciplina, mc.porcentagem_frequencia AS frequencia,  p.email AS contato
FROM ensino.matricula_componente mc
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma --Embora esse join não está sendo usado, se eu comentar ele, muda o resultado dos alunos sem frequencia.
INNER JOIN discente d ON d.id_discente = mc.id_discente
INNER JOIN ensino.componente_curricular_detalhes ccd ON ccd.id_componente_detalhes = mc.id_componente_detalhes
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
INNER JOIN curso c ON c.id_curso = d.id_curso
WHERE d.nivel = 'G'
AND d.status NOT IN (-1, 2, 3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16)
AND mc.id_situacao_matricula IN (2, 6, 7 , 9, 25, 26, 27, 4, 21, 22, 24)  
AND mc.ano= 2019 AND mc.periodo = 1 --passa período
--AND d.id_curso =  197350 --passa curso
--AND mc.id_turma = 2892 --passa turma
)
SELECT matricula, discente, curso, disciplina, frequencia, contato
FROM q1
-- Para consulta de 100%, menos de 75% e frequencia nulla, substituir o ultimo WHERE por: WHERE frequencia = 100 ou WHERE frequencia < 75 ou WHERE frequencia IS NULL. Para os demais percentuais a consulta é padronizada conforme abaixo
--	WHERE frequencia = 100
--	WHERE frequencia < 100 AND frequencia >= 95
--	WHERE frequencia < 95 AND frequencia >= 90
--	WHERE frequencia < 90 AND frequencia >= 85
--	WHERE frequencia < 85 AND frequencia >= 80
	WHERE frequencia < 80 AND frequencia >= 75
--	WHERE frequencia < 75
--	WHERE frequencia IS NULL
ORDER BY discente, frequencia











































