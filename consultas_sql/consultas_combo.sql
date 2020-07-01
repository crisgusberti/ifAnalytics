-- consulta para os campus
SELECT id_unidade, nome FROM comum.unidade 
WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 605, 723)
ORDER BY nome

-----NOVA VERSÃO que mostrar IFRS tbm. É ESSA QUE ESTÁ NO SISTEMA
SELECT id_unidade, nome FROM comum.unidade WHERE unidade_responsavel = id_unidade AND id_unidade NOT IN (2, 723)
ORDER BY CASE WHEN nome = 'INSTITUTO FEDERAL RIO GRANDE DO SUL' THEN 1 ELSE 2 END, nome
-------------

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


-- consulta para as turmas do campus e curso
SELECT mc.id_turma, t.codigo AS codigo_turma, cc.codigo as codigo_disciplina, ccd.nome

FROM ensino.matricula_componente mc

INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma
INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina

INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina
INNER JOIN ensino.componente_curricular_detalhes ccd on ccd.id_componente_detalhes = cc.id_detalhe
INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo
INNER JOIN curso c ON c.id_curso = cur.id_curso

WHERE 
	-- filtra por ano 
	t.ano = 2019 and t.periodo = 1

	--giltra por nível
	AND cc.nivel = 'G'

	-- filtra o campus
	AND cc.id_unidade  IN (
		 SELECT id_unidade FROM dti_ifrs.montar_arvore_organiz(56)
	)
	-- filtra por cursos do campus
	AND c.id_curso = 197350

GROUP BY mc.id_turma, codigo_turma, codigo_disciplina, ccd.nome


----NOVA VERSÃO - QUE ESTÁ IMPLEMENTADA NO SISTEMA
--não estou usando mais o campus_id pq ele busca do mesmo jeito e assim funciona caso o usuário tenha selecionado IFRS q é campus ID 605 e que se eu passar esse ID no função "dti_ifrs.montar_arvore_organiz" ele não traz nada 
SELECT t.ano, t.periodo, mc.id_turma, t.codigo AS codigo_turma, cc.codigo as codigo_disciplina, ccd.nome 
FROM ensino.matricula_componente mc 
INNER JOIN ensino.turma t ON t.id_turma = mc.id_turma 
INNER JOIN ensino.componente_curricular cc ON cc.id_disciplina = t.id_disciplina 
INNER JOIN graduacao.curriculo_componente ccu ON ccu.id_componente_curricular = cc.id_disciplina 
INNER JOIN ensino.componente_curricular_detalhes ccd on ccd.id_componente_detalhes = cc.id_detalhe 
INNER JOIN graduacao.curriculo cur ON cur.id_curriculo = ccu.id_curriculo 
INNER JOIN curso c ON c.id_curso = cur.id_curso 
WHERE t.ano = %s and t.periodo = %s 
AND cc.nivel = 'G' 
AND c.id_curso = %s 
GROUP BY t.ano, t.periodo, mc.id_turma, codigo_turma, codigo_disciplina, ccd.nome