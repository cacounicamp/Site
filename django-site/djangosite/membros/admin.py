import csv

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required

from .models import Membro
from .forms import FormularioAdminResetar


class MembroAdmin(admin.ModelAdmin):
    list_display = ('registro_academico', 'data_confirmacao', 'nome', 'email', 'curso', 'ano_ingresso')
    search_fields = ['registro_academico', 'nome', 'email', 'curso', 'ano_ingresso']
    # Alteramos a HTML padrão do admin
    change_list_template = 'membros_admin.html'
    # Torna o sistema bastante rígido a violações do estatuto
    readonly_fields = ['token_acao', 'token_uuid', 'token_vencimento', 'data_confirmacao']

    def get_urls(self):
        urls = super().get_urls()
        # Adicionamos nossa URL
        customizacoes = [
            path('resetar-lista/', self.ResetView),
            path('lista-de-membros.csv', self.ListaMembrosCSVView),
        ]
        return customizacoes + urls

    @permission_required('resetar_lista')
    def ResetView(self, request):
        if request.method == 'POST':
            form = FormularioAdminResetar(request.POST)

            # Conferimos se não devemos resetar
            if (not form.is_valid() or form.cleaned_data['resetar'] is False):
                # Mandamos um aviso de erro
                messages.error(request, "Erro! Formulário inválido ou reset cancelado.")
                # Retornamos à raiz
                return redirect(reverse('admin:membros_membro_changelist'))

            # Removemos todos os membros confirmados (mesmo que tenham token ativo)
            num_membros = Membro.membros_confirmados().delete()[0]
            # Avisamos o administrador
            self.message_user(request, "{0} membros foram removidos. O CACo deve avisar por e-mail que a lista foi resetada.".format(num_membros))

            # Retornamos ao fim
            return redirect(reverse('admin:membros_membro_changelist'))
        else:
            # Pegamos o context base
            context = dict(self.admin_site.each_context(request))

            # Adicionamos nossos itens
            context['title'] = 'Resetar lista de membros'
            form = FormularioAdminResetar()
            context['form'] = form

            # Produzimos a página
            return TemplateResponse(request, "membros_admin_resetar.html", context)

    @permission_required('ver_lista')
    def ListaMembrosCSVView(self, request):
        # Pegamos todos os membros confirmados
        membros = Membro.membros_confirmados().all()

        # Criamos uma resposta com arquivo CSV
        resposta = HttpResponse(content_type='text/csv')
        resposta['Content-Disposition'] = 'attachment; filename="membros.csv"'

        # Fazemos um CSV com todos os valores
        csv_membros = csv.writer(resposta)
        csv_membros.write_row([
            'nome',
            'registro_academico',
            'email_institucional',
            'email',
            'ano_ingresso',
            'curso',
            'data_confirmacao'
        ])
        # Para cada membro...
        for membro in membros:
            csv_membros.write_row([
                membro.nome,
                membro.registro_academico,
                membro.email_institucional,
                membro.email,
                membro.ano_ingresso,
                membro.curso,
                membro.data_confirmacao
            ])

        # Retornamos
        return resposta

    class Meta:
        permissions = [('resetar_lista', 'ver_lista')]


admin.site.register(Membro, MembroAdmin)
