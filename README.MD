# caco-site

Este é um repositório da segunda versão para o site do CACo. O motivo de existir
uma segunda versão é eu querer aprender a utilizar servidores web, framework
Django e Docker.

Utilizei neste guia [Arch
Linux](https://wiki.archlinux.org/index.php/Arch_Linux) e seu sistema de
pacotes.


## Estrutura básica

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
$ ls
(...) docker-compose.yml (...)
$ docker-compose -f docker-compose.yml build
```

E, para iniciar os _containers_:

```
$ docker-compose -f docker-compose.yml up
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


## Configurando HTTPS

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


## Configurando o Docker

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

### `database`:
É baseado na imagem `postgres:alpine` em configuração padrão (definimos apenas
algumas [variáveis de
_environment_](https://wiki.archlinux.org/index.php/Environment_variables) para
tornar o usuário e senha comuns ao Django e fazemos a pasta do banco de dados
vir para a pasta raiz do projeto). A porta padrão `postgres` 5432 é exposta ao
Docker (e não à máquina).

### `django-caco`:
Possui um `Dockerfile` para configuração do ambiente (que é baseado em uma
imagem do Python na distribuição debian), instalando Django, uWSGi e
dependências do site.
Possui uma dependência (irá ligar apenas depois do `database` estar ligado) e
ligação com o _container_ `database` para poder acessar o banco de dados. A
porta 8080 é exposta ao Docker para que nginx possa conversar com o Django.

### `servidor`:
É baseado na imagem `nginx:alpine`, mas possui arquivo de configuração. Tem
acesso aos arquivos estáticos do site (`/media` e `/static`) e depende de
`django-caco` e possui uma ligação ao _container_ (aquela porta 8080). As portas
80 e 443 são abertas ao público.

### `certbot_renew` (apenas HTTPS):
Executa apenas um comando e termina. É para renovar os certificados HTTPS. Esses
certificados serão utilizados pelo nginx, mantendo o site encriptado e mais
seguro. Caso não haja um _script_ que execute este _container_ periodicamente,
reiniciar a máquina antes dos 3 meses do certificado expirar basta.

## Referências

Além das referências que usei que foram mencionadas pela descrição do sistema,
utilizei estes guias:

[Antigo setup do site do CACo](https://github.com/cacounicamp/Site)

[Setting up Django and your web server with uWSGI and nginx](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

[How to Set Up Free SSL Certificates from Let's Encrypt using Docker and Nginx](https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx)
