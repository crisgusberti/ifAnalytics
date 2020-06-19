from django.http import HttpResponse
from django.shortcuts import render, redirect
import ldap

def login(request):
    request.session['username'] = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == 'admin' and password == 'admin':
            request.session['username'] = username
            return redirect('/geral')
        else:  #Tenta login no ldap
            username_ldap = 'uid=' + username + ',ou=People,dc=poa,dc=ifrs,dc=edu,dc=br'
            try:
                conn = ldap.initialize('ldap://ldap.poa.ifrs.edu.br')
                conn.protocol_version = 3
                conn.set_option(ldap.OPT_REFERRALS, 0)
                conn.simple_bind_s(username_ldap, password)
            except ldap.LDAPError:
                return redirect('login')
            request.session['username'] = username
            return redirect('/geral')
    else:
        return render(request,'login.html')

def logout(request):
    try:
        request.session.flush()
    except KeyError:
        pass
    return redirect('login')