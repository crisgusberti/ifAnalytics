 --------------
# IfAnalytics
 --------------



Preparação do ambiente:
=======================
- baixar o python: https://www.python.org/downloads/
- clonar a aplicação do git, de preferencia no C:, digitando pelo CMD "git clone https://github.com/crisgusberti/IfAnalytics"
- pelo CMD entrar na pasta IfAnalytics e digitar o comando: "python -m venv venvIfAnalytics"
- em seguida digitar: "venvIfAnalytics\Scripts\activate"
- em seguida digitar: "python -m pip install --upgrade pip"
- em seguida digitar: "pip install django"
- em seguida digitar: "pip install psycopg2"
<!-- ESSES DOIS PASSOS ABAIXO NÃO PARECEM SER NECESSÁRIOS QND O PROJETO FOR CLONADO DO GIT
- em seguida criar o projeto Django, digitando: "django-admin startproject siteIfAnalytics ." (não esquecer do ponto no fim)
- em seguinda digitar "python manage.py startapp ifAnalytics" 
-->
- em seguinda iniciar o servidor da aplicação com o comando "python manage.py runserver"
- acessar a aplicação pelo endereço "http://127.0.0.1:8000/geral/"
- OBS: o arquivo "settings.py" não é dispoibilizado no projeto





Comandos para utilizar o GIT:
=============================
dentro da pasta do projeto digitar:
-	git status<br/>
ele vai mostrar o que foi modificado
-	git add --all<br/>
ele vai adicionar ou deletar arquivos que foram adicionados ou excluídos
-	git status<br/>
ele vai mostrar em verde o que está pronto para ser commitado
-	git commit -m "Mensagem de commit"<br/>
ele vai commitar e deixar preparado para envio
-	git push<br/>
vai empurrar e subir tudo pro git online.

No outro lado, quando quiser baixar o que foi upado
-	git pull<br/>
ele vai puxar tudo oque tem de novo no git online
