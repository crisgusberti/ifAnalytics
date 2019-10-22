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

-- Contagem
SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G')
GROUP BY sd.status
ORDER BY sd.descricao

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