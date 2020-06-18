 --------------
# IfAnalytics
 --------------



Preparação do ambiente:
=======================
- baixar o python: https://www.python.org/downloads/
- clonar a aplicação do git, de preferencia no C:, digitando pelo CMD "git clone https://github.com/crisgusberti/ifAnalytics"
- pelo CMD entrar na pasta IfAnalytics e digitar o comando: "python -m venv venvIfAnalytics"
- em seguida digitar: "venvIfAnalytics\Scripts\activate"
- em seguida digitar: "python -m pip install --upgrade pip"
- em seguida digitar: "pip install django"
- em seguida digitar: "pip install psycopg2"
<!-- ESSES DOIS PASSOS ABAIXO NÃO PARECEM SER NECESSÁRIOS QND O PROJETO FOR CLONADO DO GIT
- em seguida criar o projeto Django, digitando: "django-admin startproject siteIfAnalytics ." (não esquecer do ponto no fim)
- em seguinda digitar "python manage.py startapp ifAnalytics" 
-->

- para a autenticação é necessário instalar o python-ldap:
	- digitar o comando: "python -m pip install python-ldap"
	<!-- - antes de tentar o passo abaixo onde é necessário baixar o C++, tentar o passo seguinte, baixando o arquivo .whl pq deve funcionar sem baixar esse arquivo C++ gigante-->
	- No windows, pode ocorrer um erro informando que "Microsoft Visual C++ 14.0 is required". Se isso ocorrer baixar esse componente deste link: https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16
	- caso isso não resolver e continuarem os erros, procurar nesse site: https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap um arquivo .whl que seja da versão do windows (32 ou 64) e da mesma versão do python instalada (olhando pela identificacão:  Versão Python: 3.6.0, arquivo deve ter a identificação: "cp36-cp36m" em seu nome) 
	- Baixar o arquivo correto segundo a versão e colocar na pasta raiz do sistema
	- Executar esse comando: "pip install --only-binary :all: python_ldap-3.1.0-cp36-cp36m-win_amd64.whl", sendo que "python_ldap-3.1.0-cp36-cp36m-win_amd64.whl" será o nome do arquivo baixado anteriormente
	- quando tudo der certo, execute o comando "python manage.py migrate" para que o Django crie o bd de armazenamento das sessões

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
