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


===================================
Principais Esquemas Dentro do SIGAA:
esquema ensino
esquema comum
esquema public
esquema medio
esquema tecnico
esquema graduaçao
esquema lato
esquema stricto
esquema AVA

==================================
Níveis são:
L é Lato
N é Integrado
G é Graduação
T é Técnico
S é Stricto
F é Formação Continuada
E é Mestrado