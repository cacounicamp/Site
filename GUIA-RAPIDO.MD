# Guia rápido de configuração

Guia executado e testado em
[Ubuntu Server 18.04.2 LTS](https://ubuntu.com/download/server).


## Para desenvolvimento e/ou configuração inicial de produção

### Programas necessários e configuração

Atualizamos o sistema, instalamos os pacotes necessários e clonamos o
repositório, em Ubuntu:
```
$ apt update
$ apt upgrade
$ apt install git python3-pip mariadb-server npm nginx certbot python3-certbot-nginx libmysqlclient-dev
$ pip3 install pipenv
$ git clone https://github.com/rafaelsartori96/CACo-site.git
```

### Bootstrap

Agora faremos a build do [Bootstrap](https://getbootstrap.com/) para o site.

Entramos (a partir da pasta raiz do projeto) na pasta do Bootstrap:
```
$ cd boostrap/
```

Instalamos os prérequisitos do projeto localmente:
```
$ npm install
```

Para desenvolvimento e testes, iniciamos o ambiente de teste e visualização:
```
$ npm start
```

Para apenas compilar, fazemos a build do Bootstrap:
```
$ npm run build
```

Copiamos os arquivos para a pasta estática do site:
```
$ cp build/* ../django-site/djangosite/djangosite/static/
```

Saímos dessa pasta (voltamos à raiz):
```
$ cd ..
```

### Configuração do banco de dados

Para seguir, precisamos ativar o banco de dados. Em qualquer sistema, é
necessário configurar para maior segurança. No Ubuntu, temos o script:
```
# Se não conseguir acesso, utilize o comando como usuário "root"
$ mysql_secure_installation
# É recomendado apertar 'Y' (yes) para todas as configurações

# Entramos agora para criar o database usado pelo site
$ mysql -u root -p
mysql > CREATE DATABASE nome_do_database;

# Criamos um usuário local com permissão apenas para o banco de dados do site
mysql > CREATE USER 'USUARIO'@'localhost' IDENTIFIED BY 'SENHA';
mysql > GRANT ALL PRIVILEGES ON nome_do_database.* TO 'USUARIO'@'localhost';
mysql > FLUSH PRIVILEGES;
```

Agora basta colocarmos essa configuração no nosso arquivo `config.json`, que
faremos na próxima seção.

### Configuração do Django

Configuramos agora o site utilizando um [_virtual
environment_](https://docs.python.org/3/tutorial/venv.html) (instala pacotes de
Python sem que interfira com o resto do sistema, permitindo estabilidade pois
escolhemos quando queremos atualizar um sistema em produção independente dos
pacotes do sistema operacional). Faremos isso através de pipenv, uma
ferramenta que torna mais agradável trabalhar com _virtual environments_.

Para utilizarmos depois o _virtual environment_ em produção, temos que instalar
o pipenv no local do projeto. Então precisamos definir a
_environment variable_ de configuração do pipenv, basta colocar em
`~/.bashrc` a linha:
```
export PIPENV_VENV_IN_PROJECT=1
```
e depois recarregar a configuração do bash:
```
$ source ~/.bashrc
```

Entramos na pasta raiz do projeto Django (a partir da pasta raiz do projeto):
```
$ cd django-site/
```

Criamos um _virtual environment_ instalando todos os pacotes do projeto
(descritos nos arquivos `Pipfile`, que contém os pacotes do projeto, e
`Pipfile.lock`, que contém o estado atual dos pacotes do projeto):
```
# Para produção, é importante continuar as versões testadas
$ pipenv install --keep-outdated
```

Ativamos o _virtual environment_ através do pipenv:
```
$ pipenv shell
# Note que à esquerda aparece o nome do virtual environment
(django-site) $
```

Entramos no projeto Django (a partir da pasta raiz do projeto Django):
```
(django-site) $ cd djangosite/
```

Editamos o arquivo `config.json` como diz
[README.MD](README.MD#arquivo-de-configuração):
```
(django-site) $ EDITOR_PREFERIDO config.json
# Configuramos o necessário
```

Para configurar o ReCaptcha v3, [crie um aplicativo
aqui](https://www.google.com/recaptcha/admin).

Para configurar o e-mail: se utilizar o do IC, utilize [as
configurações SMTP daqui](https://suporte.ic.unicamp.br/alunos/email); caso
contrário, procure as configurações do provedor de sua escolha.

Para configurar o banco de dados, basta substituir os credenciais.

Se houver qualquer dúvida, volte no endereço do README para ler mais atentamente
o trecho de configuração.

Voltando à pasta Django, preparamos a estrutura do banco de dados:
```
(django-site) $ python manage.py makemigrations atas banco_de_provas gestoes noticias membros ouvidoria paginas_estaticas representantes_discentes
# Observação: conferir lista atualizada de aplicativos Django
```

Colocamos a estrutura no banco de dados:
```
(django-site) $ python manage.py migrate
```

Criamos um super usuário (administrador do site):
```
(django-site) $ python manage.py createsuperuser
```

Copiamos arquivos estáticos para serem servidos:
```
(django-site) $ python manage.py collectstatic
```

Executamos o servidor para desenvolvimento e testes no IP e porta que quisermos:
```
(django-site) $ python manage.py runserver ip:porta
```

No nosso navegador, acessamos o site com o final do endereço `/admin` para
acessarmos a página de administrador e criar páginas, notícias, menu etc. Para
visualizar o site corretamente, é necessário criar pelo menos uma notícia ou uma
página estática com endereço `/` (chamada de _root_ ou raiz).

Após concluído, fechamos o servidor e o banco de dados utilizando `Ctrl + C`.
Para sair do _virtual environment_, utilize o comando `exit` ou utilize o atalho
`Ctrl + D` (isso não fechará o terminal, pois o pipenv abre uma sessão ao ser
ativado).


## Para produção

Após executar os mesmos passos para desenvolvimento (preparar o _workspace_ é
bem parecido com preparar o website para produção, pois inicializamos o banco de
dados, criamos um _super user_ etc).

### Configurando uwsgi (Django)

Para iniciar o servidor utilizando uwsgi (para ser passado pelo nginx),
utilizamos no _virtual environment_:

```
(django-site) $ uwsgi --ini uwsgi.ini
(uwsgi criará o socket ou servirá TCP para o nginx que ainda será configurado)
```

Depois dos testes com nginx, temos que configurar o uwsgi para abrir
automaticamente com um serviço, que está descrito em `uwsgi.service`. Nesse
arquivo, precisamos atualizar os caminhos até o projeto e nome de usuário,
depois copiar e ativar o serviço utilizando systemd. Para isso, fazemos:
```
$ EDITOR_PREFERIDO uwsgi.service
(alteramos o caminho para a raiz do projeto)

# Copiamos o serviço para a pasta de serviços
$ cp uwsgi.service /etc/systemd/system/

# Recarregamos o systemctl
$ systemctl daemon-reload

# Iniciamos o serviço e testamos
$ systemctl start uwsgi.service
```

Após conferir o _status_ utilizando o comando `systemctl status uwsgi.service` e
verificar também se tudo está funcionando (após configurar nginx e testar
utilizando o navegador), podemos ativar o serviço para executar em _boot_.
```
$ systemctl enable uwsgi.service
```

**Observação:** teste também `systemctl stop uwsgi.service`.


### Configurando nginx

Precisamos copiar e configurar o perfil que queremos para nginx, substituindo a
configuração padrão (em `/etc/nginx/nginx.conf`).

```
$ cd nginx/
$ cp http.conf /etc/nginx/nginx.conf
$ EDITOR_PREFERIDO /etc/nginx/nginx.conf
(precisamos alterar os caminhos de alguns itens)
```

É necessário configurar `nginx.conf` para o caminho do _socket_ configurado em
uwsgi e para o caminho das pastas `static/` e `media/`. Então podemos utilizar
o editor para substituir o texto `/caminho/para/projeto/django` pelo caminho
real do projeto em todo o arquivo.

Conferimos se está tudo certo e recarregamos a configuração:
```
$ nginx -t
(verificar se há erros no arquivo de configuração)
$ nginx -s reload

# Com Django aberto, testamos o site e, se necessário, verificamos o log:
$ cat /var/log/nginx/acess.log | less
$ cat /var/log/nginx/error.log | less
```

### Configurando HTTPS

Na primeira execução, é necessário adquirir os certificados para habilitar o
serviço HTTPS. Utilizamos o certbot para fazer isso, ele irá automaticamente
fazer as mudanças necessárias na configuração do nginx.

Para configurar o `dhparam.pem` que utilizanos com nginx, precisamos executar:
```
$ openssl dhparam -out /etc/nginx/dhparam.pem 2048
```


## Para manutenção

### Django e _virtual environment_

Para verificar o que está desatualizado no _virtual environment_ e atualizar, é
necessário estar na pasta que contém o `Pipfile` e executar:

```
# Verificar desatualizado:
$ pipenv update --outdated
# Atualizar:
$ pipenv update
```

### Bootstrap

Para verificar o que está desatualizado no _package_ e atualizar, é necessário
estar na pasta que contém o `package.json` e executar:

```
$ npm outdated
# "Wanted" é a versão compatível descrita pelo package.json
```

Para atualizar para _Latest_ é necessário instalar o pacote `npm-check-updates`
e executar:
```
# Para instalar o pacote:
$ npm install -g npm-check-updates

# Para atualizar:
$ ncu -u
(irá te informar as alterações)
$ npm install
(irá atualizar)

# Teste as novas versões compilando o projeto e corrija incompatibilidades se houver
$ npm run build
```


