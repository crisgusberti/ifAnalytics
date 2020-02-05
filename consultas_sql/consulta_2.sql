-- consulta_2
-- CONSULTA 2 - STATUS DO DISCENTE

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