from django.http import HttpResponse
from django.shortcuts import render, redirect
import ldap, json, os
from django.contrib import messages


def login(request):
    usuarios = ler_usuarios_cadastrados()

    request.session['username'] = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #REMOVIDO PQ AGORA O ADMIN ESTÁ CADASTRADO NO ARQUIVO JSON
        # if username == 'admin' and password == 'admin':
        #     request.session['username'] = username
        #     request.session['campus'] = 'FULL_ACCESS'
        #     request.session['curso'] = 'FULL_ACCESS'
        #     return redirect('/geral')
        # else:
            #Verifica se é usuário autorizado na tabela
        if username not in usuarios: 
            messages.info(request, 'Usuário não autorizado') #sistema de mensagens do Django que retorna uma mensagem especifica
            return redirect('login')
        #REMOVIDO POR NÃO CONSEGUIR USAR LDAP REITOIRA
        # else:
        #     request.session['username'] = username
        #     request.session['campus'] = usuarios[username]['campus_id'] #acessa os dados do json lido pela função ler_usuarios_cadastrados
        #     request.session['curso'] = usuarios[username]['curso_id']
        
        #ADICIONADO POR NÃO CONSEGUIR USAR LDAP REITOIRA
        else:
            request.session['username'] = username
            if password == usuarios[username]['senha']:
                request.session['campus'] = usuarios[username]['campus_id'] #acessa os dados do json lido pela função ler_usuarios_cadastrados
                request.session['curso'] = usuarios[username]['curso_id']
                return redirect('/geral')
            else:
                messages.info(request, 'Usuário ou senha incorretos')
                return redirect('login') 

            #REMOVIDO POR NÃO CONSEGUIR USAR LDAP REITOIRA
            #Autentica no LDAP 
            # username_ldap = 'uid=' + username + ',ou=People,dc=poa,dc=ifrs,dc=edu,dc=br'
            # try:
            #     conn = ldap.initialize('ldap://ldap.poa.ifrs.edu.br')
            #     conn.protocol_version = 3
            #     conn.set_option(ldap.OPT_REFERRALS, 0)
            #     conn.simple_bind_s(username_ldap, password)
            # except ldap.LDAPError:
            #     messages.info(request, 'Usuário ou senha incorretos')
            #     return redirect('login')
            # return redirect('/geral')
    else:
        return render(request,'login.html')

def logout(request):
    try:
        request.session.flush()
    except KeyError:
        pass
    return redirect('login')

def ler_usuarios_cadastrados():
    file_path = os.path.join(os.path.dirname(__file__), 'usuarios_cadastrados.json') #define o caminho e o nome do arquivo
    with open(file_path, "r", encoding="utf8") as usuarios_cadastrados: #abre o arquivo somente leitura (parametro "r")
        return json.load(usuarios_cadastrados) #converte o json em um objeto python


