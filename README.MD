# CACo-site

Este é um repositório da segunda versão para o site do CACo. O motivo de existir
uma segunda versão é, além de querer aprender a utilizar servidores web e a
framework Django, padronizar o site (diminuindo a quantidade de páginas
"jogadas", _features_ ainda não implementadas completamente), melhorar a
qualidade do que já existe (permitir envio de imagens nas páginas sem precisar
hospedar externamente, lista de membros que permite _reset_ fácil, avisando
todos os membros devidamente) e atualizar as versões do que já era utilizado
(utilizando os _rewrites_ de Bootstrap e de Django, que melhoraram muita coisa).

Por questão de legibilidade, não me preocupei em utilizar gêneros neutros em
variáveis dentro do código. Porém esse assunto é de extrema importância e DEVE
ser levado em consideração enquanto o conteúdo facilmente visível ao público do
site é reescrito.


## Guia rápido de instalação

O guia rápido pode ser encontrado [aqui](GUIA-RAPIDO.MD), utilizando
[Ubuntu](https://ubuntu.com) para configuração.

No entanto, para **desenvolvimento** e **configuração**, é necessário entender
toda a estrutura, descrita neste arquivo.


## Estrutura do servidor

Aqui será descrito quais programas utilizamos e de que forma são conectados.

O [nginx](https://www.nginx.com/) (pronunciado _engine x_) é um servidor web de
alta performance. Será utilizado para servir arquivos estáticos e redirecionar
pedidos "dinâmicos" ao [Django](https://www.djangoproject.com/) através do
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) (nginx <-> uWSGI <->
Django).

O banco de dados utilizado é [PostgreSQL](https://www.postgresql.org/) e se
conectará ao Django diretamente (django <-> banco de dados). Para isso,
utilizamos o pacote psycopg2-binary de Python, pois Django não oferece um
conector para PostgreSQL por padrão.

Antigamente utilizávamos Docker para organizar o servidor. Ele tem seus
benefícios, mas, da maneira como ocorria a aplicação e manutenção do site no
centro acadêmico, esses benefícios se perdiam e existia apenas a inconveniência
de uma ferramenta a mais para manusear. Então, com essa reescrita, resolvi
eliminar e tornar a manutenção mais fácil e automatizada (já que Docker
dificulta, por exemplo, renovar os certificados).

### Estrutura do servidor HTTP(S)

O site pode ser servido em 2 esquemas:
* HTTP (sem a _layer_ de segurança),
* HTTPS (segura, um pouco mais lenta).

Para HTTPS, usamos o serviço do [Let's Encrypt](https://letsencrypt.org/). Na
primeira execução, é necessário pedir certificados e comprovar que temos
controle do domínio (nginx irá servir um arquivo com um código que nos será dado
através do [certbot](https://certbot.eff.org/), um programa que gerencia os
certificados).

Após a aquisição inicial dos certificados, o `certbot` deve ser executado
periodicamente para renovar os certificados (Let's Encrypt nos dá certificados
que expiram em 3 meses). O `certbot` já reinicia o nginx para servir os novos
certificados, então um script que executa a cada hora é mais do que suficiente.

Para HTTP, não precisamos de certificados, então basta configurar o nginx.

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

##### Arquivo de configuração

Para segurança do site, guardamos informações e opções importantes em um arquivo
de configurações `django-site/djangosite/config.json`.

Note que é necessário configurar o
[ReCaptcha](https://www.google.com/recaptcha/admin) e um servidor de e-mail para
a página de contato. Então preencha corretamente este arquivo seguindo este
modelo:

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
    ],

    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "database_name",
            "USER": "",
            "PASSWORD": "",
            "HOST": "localhost",
            "PORT": "5432"
        }
    }
}
```

O significado de cada opção constam nessa tabela:

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
| `DATABASES` | Configuração para acessar o banco de dados, como [visto aqui](https://docs.djangoproject.com/en/dev/ref/settings/#databases), recomendamos utilizar um _socket_: basta colocar o caminho até o _socket_ (padrão em PostgreSQL é `/var/run/postgresql/`) em "`HOST`" |

Para explicar melhor as diferentes configurações de `EMAIL_CONTATO_*`, vamos
supor que alguém preencha o formulário de contato no site. As informações desse
formulário serão enviadas em um e-mail. O destinatário do e-mail será a lista
`EMAIL_CONTATO_DESTINATARIO`, o remetente será `EMAIL_CONTATO_REMETENTE`. O
e-mail de display `EMAIL_CONTATO_DISPLAY` será mostrado em algumas partes do
site.

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
que já é instalado através do `Pipfile` quando o _virtual environment_ é criado.
No entanto, a presença desse editor (e da página de administração do Django)
exigem a execução do comando `python manage.py collectstatic` antes de servir o
site.

Isso é preciso para que os arquivos do `CKEditor` (e a página de administração)
possam ser utilizados pelo navegador em produção - já que em desenvolvimento o
próprio Django ineficientemente serve os arquivos.

As páginas estáticas possuem o modelo `PaginaEstatica`, que é simplesmente uma
página com conteúdo de texto e imagens, editável através do `CKEditor`,
associado a um endereço que será servido se a opção `URL acessível` for `True`.
Essa opção é para podermos fazer páginas que **não** são servidas em si mas são
contidas em outras páginas. São elas:

| Endereço | Qual a intenção da página (do meu ponto de vista) |
|----------|---------------------------|
| `/atas/` | Explicar como funcionam as reuniões, assembleias e suas atas. |
| `/banco-de-provas/` | Falar um pouco de como isso auxilia os estudos e depende da boa vontade de todos. |
| `/banco-de-provas/contribuir/` | Explicar brevemente como preencher, talvez com uma imagem. |
| `/membros/vincular-se/` | Falar do por quê se vincular ao centro acadêmico. |
| `/membros/confirmar-token/` | Falar das consequências de se vincular, precisamos incentivar a presença das pessoas. |
| `/contato/` | Falar de como nos contatar, colocar referências para Facebook, dizer qual nosso e-mail e referênciar também a página de como participar. |
| `/contato/falha/` | Dizer para enviar um e-mail manualmente, nos avisar do erro e tentar outra rede social. **Essa customização substituirá a página padrão.** |
| `/contato/sucesso/` | Agradecer a mensagem, dizer que se não respondermos em algum tempo nos lembrar ou tentar outra rede social. **Essa customização substituirá a página padrão.** |
| `/representantes-discentes/` | Explicar como funciona a representação discente na Unicamp e o que o centro acadêmico faz sobre isso. |

A intenção de cada página estática que complementa os programas é justamente
explicar e incentivar participação. A minha visão em "intenção da página" pode
não refletir a visão de alguma futura gestão e isso é ok. :)

###### Observação:

As páginas são encontradas apenas após tentar todas as URLs do site através de
Django. Ou seja, ao encontramos uma resposta de erro 404 que irá ao usuário,
avaliamos se ela poderia ser substituída por uma página válida. Isso é uma
solução estranha, mas é a melhor maneira de servir páginas estáticas de forma
dinâmica e sem causar problemas com as __urlpatterns__ de Django.

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

Utiliza ReCaptcha para evitar spam.

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

##### `representantes_discentes`

_App_ que controla a lista de representantes discentes de cada
comissão/congregação/conselho dos principais institutos da Unicamp (ou os mais
relevantes à computação, IC e FEEC).

##### `membros`

_App_ que controla o cadastro e exibição de membros no site, permite o vínculo
e desvínculo de membros através de um e-mail institucional do IC da Unicamp.

A confirmação é feita através de um token aleatório de duração temporária, então
caso alguém digite algo errado, poderá se inscrever novamente após um período
determinado em `settings.py`.

Utiliza ReCaptcha para evitar spam.

##### `banco_de_provas`

_App_ que controla o cadastro e exibição de provas de anos anteriores para
auxiliar no estudo.

A versão anterior do site possuia um aplicativo que permitia entradas de texto
para todas as opções do formulário. Então a homogeneidade era dependente dos
membros do CACo que deveriam seguir as mesmas convenções, o que nem sempre
acontecia. A nova versão é bem mais complexa, porém a visualização fica
homogenea, bonita, é escalável e permite as disciplinas possuírem mais de um
código (por exemplo, MC302 que foi renomeada para MC322 ou a reestruturação
da árvore MCx58, que possui muitas siglas de assuntos parecidos no passado e que
podem ser juntados).

A parte ruim é que é um pouco confuso aos mantenedores, apesar de acreditar que
a interface para quem quer colaborar ficou mais intuitiva pois inclui várias
opções e não exige muita escrita, o que auxilia no processo de aprovação de uma
prova no site.

A estrutura contém vários modelos:
- **`Periodo`**: define o período em que a avaliação foi aplicada, como "1º
semestre", "2º semestre";
  - É recomendável que fique com números em primeiro caractere para manter a
ordem.
- **`TipoAvaliacao`**: define o tipo de avaliação, como "prova", "lista de
exercícios", "prova diurna", "prova vespertina";
  - É recomendável possuir uma resposta "não ser dizer ou não encontro opção"
para que o formulário de colaboração funcione bem, mas **NÃO** devemos deixar a
avaliação submetida com essa opção visível no banco de provas (os membros do
CACo devem encaixar a avaliação numa categoria que a representa).
- **`Disciplina`**: descreve apenas a existência de uma disciplina, não possui
código, nome. A descrição da disciplina é feita pela associação de uma instância
de `Disciplina` com um código de disciplina, objeto descrito abaixo. Por
exemplo, criamos a disciplina com identificador 32 (pode ser qualquer `id`),
associamos a essa disciplina os códigos "MC302" e "MC322" e agora temos a mesma
disciplina com 2 códigos válidos;
  - Se uma disciplina fica sem referência de nenhum código, ela é deletada
eventualmente;
  - Quando o próprio site cria uma disciplina (no caso em que o usuário digita
um código no banco de provas que está vazio), é necessário aprovar a disciplina
para que ela apareça no banco. Isso é necessário para que o mantenedor do site
confira se a disciplina não é alguma renomeada, mantendo as disciplinas "iguais"
juntas.
- **`CodigoDisciplina`**: é apenas um código ligado a uma disciplina. É esse
objeto que será utilizado bara buscar as avaliações quando busca-se pelo código.
O site irá procurar os códigos, que contém uma referência à `Disciplina`. Como
as avaliações também referenciam `Disciplina`, encontraremos as provas fazendo
essa associação.
- **`Avaliacao`**: guarda todas as informações de uma avaliação, como o objeto
`Disciplina`, `Periodo`, `TipoAvaliacao`;
  - Alguns itens são opcionais, porém os membros do CACo devem deixar a prova
  com o maior número de opções possíveis.

Utiliza ReCaptcha para evitar spam.

### Páginas HTML e design do site

Usamos [Bootstrap](https://getbootstrap.com/) (pretendia utilizar _material
design_ do Google, mas a documentação para web é terrível), construído na pasta
`bootstrap`, alterando alguns parâmetros para adequar-se melhor ao site do CACo,
como as cores do menu.

A construção é feita utilizando o gerenciador de pacotes JavaScript
[`npm`](https://www.npmjs.com/), que instalará os pacotes necessários localmente
e também provê uma interface de desenvolvimento através do `webpack-dev-server`.
Esse projeto `npm` é descrito no arquivo `package.json`.

As páginas HTML do site são descritas no projeto Django nas pastas `templates/`
de cada aplicativo. A base `layouts/base.html` contém todo o formato do site de
forma geral, enquanto os aplicativos descrevem as visões mais especializadas.

Utilizamos _templatetags_ para escrever HTML que envolvem modelos de aplicativos
específicos na base (por exemplo, o trecho da barra lateral que contém as atas
ou o próprio menu do site, que é dinâmico).

É recomendável utilizar ReCaptcha v3 em todo o site, porém adicionamos somente
nos trechos cruciais (`contato/` e `membros/`) para tornar o site mais leve e
responsivo.


## Referências

Além das referências que usei que foram mencionadas pela descrição do sistema e
documentação de serviços utilizados (Django, certbot, nginx), utilizei estes
guias durante o desenvolvimento. Alguns contém Docker pois por alguns meses
mantive o esquema utilizado no site anterior.

[Antigo setup do site do CACo](https://github.com/cacounicamp/Site)

[Setting up Django and your web server with uWSGI and nginx](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

[How to Set Up Free SSL Certificates from Let's Encrypt using Docker and Nginx](https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx)

Muitas pesquisas no Google e perguntas já respondidas no [Stack
Overflow](http://stackoverflow.com/).
