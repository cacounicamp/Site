import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone


class Membro(models.Model):
    # Nome do membro
    nome = models.CharField(max_length=settings.MAX_LENGTH_NOME, null=False, blank=False)

    # Registro acadêmico do membro
    registro_academico = models.PositiveIntegerField(primary_key=True, null=False, blank=False)

    # E-mail institucional do membro
    email_institucional = models.EmailField(max_length=settings.MAX_LENGTH_EMAIL, null=False, blank=False)
    # E-mail do membro
    email = models.EmailField(max_length=settings.MAX_LENGTH_EMAIL, null=False, blank=True)

    # Ano de ingresso do membro
    ano_ingresso = models.PositiveIntegerField(null=False, blank=False)
    # Curso do membro
    curso = models.CharField(max_length=settings.MAX_LENGTH_CURSOS, null=False, blank=False, choices=settings.CURSOS)

    # Data de confirmação do membro
    data_confirmacao = models.DateTimeField(default=None, null=True, blank=False)

    #
    #   INFORMAÇÕES SOBRE CONFIRMAÇÃO
    #

    # Data de registro do membro (a data em que o token foi gerado)
    token_vencimento = models.DateTimeField(default=None, null=True, blank=True)

    # Token de confirmação (gerado na data 'data_registro')
    token_uuid = models.UUIDField(default=None, null=True, blank=True)

    # Ação desse token
    ACOES = (
        ('REG', 'Confirmação para registrar membro'),
        ('DEL', 'Confirmação para deletar membro'),
    )
    token_acao = models.CharField(max_length=4, default=None, null=True, blank=True, choices=ACOES)

    def membro_confirmado(self):
        # O membro é dito confirmado quando a data de confirmação não é nula
        return self.data_confirmacao is not None

    def membros_confirmados():
        # Busca todos os membos cuja data de confirmação não é nula
        return Membro.objects.filter(data_confirmacao__isnull=False)

    def possui_token_ativo(self):
        # O membro possui token ativo quando o token existe e não está vencido
        return (self.token_acao is not None and timezone.now() < self.token_vencimento)

    def apagar_token(self):
        # Apagamos o token anterior
        self.token_uuid = None
        self.token_acao = None
        self.token_vencimento = None

        # Salvamos o membro
        self.save()

    def registrar_token(self, acao):
        # Conferimos se há um token ativo
        if self.possui_token_ativo():
            return False

        # Conferimos se a ação é não válida
        if acao not in dict(Membro.ACOES):
            return False

        # Criamos um token
        self.token_uuid = uuid.uuid4()
        self.token_acao = acao
        self.token_vencimento = timezone.now() + settings.TEMPO_CONFIRMACAO_MEMBROS

        # Salvamos o modelo
        self.save()

        # Retornamos sucesso
        return True

    def __str__(self):
        return '{membro.nome} ({membro.registro_academico}, e-mail pessoal: "{membro.email}", {membro.curso} {membro.ano_ingresso}), {status}'.format(membro=self, status='confirmado em {0}'.format(self.data_confirmacao) if self.data_confirmacao is not None else 'não confirmado')

    class Meta:
        verbose_name = "membro do centro acadêmico"
        verbose_name_plural = "membros do centro acadêmico"
        ordering = ['registro_academico']
