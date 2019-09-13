import re

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

Uma avaliação foi adicionada ao banco de provas do site. É necessário:
* revisar todas as informações;
* fazer as alterações necessárias;
* tornar a avaliação visível para ela aparecer aos usuários do site.

Informações da prova:
{info_prova}

Endereço para o arquivo NÃO APROVADO:
\t{url_arquivo}

Para alterar a situação da prova, entre no site de administração da prova no endereço a seguir:
\t{url_avaliacao}


Se não souber o que fazer com relação a "Disciplina" e "Código de disciplina", há um pequeno guia abaixo.

Para revisar a disciplina, você precisa entender o funcionamento do site. O site tenta determinar a disciplina baseado no código enviado no formulário de contribuição:
* se o código não foi registrado no passado, o site cria uma nova disciplina e associa o código preenchido no formulário a ela;
* se o código foi registrado no passado, o site apenas inclui a disciplina correspondente à prova.

Ou seja, há alguns casos:
* se digitaram errado, você precisa apagar a disciplina criada e atualizar a prova;
* se o código é um novo código para uma disciplina que foi RENOMEADA, você precisa apagar a disciplina criada pelo site e adicionar o código novo à disciplina do código antigo;
* se a prova é inédita, basta aprovar a disciplina;
* a prova está numa disciplina já existente e nada precisa ser feito sobre isso.

É um pouco confuso. Mas isso permite que você pesquise "MC322" e encontre provas de "MC302" (antigo nome da disciplina "Programação Orientada a Objetos").

Dito isso, os cuidados principais são:
* Conferir se o sistema associou a prova à disciplina correta;
* Conferir as informações do formulário, como tipo da prova, docente, semestre e ano;
* Aprovar a prova se o arquivo condiz com o que a descrição diz.

Tenham um excelente dia,
Centro acadêmico da computação
"""


re_codigo_disc = re.compile('[a-z]{1,2}\d{3}')
re_ano = re.compile('\d{4}')


def BancoDeProvasView(request):
    try:
        # Tentamos conseguir a página estática do banco de provas
        pagina = PaginaEstatica.objects.get(endereco='/banco-de-provas/')
    except ObjectDoesNotExist:
        pagina = None

    # Pegamos os dados da query
    busca = request.GET.get('busca')

    if busca is None:
        avaliacoes = None
    else:
        # Iniciamos a query
        query_final = Q()
        busca = busca.lower()

        # Iniciamos listas
        unmatched = []
        matches_codigos = []
        anos_matched = []

        # Separamos a busca em palavras
        for palavra in busca.replace(',', ' ').split():
            matched = False

            # Verificamos se há um código de disciplina
            match_codigo = re_codigo_disc.match(palavra)
            if match_codigo is not None:
                matches_codigos.append(match_codigo)
                matched = True

            # Verificamos se há anos
            match_ano = re_ano.match(palavra)
            if match_ano is not None:
                # Transformamos em inteiro
                anos_matched.append(int(match_ano.group(0)))
                matched = True

            # Conferimos se não houve matches (professores, tipo de prova)
            if not matched:
                unmatched.append(palavra)

        # Criamos lista vazia de disciplinas
        disciplinas = []
        # Buscamos todos os códigos de disciplinas
        for match_codigo in matches_codigos:
            # Buscamos a match como código
            codigos = CodigoDisciplina.objects.filter(codigo__iexact=match_codigo.group(0)).all()

            # Para cada código, adicionamos a lista se aprovada
            for codigo in codigos:
                # Conferimos se é aprovada e adicionamos à lista
                if codigo.disciplina.autorizada:
                    disciplinas.append(codigo.disciplina)

        # Buscamos as avaliações com essas disciplinas
        if len(disciplinas) > 0:
            query_final = Q(disciplina__in=disciplinas) & query_final

        # Procuramos pelo ano
        if len(anos_matched) > 0:
            query_final = Q(ano__in=anos_matched) & query_final

        # Buscamos professores e tipos de avaliação
        query_unmatched = Q()
        for palavra in unmatched:
            # Pesquisamos em cada categoria com OR
            query_unmatched = Q(tipo_avaliacao__nome__icontains=palavra) | \
                Q(docente__icontains=palavra) | \
                Q(periodo__nome__icontains=palavra) | \
                query_unmatched

        # Colocamos na query com AND
        query_final = query_unmatched & query_final

        # Buscamos as avaliações finalmente
        avaliacoes = Avaliacao.objects.filter(
            query_final,
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
        pagina = PaginaEstatica.objects.get(endereco='/banco-de-provas/contribuir/')
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
        codigo_string = form.cleaned_data['codigo_disciplina'].lower()
        docente = form.cleaned_data['docente'].lower()
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
                codigo=codigo_string.lower()
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

        # Produzimos um resumo para o e-mail
        if docente is None or len(docente) == 0:
            nome_docente = 'desconhecido'
        else:
            nome_docente = docente

        if quantificador is None:
            nome_quantificador = ''
        else:
            nome_quantificador = str(quantificador)

        if (periodo is None and ano is None):
            nome_periodo = 'desconhecido'
        elif (periodo is None and ano is not None):
            nome_periodo = 'semestre desconhecido de ' + str(ano)
        elif (periodo is not None and ano is None):
            nome_periodo = periodo.nome + ' de ano desconhecido'
        else:
            nome_periodo = periodo.nome + ' de ' + str(ano)

        informacoes = [
            '\tDisciplina: ' + codigo_string.upper(),
            '\tDocente: ' + nome_docente,
            '\tTipo: ' + tipo_avaliacao.nome + ' ' + nome_quantificador,
            '\tPeríodo: ' + nome_periodo,
            '\tPossui resolução? ' + ('Sim' if possui_resolucao else 'Não'),
        ]
        informacao_prova = '\n'.join(informacoes)

        # Agora mandamos um e-mail
        send_mail(
            subject=settings.EMAIL_ASSUNTO_BASE.format(
                assunto='Avaliação pendente no banco de provas'
            ),
            message=EMAIL_MENSAGEM_AVALIACOES_ADICIONADA.format(
                url_avaliacao=request.build_absolute_uri(reverse(
                    'admin:banco_de_provas_avaliacao_change',
                    args=[avaliacao.id]
                )),
                url_arquivo=request.build_absolute_uri(avaliacao.arquivo.url),
                info_prova=informacao_prova
            ),
            from_email=settings.EMAIL_CONTATO_REMETENTE,
            recipient_list=settings.EMAIL_CONTATO_DESTINATARIO,
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
