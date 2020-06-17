//FUNÇÕES JS COMUNS À TODAS AS PÁGINAS. PARA NÃO REPETI-LAS EM TODAS AS PÁGINAS, CENTRALIZEI AQUI.


function formataRetorno(dados, labels){
    //pega o retorno da consulta (que vem em uma linha) e quebra em X linhas, dependendo de quantos valores existem dentro da posição 0 do vetor dados, adicionando o label de cada linha para poder gerar o grafico

    let dadosNovoArray = [];
    //dependendo do que foi selecionados nos combos, a consulta pode retornar vazia esse if/else faz uma verificação para evitar erros no console.
    if(dados == null || dados.length == 0){ //Se o retorno da consulta for vazio 
		for (var i = 0; i < labels.length; i++) {
			dadosNovoArray[i] = [labels[i], 0]; //o vetor é preenchido com label da linha e valor 0
		}
		return dadosNovoArray;              
    }else{
		for (var i = 0; i < dados[0].length; i++) { //se não, pega quantos valores tem na posição 0 do dados e repete
			dadosNovoArray[i] = [labels[i], dados[0][i]]; //adicionando dentro de cada posição do dadosNovoArray uma label (labels[i]) e seu respectivo valor (dados[0][i])
		}
		return dadosNovoArray;
	}
}

function persistirParametros(chave, valor){
	//persiste na seção os valores do parametros utilizados nas consultas da página de detalhes
	sessionStorage.removeItem(chave);
	sessionStorage.setItem(chave, valor);
}

function definirQuerySelector(querySelector){
	//altera o querySelector para executar a consulta de detalhes correspondente
	if (querySelector == "campus"){
	  persistirParametros("querySelector", "campus_detalhes");
	} else if (querySelector == "periodo"){
	  persistirParametros("querySelector", "periodo_detalhes");
	} else if(querySelector == "curso"){
	  persistirParametros("querySelector", "curso_detalhes");
	} else if(querySelector == "turma"){
	  persistirParametros("querySelector", "turma_detalhes");
	}
	// window.location.href="{% url 'detalhes' %}"; //Redireciona para a página de detalhes
	gerarDetalhamento(); // função da página de detalhes.html que pega os dados e monta a tabela de detalhes
}

function titleCenter() {
	// Função que centraliza o título do gráfico
	var chart_div_container = '#' + chart_div;
	var $container = $(chart_div_container);
	var svgWidth = $container.find('svg').width();
	// var $titleElem = $container.find("text:contains(" + options.title + ")");
	var $titleElem = $container.find("text:contains(" + titulo_grafico + ")");
	var titleWidth = $titleElem.html().length * ($titleElem.attr('font-size')/2);
	var xAxisAlign = (svgWidth - titleWidth)/2;
	$titleElem.attr('x', xAxisAlign);
}




