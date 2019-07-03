# Guia rápido de configuração

Guia executado e testado em
[Arch Linux](https://wiki.archlinux.org/index.php/Arch_Linux).

## Para desenvolvimento e/ou configuração inicial de produção

### Programas necessários e configuração

Instalamos os pacotes necessários:
```
$ pacman -S python3 python-pipenv mariadb npm
```

Ou, no Ubuntu:
```
$ apt install python3-pip mariadb-server
$ pip3 install pipenv
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
pacotes do sistema operacional). Faremos isso através de `pipenv`, uma
ferramenta que torna mais agradável trabalhar com _virtual environments_.

Entramos na pasta raiz do projeto Django (a partir da pasta raiz do projeto):
```
$ cd django-site/
```

Criamos um _virtual environment_ instalando todos os pacotes do projeto
(descritos nos arquivos `Pipfile` e `Pipfile.lock`):
```
$ pipenv install
```

Ativamos o _virtual environment_ através do `pipenv`:
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
# Copiamos e colamos o modelo, configurando o necessário
```

Para configurar o ReCaptcha v3, [crie um aplicativo
aqui](https://www.google.com/recaptcha/admin).

Para configurar o e-mail: se utilizar o do IC, utilize [essas
configurações](https://suporte.ic.unicamp.br/alunos/email); caso contrário,
procure as configurações do provedor de sua escolha.

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

Executamos o servidor para desenvolvimento e testes no IP e porta que quisermos:
```
(django-site) $ python manage.py runserver ip:porta
```

No nosso navegador, acessamos o site com o final do endereço `/admin` para
acessarmos a página de administrador e criar páginas, notícias, menu etc.

Após concluído, fechamos o servidor e o banco de dados utilizando `Ctrl + C`.
Para sair do _virtual environment_, utilize o comando `exit` ou utilize o atalho
`Ctrl + D` (isso não fechará o terminal, pois o `pipenv` abre uma sessão ao ser
ativado).


## Para produção

Após executar os mesmos passos para desenvolvimento (preparar o _workspace_ é
bem parecido com preparar o website para produção, pois inicializamos o banco de
dados, criamos um _super user_ etc).

### Configurando HTTPS

Na primeira execução, é necessário adquirir os certificados para habilitar o
serviço HTTPS. Utilizamos o arquivo `docker-compose-cert.yml`, que irá servir o
comprovante de controle de domínio para Let's Encrypt.

É necessário para o servidor HTTPS que utilizamos criar o arquivo `dhparam.pem`
na pasta `nginx/certificados/`:
```
§ openssl dhparam -out certificados/dhparam.pem 2048
```

Criamos as imagens do Docker para a aquisição do primeiro certificado:
```
§ docker-compose -f docker-compose-cert.yml build
§ docker-compose -f docker-compose-cert.yml up
... Aguardamos a verificação ...
(Ctrl + C para parar)
```

Finalmente, criamos as imagens para o servidor HTTPS:
```
§ docker-compose -f docker-compose-https.yml build
```

### Inicializando o servidor

Podemos executar o Docker para produção com um _daemon_:
```
$ docker-compose -f (arquivo docker-compose) up -d
```

Podemos ver quais os _containers_ ativos no Docker através do comando:
```
$ docker ps
```

Para parar o Docker, utilizamos:
```
$ docker-compose -f (arquivo docker-compose) down
```
