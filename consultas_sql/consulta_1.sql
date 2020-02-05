-- IfAnalytics
-- CONSULTA 1 - FORMA DE INGRESSO

-- criar duas funções futuramente
dti_ifrs.contar_modo_ingresso();
dti_ifrs.contar_forma_ingresso();

-- Condições
-- Desconsiderar os status: CADASTRO, CANCELADO, CONCLUÍDO, {EXCLUÍDO}, FALECIDO, FORMADO, PENDENTE 

-- Níveis na tabela 'discente' - 
   -- "G" : Graduacao;
   -- "N" : Integrado
   -- "T" : Técnico
   -- "L" : Lato
   -- "E" : Mestrado

   -- nao constam na base, mas na classe 
   -- S: Stricto (ele grava como 'E')
   -- D: Doutorado
   -- R: Residência
   -- F: Formação complementar

-- TÉCNICO/INTEGRADO/SUPERIOR

-- Contagem
SELECT mi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 
AND d.nivel NOT IN ('E', 'L')
GROUP BY mi.id_modalidade_ingresso
ORDER BY mi.descricao

-- passando o campus e ano

SELECT mi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 
AND d.nivel NOT IN ('E', 'L')

AND d.id_gestora_academica IN (
   SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz({31})
)
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
GROUP BY mi.id_modalidade_ingresso
ORDER BY mi.descricao

-- passando o curso e ano

SELECT mi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 
AND d.nivel NOT IN ('E', 'L')
AND d.id_curso = {28}
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
GROUP BY mi.id_modalidade_ingresso
ORDER BY mi.descricao

-- passando um período (ano/semestre) e campus

SELECT  mi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso

WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 
AND d.nivel NOT IN ('E', 'L')

AND d.id_gestora_academica IN (
   SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz({31})
)

AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1

GROUP BY mi.id_modalidade_ingresso
ORDER BY mi.descricao

-- passando o id da turma
SELECT  mi.descricao, COUNT(distinct d.id_discente) AS total_alunos 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso

INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 

AND mc.id_turma = {4735}

GROUP BY mi.id_modalidade_ingresso
ORDER BY mi.descricao


-- Dados detalhados
SELECT mi.descricao, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN ensino.modalidade_ingresso mi ON mi.id_modalidade_ingresso = d.id_modalidade_ingresso
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel NOT IN ('E', 'L')
ORDER BY mi.descricao, c.nome, nome_pessoa


-- LATO SENSU

-- Contagem
SELECT fi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.forma_ingresso fi ON fi.id_forma_ingresso = d.id_forma_ingresso
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel = 'L'
GROUP BY fi.id_forma_ingresso
ORDER BY fi.descricao

-- Dados detalhados
SELECT fi.descricao, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN ensino.forma_ingresso fi ON fi.id_forma_ingresso = d.id_forma_ingresso
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel = 'L'
ORDER BY fi.descricao, c.nome, nome_pessoa


-- STRICTO

-- Contagem
SELECT fi.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN ensino.forma_ingresso fi ON fi.id_forma_ingresso = d.id_forma_ingresso
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel = 'E'
GROUP BY fi.id_forma_ingresso
ORDER BY fi.descricao

-- Dados detalhados
SELECT fi.descricao, d.matricula, p.nome AS nome_pessoa, c.id_curso, c.nome 
FROM discente d 
INNER JOIN ensino.forma_ingresso fi ON fi.id_forma_ingresso = d.id_forma_ingresso
INNER JOIN curso c ON c.id_curso = d.id_curso
INNER JOIN comum.pessoa p ON p.id_pessoa = d.id_pessoa
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) AND d.nivel = 'L'
ORDER BY fi.descricao, c.nome, nome_pessoa
