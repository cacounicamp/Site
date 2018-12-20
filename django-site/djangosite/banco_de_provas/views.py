from django.http import Http404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from paginas_estaticas.models import PaginaEstatica
from util import util

from .models import Avaliacao, CodigoDisciplina, Disciplina, Periodo, TipoAvaliacao
from .forms import FormAvaliacao


EMAIL_MENSAGEM_AVALIACOES_ADICIONADA = """Olá,

Uma avaliação foi adicionada ao banco de provas do site. É necessário revisar todas as informações, fazer as alterações necessárias e tornar a avaliação visível para ela aparecer aos usuários do site.

O site tenta determinar a disciplina baseado no código. Se o código não foi registrado no passado, o site cria uma nova disciplina e associa o código preenchido no formulário a ela.
Vamos supor que no banco de provas haja apenas provas de MC302 e alguém acaba de adicionar a prova de MC322 (novo código da disciplina). O site criará a disciplina MC322, mas você deve apagar essa disciplina e associar a prova à disciplina MC302. Depois disso, adicionar um novo código à disciplina MC302, o código "MC322".
É um pouco confuso. Mas o que vocês devem fazer é apenas manter as disciplinas iguais juntas e permitir a criação de novas se não há nenhuma disciplina equivalente.

Dito isso, os cuidados principais são:
* Conferir se o sistema associou a prova à uma disciplina já existente ou se criou uma nova disciplina. Em ambos os casos, conferir se está corretamente configurado;
* Conferir as informações do formulário, como docente, semestre e ano;
* Aprovar a prova se o arquivo condiz com o que ela é.

Página de administrador para a prova inserida: {url_avaliacao}

Atenciosamente,
Centro acadêmico da computação
""".encode()


def BancoDeProvasView(request):
    try:
        # Tentamos conseguir a página estática do banco de provas
        pagina = PaginaEstatica.objects.get(endereco='banco-de-provas/')
    except ObjectDoesNotExist:
        pagina = None

    # Pegamos os dados da query
    busca = request.GET.get('busca')

    if busca is None:
        avaliacoes = None
    else:
        # Buscamos todos os códigos de disciplinas
        disciplinas = []
        codigos = CodigoDisciplina.objects.filter(codigo__icontains=busca).all()
        for codigo in codigos:
            # Colocamos na lista de disciplinas apenas as que foram aprovadas
            # e não automaticamente criadas
            if codigo.disciplina.autorizada:
                disciplinas.append(codigo.disciplina)

        # Buscamos as avaliações com qualquer combinação desses dados
        avaliacoes = Avaliacao.objects.filter(
            Q(disciplina__in=disciplinas) | \
            Q(docente__icontains=busca) | \
            Q(tipo_avaliacao__nome__icontains=busca) | \
            Q(quantificador_avaliacao__icontains=busca) | \
            Q(periodo__nome__icontains=busca) | \
            Q(ano__icontains=busca),
            # Filtramos as avaliações visíveis
            visivel=True,
            disciplina__autorizada=True
        ).all()[0:settings.MAX_LENGTH_MAX_AVALIACOES]

    # Servimos a página
    context = {
        'pagina': pagina,
        'busca': busca,
        'avaliacoes': avaliacoes,
    }
    return render(request, 'banco_de_provas.html', context=context)


def SubmeterProvaView(request):
    # Se não estamos em POST, temos que servir a página

    try:
        # Tentamos conseguir a página estática para contribuições
        pagina = PaginaEstatica.objects.get(endereco='banco-de-provas/contribuir/')
    except ObjectDoesNotExist:
        pagina = None

    # Inicializamos contexto
    context = {
        'captcha_site_key': settings.CAPTCHA_SITE_KEY,
        'pagina': pagina,
    }

    # Verificamos se estamos recebendo informação ou temos que servir o
    # formulário
    if request.method != 'POST':

        # Criamos o formulário
        context['form'] = FormAvaliacao()

        # Apenas servimos
        return render(request, 'contribuir_formulario.html', context=context)

    else:

        # Se estamos em POST, estamos recebendo o formulário
        form = FormAvaliacao(request.POST, request.FILES)
        context['form'] = form

        # Conferimos o Recaptcha
        if not util.recaptcha_valido(request):
            # Avisamos o usuário
            messages.add_message(
                request, messages.SUCCESS,
                'Recaptcha inválido! Atualize a página e tente novamente mais tarde.',
                extra_tags='danger'
            )

            # Redirecionamos à página de contribuição novamente
            return redirect(reverse('banco-de-provas/contribuir/'))

        # Verificamos se todos os dados respeitam o formulário
        if not form.is_valid():

            # Caso o formulário não for preenchido corretamente, avisamos o
            # usuário
            form.add_error(
                None,
                'O formulário não foi preenchido corretamente!'
            )

            # Redirecionamos ao formulário
            return render(request, 'contribuir_formulario.html', context=context)

        # Obtemos as informações limpas do formulário
        # Observação: os tipos são mantidos, Django é excelente <3
        codigo_string = form.cleaned_data['codigo_disciplina']
        docente = form.cleaned_data['docente']
        # Tipo de avaliação deve possuir uma opção chave para os formulários
        # como "Não sei dizer ou não encontrei o tipo que procuro"
        tipo_avaliacao = form.cleaned_data['tipo_avaliacao']
        quantificador = form.cleaned_data['quantificador']
        periodo = form.cleaned_data['periodo']
        ano = form.cleaned_data['ano']
        possui_resolucao = form.cleaned_data['possui_resolucao']
        arquivo = form.cleaned_data['arquivo']

        # Temos que determinar em qual disciplina colocamos. Fazemos isso pelo
        # nome
        try:
            codigo_disciplina = CodigoDisciplina.objects.get(
                codigo=codigo_string
            )

            # Se o código já foi registrado, basta pegar a disciplina
            # correspondente
            disciplina = codigo_disciplina.disciplina
        except ObjectDoesNotExist:
            # Se não há código registrado, precisamos criar uma nova

            # Criamos uma nova disciplina não autorizada
            disciplina = Disciplina(
                autorizada=False
            )
            disciplina.save()

            # Agora criamos um nome para a disciplina
            # Consideramos o nome como o mais atualizado
            codigo_disciplina = CodigoDisciplina(
                disciplina=disciplina,
                nome_atualizado=True,
                codigo=codigo_string.lower(),

            )
            codigo_disciplina.save()

        # Agora que já temos a disciplina, que era o mais difícil, basta
        # inserir numa avaliação
        avaliacao = Avaliacao(
            disciplina=disciplina,
            docente=docente,
            tipo_avaliacao=tipo_avaliacao,
            quantificador_avaliacao=quantificador,
            periodo=periodo, # aceita None (período é uma instância mesmo)
            ano=ano,
            possui_resolucao=possui_resolucao,
            arquivo=arquivo
        )
        avaliacao.save()

        # Agora mandamos um e-mail
        send_mail(
            subject=settings.EMAIL_ASSUNTO_BASE.format(
                assunto='Avaliação pendente no banco de provas'
            ),
            message=EMAIL_MENSAGEM_AVALIACOES_ADICIONADA.format(
                url_avaliacao=request.build_absolute_uri(reverse(
                    'admin:banco_de_provas_avaliacao_change',
                    args=[avaliacao.id]
                ))
            ),
            from_email=settings.EMAIL_CONTATO_REMETENTE,
            recipient_list=[settings.EMAIL_CONTATO_DESTINATARIO],
            fail_silently=True
        )

        # Falamos ao usuário que o formulário foi enviado com sucesso e que
        # avaliaremos
        messages.add_message(
            request, messages.SUCCESS,
            'Avaliação enviada! Membros do centro acadêmico avaliarão e logo a prova estará disponível. Se quiser, nos envie outra avaliação!',
            extra_tags='success'
        )

        # Mostramos a página do formulário
        return render(request, 'contribuir_formulario.html', context=context)
