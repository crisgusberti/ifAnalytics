-- total de alunos por disciplina

with q1 as (
	select count(mc.*) as total_matricula_discente, mc.id_discente from ensino.matricula_componente mc
	inner join ensino.turma t on t.id_turma = mc.id_turma
	inner join ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	where 
	    -- filtra por ano 
	    t.ano = 2019 
	    -- remove situacoes (rever)
		and mc.id_situacao_matricula  NOT IN (2, 3, 6, 16, 9, 10, 13)
	    -- filtra o campus
	    and cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)

	group by id_discente
	order by total_matricula_discente
)
select total_matricula_discente as total_disciplinas_ano, count(*) as total_alunos
from q1
group by total_disciplinas_ano
order by total_disciplinas_ano
