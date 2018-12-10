# CACo-site

Este é um repositório da segunda versão para o site do CACo. O motivo de existir
uma segunda versão é, além de querer aprender a utilizar servidores web,
framework Django e Docker, padronizar o site (diminuindo a quantidade de páginas
jogadas, provas sem uniformização dos nomes), melhorar a qualidade do que já
existe (permitir envio de imagens nas páginas sem precisar hospedar
externamente, lista de membros que permite _reset_ fácil, avisando todos os
membros devidamente) e atualizar as versões do que já era utilizado (utilizando
os _rewrites_ de Bootstrap e de Django).

Por questão de legibilidade, não me preocupei em utilizar gêneros neutros em
variáveis dentro do código. Porém esse assunto é de extrema importância e DEVE
ser levado em consideração enquanto o conteúdo do site é reescrito.

Utilizei neste guia [Arch
Linux](https://wiki.archlinux.org/index.php/Arch_Linux) e seu sistema de
pacotes.

Um guia rápido de configuração e instalação pode ser encontrado
[aqui](GUIA-RAPIDO.MD).


## Estrutura do servidor

Aqui será descrito o alicerce do servidor e todos os passos para sua
configuração e inicialização.

### Estrutura básica

[nginx](https://www.nginx.com/) (pronunciado _engine x_) é um servidor web de
alta performance. Será utilizado para servir arquivos estáticos e redirecionar
pedidos dinâmicos ao [Django](https://www.djangoproject.com/) através do
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (nginx <-> uWSGI <->
Django).

O banco de dados utilizado é [postgresql](https://www.postgresql.org/) e se
conectará ao Django (django <-> banco de dados).

Tudo é organizado utilizando [Docker](https://www.docker.com/) através de uma
ferramenta `docker-compose`. Ela irá ler arquivos do formato
[`compose file`](https://docs.docker.com/compose/compose-file/), construir
as imagens e configurações dos _containers_ (é bem como o nome diz, é um espaço
individual para a aplicação) para serem executados posteriormente.

Após [instalar
e configurar](https://wiki.archlinux.org/index.php/Docker#Installation) `docker`
e `docker-compose`, usamos para construir a imagem dos _conainers_ (deve estar
na pasta que contém algum `docker-compose.yml` que deseja utilizar):

```
§ ls
(...) docker-compose.yml (...)
§ docker-compose -f docker-compose.yml build
```

E, para iniciar os _containers_:

```
§ docker-compose -f docker-compose.yml up
```

Se o Docker for configurado corretamente (usando `systemctl enable docker` para
garantir que o serviço do Docker se iniciará com o sistema) e, no caso de servir
HTTPS, se o certificado foi obtido com sucesso, o site deve se manter online sem
qualquer interferência humana (requer um detalhezinho rs).

No nosso projeto, há diferentes arquivos `docker-compose.yml`:
* um para servir o site perpetuamente apenas HTTP (`docker-compose-http.yml`),
* outro para aquisiçãoúnica dos certificados HTTPS (`docker-compose-cert.yml`)
* outro para servir perpetuamente o site HTTPS (`docker-compose-https.yml`).

Independente do que escolher, a configuração do Docker é a mesma.


### Estrutura do servidor HTTPS

Usamos o serviço do [Let's Encrypt](https://letsencrypt.org/). Na primeira
execução, é necessário pedir certificados e comprovar que temos controle do
domínio (nginx irá servir um arquivo que nos será dado através do
[certbot](https://certbot.eff.org/), um programa que gerencia os certificados).

Como usamos Docker, não é ideal usar os pacotes `docker` e `docker-nginx` do
Arch Linux, mas sim fazer um _container_ com alguma imagem `certbot` que seja
compatível com o nosso _container_ nginx. De tal forma que o servidor inteiro
permanece inalterado com relação aos certificados (todo o processo fica
encapsulado no Docker, ao contrário do que fazíamos na versão anterior do site).

É por causa disso que há diversos `docker-compose.yml`, pois nginx está
configurado para 3 situações:
* servir HTTP,
* servir o teste dos certificados e
* servir HTTPS após aquisição dos certificados.

Após a aquisição dos certificados pela primeira vez, o _container_
`certbot_renew` (descrito em `docker-compose-https.yml`) deve ser executado
periodicamente para renovar os certificados (Let's Encrypt nos dá certificados
que expiram em 3 meses). Como nginx possui acesso direto aos certificados, é
possível atualizar os certificados sem precisar reiniciar todos os serviços.
Esse é o "detalhezinho rs", é (quase) a única tarefa fora do Docker de que
precisamos.


### Configurando o Docker

Para entender a estrutura dos _containers_, é necessário entender alguns
conceitos:
* _containers_ são imagens Linux pré-configuradas para seu projeto.
* [Alpine](https://alpinelinux.org/) é uma distribuição Linux muito pequena e,
justamente por isso, é comum no Docker. As imagens dos _containers_ ocupam pouco
espaço após construídas, mas a distribuição não utiliza `libc`, uma biblioteca
comum que é usada por muitos aplicativos como o próprio uWSGI (então uWSGI não
pode estar em um _container_ cuja imagem-base é Alpine).
* Se um _container_ requer uma configuração prévia para funcionar (por exemplo,
instalação de pacotes Python, como o próprio Django), é necessário executar essa
configuração usando um arquivo
[`Dockerfile`](https://docs.docker.com/engine/reference/builder/).

A estrutura dos _containers_ de produção (não inclui o _container_ usado para
aquisição dos certificados HTTPS, que é usado apenas uma vez) é, em ordem
crescente de "dependência":

#### `database`:
É baseado na imagem `postgres:alpine` em configuração padrão (definimos apenas
algumas [variáveis de
_environment_](https://wiki.archlinux.org/index.php/Environment_variables) para
tornar o usuário e senha comuns ao Django e fazemos a pasta do banco de dados
vir para a pasta raiz do projeto). Para ligarmos o Django ao banco de dados,
utilizando um Unix socket que é mais eficiente do que conexões TCP. Esse arquivo
socket ficará na raiz do projeto também.

#### `django-caco`:
Possui um `Dockerfile` para configuração do ambiente (que é baseado em uma
imagem do Python na distribuição debian), instalando Django, uWSGi e
dependências do site.
Possui uma dependência (irá ligar apenas depois do `database` estar ligado). A
porta 8080 é exposta ao Docker para que nginx possa conversar com o Django. Não
consegui ainda utilizar um Unix socket para isso.

#### `servidor`:
É baseado na imagem `nginx:alpine`, mas possui arquivo de configuração. Tem
acesso aos arquivos estáticos do site (`/media` e `/static`) e depende de
`django-caco` e possui uma ligação ao _container_ (aquela porta 8080). As portas
80 e 443 são abertas ao público.

#### `certbot_renew` (apenas HTTPS):
Executa apenas um comando e termina. É para renovar os certificados HTTPS. Esses
certificados serão utilizados pelo nginx, mantendo o site encriptado e mais
seguro. Caso não haja um _script_ que execute este _container_ periodicamente,
reiniciar a máquina antes dos 3 meses do certificado expirar basta.

### Criação das imagens do docker

O Docker utiliza imagens configuradas para a execução dos _containers_, é o que
traz estabilidade ao serviço, pois tudo se torna previsível se a imagem é
idêntica para qualquer máquina que a executa.

```
# Criamos as imagens
§ docker-compose -f (arquivo de configuração yml) build
```

Como dito anteriormente, as opções de configurações são HTTP ou HTTPS. A
configuração é adicional com HTTPS pois é necessário adquirir um certificado.

### (Re-)Configuração do banco de dados

O banco de dados precisa receber a estrutura do site. Isso deve ser feito antes
da execução do servidor através dos modelos criados em Django.

Para entrarmos no _environment_ de Python, é necessário estar dentro da imagem
configurada do Docker ou dentro de um _virtual environment_ idêntico ao da
imagem (para minimizar erros). Acredito que é mais fácil iniciar a imagem do
banco de dados e depois utilizar a linha de comando da própria máquina para
entrar no _virtual environment_ idêntico ao da imagem do que fazer algo
mirabolante como iniciar as duas imagens e fazer interagirem uma com a outra.

Portanto, criaremos um _virtual environment_:

```
  # Instalamos virtualenv
§ pip3 install virtualenv
§ cd django-site
  # Criamos um virtual environment dando uma pasta em que será guardada todas as
  # informações do virtual environment
§ python3 -m venv (nome da pasta, usarei 'virtualenv-django')
  # Ativamos o virtual environment (onde virtualenv-django é a sua pasta do seu
  # virtual environment)
§ source virtualenv-django/bin/activate
```

Para obtermos um _virtual environment_ idêntico ao da imagem, precisamos
instalar todas as dependências de nosso projeto Django:

```
  # Usamos o pip para instalar todas as dependências do projeto
(virtualenv-django) § pip install -r requirements.txt
```

Para sairmos desse _virtual environment_, utilizamos:

```
(virtualenv-django) § deactivate
§
```

Agora que já sabe utilizar o _virtual environment_, precisamos utilizá-lo para
configurar as estruturas no banco de dados:

```
  # Iremos iniciar o banco de dados com a opção detached (desvinculada do
  # terminal, o tornará livre para uso)
§ docker-compose -f (arquivo de configuração yml) run -d database
...
  # Entramos no virtual environment idêntico ao configurado na imagem e vamos
  # para a raiz do projeto Django (para a pasta django-site/djangosite)
...
  # Fazemos Django criar as transações para o banco de dados executar
(virtualenv-django) § python3 manage.py makemigrations
  # Executamos as transações no banco de dados
(virtualenv-django) § python3 manage.py migrate
...
  # Terminamos a imagem do banco de dados
§ docker-compose -f (arquivo de configuração yml) down
```

### Configuração HTTPS (apenas para o servidor HTTPS)

Na primeira execução, é necessário adquirir os certificados para habilitar o
serviço HTTPS. Utilizamos o arquivo `docker-compose-cert.yml`, que irá servir o
comprovante de controle de domínio para Let's Encrypt.

É necessário para o servidor HTTPS que utilizamos, criar o arquivo `dhparam.pem`
na pasta `certificados/`:

```
§ openssl dhparam -out certificados/dhparam.pem 2048
```

```
  # Criamos as imagens para a configuração do certificado
§ docker-compose -f docker-compose-cert.yml build
§ docker-compose -f docker-compose-cert.yml up
  # Aguardamos a verificação
...
§ docker-compose -f docker-compose-cert.yml down
  # Criamos as imagens para o servidor HTTPS
§ docker-compose -f docker-compose-https.yml build
```

### Execução do servidor

Para completar, já que o Docker possui imagens configuradas, o banco de dados
possui toda a estrutura atualizada dos modelos do site, basta executar todas as
imagens do Docker:

```
§ docker-compose -f (arquivo de configuração yml) up
```


## Estrutura do site (Django)

Aqui será descrito a estrutura do site como um projeto Django, presente na pasta
`django-site/djangosite`. Django utiliza uma estrutura MCV (_Model, Controller,
View_). Modelos controlam os objetos que serão trabalhados no controlador e
mostrados na _view_.

### Aplicações Django

Django isola cada trecho do site em diversas aplicações, que possuem modelos,
controladores e _views_ individuais. Cada modelo poderá ser editado na páginas
de administrador quando configurado. As aplicações do site são em ordem
aleatória:

#### `paginas_estaticas`

As páginas estáticas são controladas pelo _app_ `paginas_estaticas`. Há modelos
que definem as coisas presentes na barra de menu e outros para cada página.

O menu é composto por:
* `ItemMenu` é um item do menu, filho ou não de um _dropdown_, com um índice que
indica qual sua posição na barra ou dentro do _dropdown_, um endereço para o
qual o item ao ser clicado redirecionará o usuário, um booleano para indicar se
o item estará visível ou não e outro para indicar se é clicável ou não.
* `MenuDropdown` é um `ItemMenu` que contém outros objetos `ItemMenu` e não
possui endereço.

Para a composição das páginas, utilizamos o editor
[CKEditorWidget](https://github.com/django-ckeditor/django-ckeditor#widget),
que já é instalado através do `requirements.txt`. No entanto, é necessário
utilizar o comando:

```
§ python manage.py collectstatic
```

para organizar todos os arquivos estáticos na pasta que será servida. Isso é
preciso para que os arquivos do `CKEditor` possam ser utilizados pelo
navegador.

Utilizaremos este comando na próxima seção para organizar também os arquivos
estáticos do Bootstrap.

As páginas estáticas possuem o modelo `PaginaEstatica`, que é simplesmente uma
página com atributo de texto, editável através do `CKEditor`, associado a um
endereço que será servido se a opção `URL acessível` for `True`. Essa opção é
para podermos fazer páginas que não são servidas mas são contidas em outras
páginas (por exemplo, para customizar a página `contato/sucesso/` sem alterar o
código).

É possível em qualquer página enviar imagens (e arquivos) dinâmicamente.

##### Observação:

Após a criação de uma página, é necessário reiniciar o servidor para que o novo
endereço seja servido corretamente.

#### `ouvidoria`

É um _app_ que controla todo contato feito através da página `contato/`, ele
enviará um e-mail para a própria gestão do CACo através de um e-mail da gestão
do CACo (configurado através do Django em `config.json`).

Um modelo que guardará as informações do pedido de contato, assim não perderemos
nenhuma informação caso o envio do e-mail falhe.

A página de contato pode ser associada a uma instância de `PaginaEstatica` (com
endereço `contato/`), dessa maneira, então, é possível adicionar/editar/remover
textos da página de contato facilmente, sem alterar o código fonte da página
através do servidor.

Além da página de contato, devemos criar instâncias de `PaginaEstatica` para os
endereços `contato/sucesso/` e `contato/falha/` que aparecem respectivamente ao
tentar utilizar a página de contato obtendo sucesso e falha.

#### `atas`

_App_ que controla as atas de reunião e de assembleias. A página principal
(`atas/`) está ligada à página estática `atas/` para produzir uma página
dinâmica.

Há dois modelos: `AtaReuniao` e `AtaAssembleia`. As atas de assembleia podem ser
marcadas como deliberativas ou não. Já as de reunião, podem ser marcadas como
extraordinárias ou não. Ambas possuem conteúdo dinâmico, permitem envio de
arquivos e possuem um trecho sobre _highlights_, para atrair mais usuários à
leitura.

O _app_ ainda descreve o _templatetags_:

##### _templatetag atas_
Auxilia na fabricação da página de atas (há um HTML para os 2 tipos de atas,
esse _template_ possui funções que auxiliam em diferenciar essas atas) e também
processa as últimas atas para ficar ao lado direito do site para fácil acesso.

##### Observação
Junto com `noticias`, `atas` utiliza o serviço de paginação descrito em
`util/util.py`.

#### `noticias`

_App_ controla as notícias do site. Contém a página raiz (`/`, a inicial). O
único modelo descrito é `Noticia`, que guarda o conteúdo (editável pelo
`CKEditor`), a data de criação e um resumo que aparecerá nas listagens de
notícias (página inicial, página `noticias/`). Não há nenhuma página estática
usada nas _views_ de notícias.

Para a _view_ de notícias e atas, temos o documento `util/util.py`, que conta o
número de itens e separa em páginas. O número de itens mostrado por página é
customizável em `settings.py`.

#### `gestoes`

_App_ controla o histórico de gestões do CACo. Ele existe (diferente da criação
de páginas estaticas manualmente que era feito nos anos anteriores) apenas para
uniformizar a apresentação de informações.

Como há grande número de gestões, utiliza uma versão modificada da função de
páginas definida em `util/util.py`. Não pode utilizar a versão exata pois a
apresentação de informações requer uma alteração antes de disponibilizar a
página.

### Configuração do site Django

Adicione na raiz do projeto Django (`django-site/djangosite/`) o arquivo
`config.json`:

```javascript
{
    "SECRET_KEY": "",

    "DEBUG": true,
    "ALLOWED_HOSTS": [
        "*"
    ],

    "CAPTCHA_SECRET_KEY": "",
    "CAPTCHA_SITE_KEY": "",

    "EMAIL_HOST": "",
    "EMAIL_PORT": 0,
    "EMAIL_HOST_USER": "",
    "EMAIL_HOST_PASSWORD": "",
    "EMAIL_USE_TLS": false,
    "EMAIL_USE_SSL": false,

    "EMAIL_CONTATO_REMETENTE": "caco@ic.unicamp.br",
    "EMAIL_CONTATO_DISPLAY": "caco@ic.unicamp.br",
    "EMAIL_CONTATO_DESTINATARIO": [
        "caco@ic.unicamp.br"
    ]
}
```

E configure corretamente os valores. É necessário configurar o ReCaptcha e um
servidor de e-mail para a página de contato.

| Configuração | Significado |
| ------------ | ----------- |
| `SECRET_KEY` | Chave de segurança utilizada internamente pelo Django. Deve ser uma grande string e deve ser secreta |
| `DEBUG` | Valor de true ou false, define diversos parâmetros no servidor. NÃO deve ser true em produção |
| `ALLOWED_HOSTS` | Lista de _hosts_ aceitos para respondermos à requisição HTTP |
| `CAPTCHA_SECRET_KEY`, `CAPTCHA_SITE_KEY` | Chave privada e pública respectivamente do ReCaptcha (página de contato) |
| `EMAIL_CONTATO_DESTINATARIO` | Define a lista de e-mails que receberá os contatos do site |
| `EMAIL_CONTATO_REMETENTE` | Define qual será o remetente do e-mail que será enviado à lista `EMAIL_CONTATO_DESTINATARIO` |
| `EMAIL_CONTATO_DISPLAY` | Define qual e-mail (único) da gestão que aparecerá na página de contato em caso de falhas no site ou no ReCaptcha |
| `EMAIL_*` | Configurações de e-mail para utilizarmos na página de contato principalmente |

Para explicar melhor as diferentes configurações de `EMAIL_CONTATO_*`, vamos
supor que alguém preencha o formulário de contato no site. As informações desse
formulário serão enviadas em um e-mail. O destinatário do e-mail será a lista
`EMAIL_CONTATO_DESTINATARIO`, o remetente será `EMAIL_CONTATO_REMETENTE`.


## Estrutura do site (páginas, design)

Usamos [Bootstrap](https://getbootstrap.com/) (pretendia utilizar _material
design_ do Google, mas a documentação para web é terrível) construindo a página
de maneira genérica na pasta `bootstrap` e alterando-a para os parâmetros
genéricos de Django na pasta do projeto.

### Configurando com `npm`

Instalamos os pré-requisitos utilizando `npm` (gerenciador de pacotes
JavaScript), que irá identificar o arquivo do projeto `package.json`:

```
§ cd bootstrap/
§ npm install
```

### Modificando o projeto

Para modificar e testar essas alterações, utilizamos o `webpack-dev-server`, que
irá servir os arquivos compilados:

```
§ npm start
```

### Construindo arquivos estáticos

Após modificar os arquivos `app.js`, `app.scss`, utilizamos o comando que irá
construir na pasta `build/` os arquivos finais `bundle.js` e `bundle.css`:

```
§ npm run build
```

Agora colocamos esses arquivos na pasta que será servida pelo Django:
`django-site/djangosite/static` e utilizamos o comando para reorganizar os
arquivos estáticos:

```
§ python manage.py collectstatic
```


## Referências

Além das referências que usei que foram mencionadas pela descrição do sistema e
documentação de serviços utilizados (Django, Docker), utilizei estes guias:

[Antigo setup do site do CACo](https://github.com/cacounicamp/Site)

[Setting up Django and your web server with uWSGI and nginx](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

[How to Set Up Free SSL Certificates from Let's Encrypt using Docker and Nginx](https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx)
