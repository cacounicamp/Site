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

Aqui será descrito quais programas utilizamos e de que forma são conectados.

O [nginx](https://www.nginx.com/) (pronunciado _engine x_) é um servidor web de
alta performance. Será utilizado para servir arquivos estáticos e redirecionar
pedidos "dinâmicos" ao [Django](https://www.djangoproject.com/) através do
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (nginx <-> uWSGI <->
Django).

O banco de dados utilizado é [postgresql](https://www.postgresql.org/) e se
conectará ao Django (django <-> banco de dados).

Tudo é organizado utilizando [Docker](https://www.docker.com/) através de uma
ferramenta `docker-compose`. Ela irá ler arquivos do formato
[`compose file`](https://docs.docker.com/compose/compose-file/), construir
as imagens e configurações dos _containers_ (é bem como o nome diz, é um espaço
individual para a aplicação) para serem executados posteriormente.

Ou seja, através do arquivo _compose_ do Docker, descrevemos todo o sistema:
como cada _container_ (que guarda apenas uma aplicação) comunica-se com outros
e com o mundo externo.

### Docker

O Docker utiliza imagens de sistemas estáveis e pré-configurados para garantir
que os seus programas executem em um ambiente previsível.

Se o Docker for configurado corretamente (no Arch, por exemplo, usando
`systemctl enable docker` para garantir que os serviços se iniciará com o
sistema) e, no caso de servir HTTPS, se o certificado foi obtido com sucesso, o
site deve se manter online sem qualquer interferência humana (requer um
detalhezinho rs).

No nosso projeto, há diferentes arquivos `docker-compose.yml`:
* um para servir o site perpetuamente apenas HTTP (`docker-compose-http.yml`),
* outro para aquisição única dos certificados HTTPS (`docker-compose-cert.yml`)
e
* outro para servir perpetuamente o site HTTPS (`docker-compose-https.yml`).

Independente do que escolher, a configuração do Docker é a mesma.

Para entender a estrutura dos _containers_, é necessário entender alguns
conceitos:
* _containers_ são imagens pré-configuradas para serem executadas em uma leve
camada de abstração (ao contrário de _virtual machines_ que simulam o sistema
operacional por inteiro, _containers_ utilizam o núcleo do sistema operacional
já executado na máquina),
* [Alpine](https://alpinelinux.org/) é uma distribuição Linux muito pequena e,
justamente por isso, é comum no Docker. As imagens dos _containers_ ocupam pouco
espaço após construídas. No entanto a distribuição não utiliza `libc`, uma
biblioteca comum que é usada por muitos programas, como o próprio uWSGI (então
uWSGI não pode estar em um _container_ cuja imagem-base é Alpine),
* Se um _container_ requer uma configuração prévia para funcionar (por exemplo,
instalação de pacotes Python, como o próprio Django), é necessário executar essa
configuração usando um arquivo
[`Dockerfile`](https://docs.docker.com/engine/reference/builder/) ao invés de
uma imagem base "pura".

A estrutura dos _containers_ de produção (não inclui o _container_ usado apenas
uma vez para aquisição dos certificados HTTPS - que falaremos no futuro) é, em
ordem crescente de "dependências":

#### `database`:
É baseado na imagem `postgres:alpine` em configuração padrão (definimos apenas
algumas [variáveis de
_environment_](https://wiki.archlinux.org/index.php/Environment_variables) para
tornar o usuário e senha comuns aos do Django e para fazemos a pasta do banco de
dados vir para a pasta raiz do projeto). A ligação entre o Django ao banco de
dados é feita através de um [Unix
socket](https://en.wikipedia.org/wiki/Unix_domain_socket) que é mais eficiente
do que conexões TCP. Esse arquivo socket ficará na raiz do projeto também.

#### `django-caco`:
Possui um `Dockerfile` para configuração do ambiente (que é baseado em uma
imagem do Python na distribuição debian), instalando Django, uWSGi e
as dependências do site.

Possui uma dependência (irá ligar apenas depois do _container_ `database`). A
porta 8080 é exposta ao Docker para que nginx possa conversar com o Django. Não
consegui ainda utilizar um Unix socket para isso infelizmente.

#### `servidor`:
É baseado na imagem `nginx:alpine`, mas possui um arquivo de configuração
(`Dockerfile`). Possui acesso aos arquivos estáticos do site (`/media` e
`/static` dentro do projeto Django). Depende de `django-caco` para inicializar e
possui uma ligação ao _container_ (através da porta 8080). As portas 80 (HTTP) e
443 (HTTPS) são abertas ao público (abertas ao computador, através do Docker).

#### `certbot_renew` (apenas HTTPS):
Executa apenas um comando e termina. Esse comando serve para renovar os
certificados HTTPS. Esses certificados serão utilizados pelo nginx, mantendo o
site encriptado e mais seguro. Caso não haja um _script_ que execute este
_container_ periodicamente, reiniciar a máquina antes do vencimento (3 meses) do
certificado do site já basta para renová-lo (já que esse _container_ executa
junto com os outros a cada reinicialização).

Após [instalar
e configurar](https://wiki.archlinux.org/index.php/Docker#Installation) `docker`
e `docker-compose`, para construirmos os _containers_ que necessitam de
configuração/preparo prévio (como os de Django e nginx), precisamos estar no
diretório que contém a configuração do `docker-compose` e executar:

```
§ ls
(...) docker-compose.yml (...)
§ docker-compose -f docker-compose.yml build
```

Para iniciar os _containers_, executamos:

```
§ docker-compose -f docker-compose.yml up
```

### Estrutura do servidor HTTPS

Usamos o serviço do [Let's Encrypt](https://letsencrypt.org/). Na primeira
execução, é necessário pedir certificados e comprovar que temos controle do
domínio (nginx irá servir um arquivo com um código que nos será dado através do
[certbot](https://certbot.eff.org/), um programa que gerencia os certificados).

Como usamos Docker, não é ideal usar os pacotes `docker` e `docker-nginx` do
Arch Linux, mas sim fazer um _container_ com alguma imagem `certbot` que seja
compatível com o nosso _container_ nginx. De tal forma que o servidor inteiro
permanece inalterado com relação aos certificados (todo o processo fica
encapsulado no Docker).

É por causa disso que há diversos `docker-compose.yml`, pois nginx está
configurado para 3 situações:
* servir HTTP,
* servir a comprovação de domínio, primeira aquisição de certificados e
* servir HTTPS após aquisição dos certificados.

Após a aquisição inicial dos certificados, o _container_ `certbot_renew`
(descrito em `docker-compose-https.yml`) deve ser executado periodicamente para
renovar os certificados (Let's Encrypt nos dá certificados que expiram em 3
meses). Como nginx possui acesso direto aos certificados, é possível atualizar
os certificados sem precisar reiniciar todos os serviços. O "detalhezinho rs"
escrito na seção Docker é esse: a única tarefa fora do Docker de que precisamos,
é necessário reiniciar o servidor a cada alguns meses.

### Django

Aqui será descrito a estrutura do site como um projeto Django, presente na pasta
`django-site/djangosite/`. Django utiliza uma estrutura MCV (_Model, Controller,
View_). Modelos controlam os objetos que serão trabalhados no controlador e
mostrados na _view_.

Django isola cada trecho do site em diversas aplicações, que possuem modelos,
controladores e _views_ individuais. Cada modelo poderá ser editado na páginas
de administrador quando configurado.

As páginas HTML são marcadas com trechos de uma "linguagem" implementada pelo
Django, processadas ao servir a página. Dessa forma, é possível exibir um
conteúdo dinâmico utilizando uma linguagem rápida de ser escrita.

As principais modificações que fizemos em comparação ao site anterior do CACo
foi transformar antes o que era exibido em páginas "estáticas" (estáticas pois o
conteúdo não se alterava senão através da página de administrador, de maneira
similar a algum site completamente estático, feito com vários arquivos HTML
editados apenas manualmente) em modelos e visualizações que homogenizam o site
e facilitam a inserção de dados.

Por exemplo, no site antigo, toda gestão antiga do CACo possuia páginas
estáticas, um link criado manualmente que não eram homogêneas (havia gestões em
que a tabela era formatada diferente de outras, por exemplo). Hoje isso virou um
app e basta ir à página de administrador e descrever a gestão, de maneira fácil
e simples, com uma visualização única para todas as gestões.

As aplicações do site em ordem aleatória são:

##### `paginas_estaticas`

As páginas estáticas são controladas pelo _app_ `paginas_estaticas`. Há modelos
que definem as coisas presentes na barra de menu e outros para cada página.

O menu é composto por:
* `ItemMenu` é um item do menu, filho ou não de um _dropdown_, com um índice que
indica qual sua posição na barra ou dentro do _dropdown_, um endereço para o
qual o item ao ser clicado redirecionará o usuário, um booleano para indicar se
o item estará visível ou não e outro para indicar se é clicável ou não.
* `MenuDropdown` é um `ItemMenu` que contém outros objetos `ItemMenu` em seu
interior e não possui endereço.

Para a composição das páginas, utilizamos o editor
[CKEditorWidget](https://github.com/django-ckeditor/django-ckeditor#widget),
que já é instalado através do `requirements.txt` quando o `docker-compose` cria
o _container_. No entanto, a presença desse editor (e da página de administração
do Django) exigem a execução do comando `python manage.py collectstatic` antes
de servir o site.

Isso é preciso para que os arquivos do `CKEditor` (e a página de administração)
possam ser utilizados pelo navegador em produção - já que em desenvolvimento o
próprio Django ineficientemente serve os arquivos.

As páginas estáticas possuem o modelo `PaginaEstatica`, que é simplesmente uma
página com conteúdo de texto e imagens, editável através do `CKEditor`,
associado a um endereço que será servido se a opção `URL acessível` for `True`.
Essa opção é para podermos fazer páginas que **não** são servidas mas são
contidas em outras páginas (por exemplo, para customizar a página
`contato/sucesso/` que aparece ao enviar um formulário de contato com sucesso,
assim não temos que editar diretamente o HTML e de maneira que as pessoas não
possam acessar o site `/contato/sucesso/`).

###### Observação:

Após a criação de uma página, é necessário reiniciar o servidor para que o novo
endereço seja servido corretamente.

##### `ouvidoria`

É um _app_ que controla todo contato feito através da página `contato/`, ele
enviará um e-mail para a própria gestão do CACo através de um e-mail da gestão
do CACo (configurado através do Django em `config.json`).

Um modelo que guardará as informações do pedido de contato, assim não perderemos
nenhuma informação caso o envio do e-mail falhe.

A página de contato pode ser associada a uma instância de `PaginaEstatica` (com
endereço `contato/`), dessa maneira, então, é possível adicionar/editar/remover
textos da página de contato facilmente, sem alterar o código fonte da página
através do servidor, alterando apenas o texto na página de administração.

Além da página de contato, devemos criar instâncias de `PaginaEstatica` para os
endereços `contato/sucesso/` e `contato/falha/` que aparecem respectivamente ao
tentar utilizar a página de contato obtendo sucesso e falha.

##### `atas`

_App_ que controla as atas de reunião e de assembleias. A página principal
(`atas/`) está ligada à página estática `atas/` para produzir uma página com
conteúdo dinâmico.

Há dois modelos: `AtaReuniao` e `AtaAssembleia`. As atas de assembleia podem ser
marcadas como deliberativas ou não. Já as de reunião, podem ser marcadas como
extraordinárias ou não. Ambas possuem conteúdo dinâmico, permitem envio de
arquivos e possuem um trecho sobre _highlights_, para atrair mais usuários à
leitura.

O _app_ ainda descreve o _templatetag_:

###### _templatetag atas_
Auxilia na fabricação da página de atas (há um HTML para os 2 tipos de atas,
esse _template_ possui funções que auxiliam em diferenciar essas atas) e também
processa as últimas atas para ficar ao lado direito do site (em todas as
páginas, através da página base do site) para fácil acesso.

###### Observação
Junto com `noticias`, `atas` utiliza o serviço de paginação (determinar números
de páginas) descrito em `util/util.py`.

##### `noticias`

_App_ controla as notícias do site. Contém a página raiz (`/`, a inicial). O
único modelo descrito é `Noticia`, que guarda o conteúdo (editável pelo
`CKEditor`), a data de criação e um resumo que aparecerá nas listagens de
notícias (página inicial, página `noticias/`). Não há nenhuma página estática
usada nas _views_ de notícias.

Para a _view_ de notícias e atas, temos o documento `util/util.py`, que conta o
número de itens e separa em páginas. O número de itens mostrado por página é
customizável em `settings.py`.

##### `gestoes`

_App_ controla o histórico de gestões do CACo. Ele existe (diferente da criação
de páginas estaticas manualmente que era feito nos anos anteriores) apenas para
uniformizar a apresentação de informações.

Como há grande número de gestões, utiliza uma versão modificada da função de
páginas definida em `util/util.py`. Não pode utilizar a versão exata pois a
apresentação de informações requer uma alteração antes de disponibilizar a
página.


## Referências

Além das referências que usei que foram mencionadas pela descrição do sistema e
documentação de serviços utilizados (Django, Docker), utilizei estes guias:

[Antigo setup do site do CACo](https://github.com/cacounicamp/Site)

[Setting up Django and your web server with uWSGI and nginx](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

[How to Set Up Free SSL Certificates from Let's Encrypt using Docker and Nginx](https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx)
