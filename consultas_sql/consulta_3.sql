-- total de alunos por disciplina

-- selecionando um curso graduacao
with q1 as (
	select count(mc.*) as total_matricula_discente, mc.id_discente from ensino.matricula_componente mc
	inner join ensino.turma t on t.id_turma = mc.id_turma
	inner join ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	inner join graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	inner join graduacao.curriculo cur on cur.id_curriculo = ccu.id_curriculo
	inner join curso c ON c.id_curso = cur.id_curso

	where 
	    -- filtra por ano 
	    t.ano = 2019 
	    -- alunos matriculados
		AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27)
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)
		-- filtra por cursos do campus
		AND c.id_curso = {id_curso}
		

	group by id_discente
	order by total_matricula_discente
)
select total_matricula_discente as total_disciplinas_ano, count(*) as total_alunos
from q1
group by total_disciplinas_ano
order by total_disciplinas_ano

----  ---------


with q_disciplinas_curso as (
		select cu.id_disciplina, 'G' as nivel 
		from graduacao.curriculo cur
		inner join graduacao.curriculo_componente cc on cc.id_curriculo = cur.id_curriculo
		inner join ensino.componente_curricular cu ON cc.id_componente_curricular = cu.id_disciplina
		where cur.id_curso = 379430
		--where cur.id_curso = 379430
		where cur.id_curso = {id_curso}

		union

		select md.id_disciplina, 'T' as nivel 
		from tecnico.modulo_curricular mc
		inner join tecnico.estrutura_curricular_tecnica ect on ect.id_estrutura_curricular = mc.id_estrutura_curricular
		inner join tecnico.modulo m on m.id_modulo = mc.id_modulo
		inner join tecnico.modulo_disciplina md on md.id_modulo = m.id_modulo
	--	where ect.id_curso = 379430
		where cur.id_curso = {id_curso}

)
with q1 as (
	select count(mc.*) as total_matricula_discente, mc.id_discente from ensino.matricula_componente mc
	inner join ensino.turma t on t.id_turma = mc.id_turma
	inner join ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina
	
	--inner join graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
	--inner join graduacao.curriculo cur on cur.id_curriculo = ccu.id_curriculo
	--inner join curso c ON c.id_curso = {id_curso}

	where 
	    -- filtra por ano 
	    t.ano = 2019 
	    -- alunos matriculados
		AND mc.id_situacao_matricula IN (2, 4, 6, 7, 8, 9, 24, 25, 26, 27)
	    -- filtra o campus
	    AND cc.id_unidade  IN (
  			 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(31)
		)
		-- filtra por cursos do campus
		--AND c.id_curso = {id_curso};
		
		-- filtrando por disciplinas
		AND t.id_disciplina IN (
			SELECT id_disciplina FROM q_disciplinas_curso
		)

	group by id_discente
	order by total_matricula_discente
)
select total_matricula_discente as total_disciplinas_ano, count(*) as total_alunos
from q1
group by total_disciplinas_ano
order by total_disciplinas_ano
