// Script para fazer funcionar a identificação de menu atual ativo

// $(document).ready(function(){
// 	$('ul li a').click(function(){
// 		$('li a').removeClass("active");
// 		$(this).addClass("active");
// 	});
// });




// window.onload = function(){//previne que o script seja executado apos o carregamento da página
// /*
//  * retorna o nome da página atual sem a extensão
//  */
//     function thisPage(){
	
//   var url = document.URL; //retorna a url da página
//   var urlArr = url.split("/");//retorna um array da url separado pelas barras
//   var lastInd = urlArr.length -1;//retorna o ultimo índice do array (tamanho total menos 1, pois o array começa do zero)
//   var thisPageExtension = urlArr[lastInd];//retorna a pagina atual + a extensão .html .php etc.
//   var thisPageArr = thisPageExtension.split(".");//retorna outro array separando o nome da pagina da extenção
//   var thisPage = thisPageArr[0];//retorna a pagina atual sem a extensão

//   return thisPage;
//   } // fim da função thisPage

// var thisPage = thisPage();  // recebe a string da página atual
// document.getElementById(thisPage).className= 'active';// altera a classe do elemento através do id que deve ser igual ao nome da página

// };//fim do script



// $(document).ready(function(){
//   $('ul li a').click(function(){
//     $('li a').removeClass("active");
//     $(this).addClass("active");
// });
// });




// function setActive () {
//     aObj = document.getElementById('menu_direita')
//     .getElementsByTagName('a');
//     for(i=0;i=0) {
//         aObj[i].addClass('active');
//     }
// }







// function mostrarAtivo(tag){
//    var tag_li = document.getElementById('menu_direita');
//    var tag_a = tag_li.getElementsByTagName('a');
//    for (i=0; i<tag_a.length; i++ )
//    {
//       tag_a[i].style.color = "";
//   }
//   tag.style.color = "#ff0000";
// }
//  incluir dentro da tag a isso: onclick="mostrarAtivo(this);"



// $('.nav li').click(function() {
//     $(this).siblings('li').removeClass('active');
//     $(this).addClass('active');

//     return false;
// });





// outro exemplo o item-menu era o nome da classe do li
// $('.item-menu').click(function(e) {
//             $('.item-menu').removeClass('active');
//             $(this).addClass('active');
//           });