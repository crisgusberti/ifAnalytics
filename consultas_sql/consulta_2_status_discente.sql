-- CONSULTA GRÁFICO 2: STATUS DO DISCENTE

-- Contagem geral (não considera nível de ensino)
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
GROUP BY sd.status
ORDER BY sd.descricao

-- Contagem geral (agrupa por nível de ensino)
SELECT sd.descricao, nivel, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
GROUP BY sd.status, nivel
ORDER BY nivel, sd.descricao

-- Dados detalhados (não considera nível de ensino)
SELECT sd.descricao, d.nivel, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
ORDER BY sd.descricao, d.nivel, c.nome, nome_pessoa


-- TÉCNICO/INTEGRADO

-- Contagem 
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('T', 'N')
GROUP BY sd.status
ORDER BY sd.descricao

-- Dados detalhados
SELECT sd.descricao, d.nivel, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('T', 'N')
ORDER BY sd.descricao, d.nivel, c.nome, nome_pessoa


-- GRADUAÇÃO

-- Contagem geral
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G')
GROUP BY sd.status
ORDER BY sd.descricao


--select status alunos passando campus e ano

SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G')
AND d.id_gestora_academica IN (
   SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz({31})
)
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
GROUP BY sd.status
ORDER BY sd.descricao


--select status alunos passando curso e ano

SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.id_curso = {28}
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
GROUP BY sd.status
ORDER BY sd.descricao


--select status alunos passando ano e semestre e campus

SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G') 
AND d.id_gestora_academica IN (
   SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz({31})
)
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
GROUP BY sd.status
ORDER BY sd.descricao


--select status alunos passando turma

SELECT sd.descricao, COUNT(distinct d.id_discente) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 
AND mc.id_turma = {4735}
GROUP BY sd.status
ORDER BY sd.descricao

=====================================
-- Status que não estão sendo considerados nas consultas:
-- 2    "CADASTRADO"
-- 3    "CONCLUÍDO"
-- 6    "CANCELADO"
-- 10    "NÃO CADASTRADO"
-- 13    "PENDENTE DE CADASTRO"
-- 9    "FORMADO"
-- 16    "FALECIDO"
-- -1 	"DESCONHECIDO"
====================================


-- Dados detalhados
SELECT sd.descricao, d.nivel, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('G')
ORDER BY sd.descricao, d.nivel, c.nome, nome_pessoa


-- LATO SENSU

-- Contagem
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('L')
GROUP BY sd.status
ORDER BY sd.descricao
-- Dados detalhados
SELECT sd.descricao, d.nivel, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('L')
ORDER BY sd.descricao, d.nivel, c.nome, nome_pessoa

-- STRICTO 

-- Contagem
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('E')
GROUP BY sd.status
ORDER BY sd.descricao

-- Dados detalhados
SELECT sd.descricao, d.nivel, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('E')
ORDER BY sd.descricao, d.nivel, c.nome, nome_pessoa


=====================================================
--CONSULTA DETALHES STATUS DOS ALUNOS, FEITA POR MIM! --não estão mais sendo usadas
SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato
FROM discente d
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
--para a consulta da turma, decomentar o join abaixo
--INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente

WHERE d.nivel IN ('G')

--passando campi
AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56))

--passando periodo
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1 --turma não leva ano e período

--passando curo
AND d.id_curso =  197350

--passando turma
--AND mc.id_turma = 2889

--parametro detalhes
AND sd.descricao = 'ATIVO'

ORDER BY discente


===============================================================
--NOVAS VERSÕES FEITAS POR MIM --NÃO ESTÃO MAIS SENDO USADAS

--CONTAGEM para campus e curso
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G')
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49))
--AND d.id_curso = 211165 --lic matematica
GROUP BY sd.status
ORDER BY sd.descricao

--CONTAGEM para TURMA
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
WHERE d.nivel IN ('G') 
AND t.ano = 2019 and t.periodo = 1 --pega ano/periodo de outro lugar
AND mc.id_turma = 3478
GROUP BY sd.status ORDER BY sd.descricao


--DETALHES --NÃO ESTÃO MAIS SENDO USADAS
SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email AS contato
FROM discente d
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
--INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente --para a consulta da turma, decomentar o join abaixo
WHERE d.nivel IN ('G')
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49))
--AND d.id_curso =  211165
--AND mc.id_turma = 3511
AND sd.descricao = 'ATIVO'
ORDER BY discente


============================
 -- CONTAGEM NOVA VERSÃO UNIFICADA PARA CAMPUS/CURSO/TURMA !!!!!!!!!!!!!!!!!!!!!QUE ESTÃO IMPLEMENTADAS NO SISTEMA!!!!!!!!!!!!!!!!!!!!!!!!!!!
SELECT sd.descricao, COUNT(distinct d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
WHERE d.nivel IN ('G')
AND t.ano = 2019 and t.periodo = 1
AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49))
--AND d.id_curso = 211165 --lic matematica
--AND mc.id_turma = 3511
GROUP BY sd.status
ORDER BY sd.descricao


-- DETALHES NOVA VERSÃO UNIFICADA PARA CAMPUS/CURSO/TURMA !!!!!!!!!!!!!!!!!!!!!QUE ESTÃO IMPLEMENTADAS NO SISTEMA!!!!!!!!!!!!!!!!!!!!!!!!!!!
SELECT d.matricula, p.nome AS discente, c.nome AS curso, sd.descricao AS status, p.email, translate(('55' || CAST(p.codigo_area_nacional_telefone_celular AS varchar) || p.telefone_celular), '-', '') AS celular
FROM discente d
INNER JOIN status_discente sd ON sd.status = d.status 
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.nivel IN ('G')
AND t.ano = 2019 and t.periodo = 1
AND d.id_gestora_academica IN (SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49))
--AND d.id_curso =  211165 --lic matematica
--AND mc.id_turma = 3511
AND sd.descricao = 'ATIVO'
GROUP BY d.matricula, discente, curso, sd.descricao, p.email, celular
ORDER BY discente