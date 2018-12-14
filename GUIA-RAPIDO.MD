# Guia rápido de configuração

Guia executado e testado em [Arch Linux](https://wiki.archlinux.org/index.php/Arch_Linux).

## Para desenvolvimento e/ou configuração inicial de produção

### Programas necessários e configuração

Instalamos os pacotes necessários:
```
$ pacman -S docker docker-compose python3 python-pip npm
```

Ativamos o Docker na inicialização do computador:
```
$ systemctl enable docker
```

Permitimos usuário possuir acesso ao docker (observação: esse grupo é
equivalente a root, permita apenas usuários confiáveis):
```
$ gpasswd -a USUÁRIO docker
```

Instalamos `virtualenv` (_virtual environment_) de Python:
```
$ pip install virtualenv
```

Reiniciamos o computador para atualizar permissões (por conta do grupo `docker`):
```
$ reboot
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

### Configuração do Django

Configuramos agora o site utilizando um [_virtual
environment_](https://docs.python.org/3/tutorial/venv.html) (instala pacotes de
Python sem que interfira com o resto do sistema, seguindo o mesmo conceito de
Docker, permitindo estabilidade) para depois utilizá-lo inteiramente em
`docker`.

Para configurar o ReCaptcha v3, [crie um aplicativo
aqui](https://www.google.com/recaptcha/admin).

Para configurar o e-mail, se utilizar o do IC, utilize [essas
configurações](https://suporte.ic.unicamp.br/alunos/email).

Entramos na pasta raiz do projeto Django (a partir da pasta raiz do projeto):
```
$ cd django-site/
```

Criamos um _virtual environment_:
```
$ python -m venv NOME_DA_PASTA
```

Ativamos o _virtual environment_:
```
$ source NOME_DA_PASTA/bin/activate
# Note que à esquerda aparece o nome do virtual environment
(NOME_DA_PASTA) $
```

Instalamos os pré requisitos de Python no _virtual environment_:
```
(NOME_DA_PASTA) $ pip install -r requirements-virtualenv.txt
```

Entramos no projeto Django (a partir da pasta raiz do projeto Django):
```
$ cd djangosite/
```

Criamos o arquivo `config.json` como diz [README.MD](README.MD):
```
$ EDITOR_PREFERIDO config.json
# Copiamos e colamos o modelo, configurando o necessário
```

Abrimos outro terminal e, na pasta raiz, ativamos o banco de dados através do
Docker:
```
$ docker-compose -f docker-compose-http.yml up database
```

Voltando à pasta Django, preparamos a estrutura do banco de dados:
```
$ python manage.py makemigrations atas banco_de_provas gestoes noticias membros ouvidoria paginas_estaticas representantes_discentes
# Observação: conferir lista atualizada de aplicativos Django
```

Colocamos a estrutura no banco de dados:
```
$ python manage.py migrate
```

Criamos um super usuário (administrador do site):
```
$ python manage.py createsuperuser
```

Executamos o servidor para desenvolvimento e testes no IP e porta que quisermos:
```
$ python manage.py runserver ip:porta
```

No nosso navegador, acessamos o site com o final do endereço `/admin` para
acessarmos a página de administrador e criar páginas, notícias, menu etc.

Após concluído, fechamos o servidor e o banco de dados utilizando `Ctrl + C`.
Para sair do _virtual environment_, utilize o comando `deactivate`.

