# alpine e slim são incompatíveis com uwsgi
FROM python:3.7.1

# Definimos o WORKDIR como pedido na configuração do docker para python
WORKDIR /djangosite

# Montamos o arquivo requirements.txt e uwsgi.ini no WORKDIR
# Observação: . é em relação de onde Dockerfile está e não de onde o comando
# `docker-compose` build é utilizado
COPY ./requirements.txt /djangosite

# Instalamos os pacotes requeridos
RUN python3 -m pip install -r requirements.txt

# Configuramos o uwsgi usando o nosso arquivo .ini
CMD ["uwsgi", "--ini", "/djangosite/uwsgi.ini"]
