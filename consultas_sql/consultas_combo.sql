-- consulta para os campus

SELECT id_unidade, nome FROM comum.unidade 
WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 605, 723)
ORDER BY nome

-- consulta para os cursos
-- EXEMPLO: 31 é o id do unidade 'Campus Porto Alegre'

SELECT id_curso, id_unidade, nome 
FROM curso 
WHERE ativo IS TRUE
AND nivel = 'G'
AND id_unidade IN
(
  SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
)

-- consulta para os períodos de turmas do graduação

SELECT DISTINCT ano, periodo, (ano || '/' || periodo) AS periodo_formatado 
FROM ensino.turma t 
INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
WHERE cc.id_unidade IN
(
	SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(52)	
)
and cc.nivel = 'G'
order by ano desc, periodo desc

-- consulta para as turmas do campus

select ano, periodo, t.id_turma, t.codigo AS codigo_turma, cc.codigo as codigo_disciplina, ccd.nome  
from ensino.turma t 
inner join ensino.componente_curricular cc on cc.id_disciplina = t.id_disciplina
inner join ensino.componente_curricular_detalhes ccd on ccd.id_componente_detalhes = cc.id_detalhe 
where cc.id_unidade in
(
	SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(49)	
)
-- busca os niveis de graduação
and cc.nivel = 'G'
-- busca pelo período filtrado
and ano = 2019 and periodo = 1

