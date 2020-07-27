//FUNÇÕES JS COMUNS À TODAS AS PÁGINAS. PARA NÃO REPETI-LAS EM TODAS AS PÁGINAS, CENTRALIZEI AQUI.


//pega o retorno da consulta (que vem em uma linha) e quebra em X linhas, dependendo de quantos valores existem dentro da posição 0 do vetor dados, adicionando o label de cada linha para poder gerar o grafico
function formataRetorno(dados, labels){
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

//persiste na seção os valores do parametros utilizados nas consultas da página de detalhes
function persistirParametros(chave, valor){
	sessionStorage.removeItem(chave);
	sessionStorage.setItem(chave, valor);
}

//altera o querySelector para executar a consulta de detalhes correspondente
function definirQuerySelector(querySelector){
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

//Função que centraliza o título do gráfico
function titleCenter() {
	var chart_div_container = '#' + chart_div;
	var $container = $(chart_div_container);
	var svgWidth = $container.find('svg').width();
	// var $titleElem = $container.find("text:contains(" + options.title + ")");
	var $titleElem = $container.find("text:contains(" + titulo_grafico + ")");
	var titleWidth = $titleElem.html().length * ($titleElem.attr('font-size')/2);
	var xAxisAlign = (svgWidth - titleWidth)/2;
	$titleElem.attr('x', xAxisAlign);
}

//função que me diz qual é a página atual
function thisPage(){
	var url = document.URL; //retorna a url da página
	if (url[url.length-1] == "/"){ // remove última barra do endereço
	  	url = url.substring(0, url.length-1);
	}
	var urlArr = url.split("/");//retorna um array da url separado pelas barras
	var thisPage = urlArr[3]; //armazena em thisPage a posição 3 do array que é a posição ref. ao nome da página. Pq ele conta as barras do http:// na hora de splitar
	if (thisPage == "frequencias") { //Correção do acento da palavra
		thisPage = "Frequências";
	}
	return thisPage;
}

//Função que oculta ou mostra a div dos gráficos ou da tabela de detalhes. Essa função é necessária para mostrar, alternadamente, os gráficos ou a tabela de detalhes na mesma página, permitindo assim usar os combos e as seleções já feitas sempre
function mostrarDiv(id_elemento, visibilidade) {
	if (visibilidade == true){
		document.getElementById(id_elemento).style.display = 'block';
		alterarAlturaMenuLateral(id_elemento); //toda vez que a div dos gráficos ou da tabela é mostrada, a altura do menu lateral é recalculada e alterada
	}else{
		document.getElementById(id_elemento).style.display = 'none';
	}
}

// Como eu não consegui, apenas com CSS, alterar dinamicamente a altura da div do menu lateral para que sempre esteja do mesmo tamanho da div dashboards e da div da tabela detalhes, tive que fazer a função abaixo 
function alterarAlturaMenuLateral(elemento){
 	let height_filtros = document.getElementById("filtros").offsetHeight; //pega a altura da div filtos (combos)
 	let height_elemento = document.getElementById(elemento).offsetHeight; //pega a altura do elemento em questão (div dashboards ou table)
 	let heigth_total = height_elemento + height_filtros; //soma a altura dos combos com a do elemento
 	if (heigth_total <  1290) { //define uma altura mínima para a página
 		heigth_total =  1290;
 	}
	document.getElementById("menu_esquerda").style.height = heigth_total + "px"; // seta a soma das alturas no menu lateral
}