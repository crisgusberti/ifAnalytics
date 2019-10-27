====================================
--select status alunos passando campus

SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G')
AND d.nivel NOT IN ('E', 'L')
AND d.id_gestora_academica IN (
   SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz({31})
)
GROUP BY sd.status
ORDER BY sd.descricao

=====================================
--select status alunos passando curso

SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G') 
AND d.nivel NOT IN ('E', 'L')
AND d.id_curso = {28}
GROUP BY sd.status
ORDER BY sd.descricao

=====================================
--select status alunos passando ano e semestre

SELECT sd.descricao, COUNT(d.*) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status 
WHERE d.nivel IN ('G') 
AND d.nivel NOT IN ('E', 'L')
AND d.ano_ingresso = 2019 AND d.periodo_ingresso = 1
AND d.id_curso = 509023
GROUP BY sd.status
ORDER BY sd.descricao

=====================================
--select status alunos passando turma

SELECT sd.descricao, COUNT(distinct d.id_discente) AS total_alunos 
FROM discente d 
INNER JOIN status_discente sd ON sd.status = d.status
INNER JOIN ensino.matricula_componente mc ON mc.id_discente = d.id_discente
WHERE d.status NOT IN (2, 3, 6, 16, 9, 10, 13) 
AND mc.id_turma = {4735}
GROUP BY sd.status
ORDER BY sd.descricao

Quais status não estão sendo considerados????