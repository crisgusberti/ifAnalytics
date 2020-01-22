--listar todos os ids das unidades (caxias ID 49, POA ID 31)
SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)


--consultar cursos de uma unidade
select * from curso
where id_unidade in (
	SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)
)

--descobrir nome do curso atraves do ID
select * from curso where id_curso = 379430 


--consultar ID turma
select * from ensino.turma limit 1