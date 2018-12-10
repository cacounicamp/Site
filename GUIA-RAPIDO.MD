# Guia rápido de configuração

Guia executado e testado em [Arch Linux](https://wiki.archlinux.org/index.php/Arch_Linux)

## Programas necessários e configuração

```
# Instalamos os pacotes necessários
$ pacman -S docker docker-compose python3 python-pip npm

# Ativamos o docker na inicialização do computador
$ systemctl enable docker

# Permitimos usuário possuir acesso ao docker (observação: esse grupo é equivalente a root, permita apenas usuários confiáveis)
$ gpasswd -a USUÁRIO docker

# Instalamos virtualenv (virtual environment) de Python
$ pip install virtualenv

# Reiniciamos o computador para atualizar permissões (por conta do grupo `docker`)
$ reboot
```

## Bootstrap

Agora faremos a build do [Bootstrap](https://getbootstrap.com/) para o site.

```
# Entramos na pasta do Bootstrap
$ cd boostrap/

# Instalamos os prérequisitos do projeto localmente
$ npm install

# Fazemos a build do Bootstrap
$ npm run build

# Copiamos os arquivos para a pasta estática do site
$ cp build/* ../django-site/djangosite/djangosite/static/

# Saímos dessa pasta
$ cd ..
```

## Configuração do Django

Configuramos agora o site utilizando um virtual environment para depois utilizá-lo inteiramente em `docker`.

Para configurar o ReCaptcha v3, [crie um aplicativo aqui](https://www.google.com/recaptcha/admin).
Para configurar o e-mail, se utilizar o do IC, utilize [essas configurações](https://suporte.ic.unicamp.br/alunos/email).

```
# Entramos na pasta
$ cd django-site/

# Criamos um virtual environment
$ python -m venv NOME_DA_PASTA

# Ativamos o virtual environment
$ source NOME_DA_PASTA/bin/activate
# A esquerda aparece o nome do virtual environment
(NOME_DA_PASTA) $ 

# Instalamos os pré requisitos
(NOME_DA_PASTA) $ pip install -r requirements-virtualenv.txt

# Entramos no projeto Django
$ cd djangosite/

# Criamos o arquivo config.json como diz README.MD
$ EDITOR_PREFERIDO config.json
# Copiamos e colamos o modelo, configurando o necessário

...
```

Abrimos outro terminal e inicializamos o banco de dados no Docker.

```
# Na pasta raiz, ativamos o banco de dados
$ docker-compose -f docker-compose-http.yml up database
```

Voltando à pasta Django:

```
...

# Preparamos a estrutura do banco de dados
$ python manage.py makemigrations atas gestoes noticias ouvidoria paginas_estaticas representantes_discentes
# Observação: conferir lista de aplicativos Django

# Fazemos a estrutura
$ python manage.py migrate

# Criamos um super usuário (administrador do site)
$ python manage.py createsuperuser

# Executamos o servidor para desenvolvimento e testes no IP e porta que quisermos
$ python manage.py runserver ip:porta
```

No nosso navegador, acessamos o site com o final do endereço `/admin` para acessarmos a página de administrador e criar páginas/notícias etc.