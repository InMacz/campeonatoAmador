from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ArbitroForm, GolForm, JogadorForm, PartidaForm, TimeForm
from .models import Arbitro, Gol, Jogador, Partida, Time


# ---------------------------------------------------------------------------
# Níveis de acesso
# ---------------------------------------------------------------------------
# user  -> qualquer usuário logado: só consegue VER as listas e os detalhes
# admin -> usuário com is_staff=True: também pode cadastrar, editar e excluir

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    # LoginRequiredMixin: quem não está logado é mandado para a tela de login
    # UserPassesTestMixin: quem está logado mas não passa no test_func recebe erro 403 (acesso negado)
    def test_func(self):
        return self.request.user.is_staff



# ---------------------------------------------------------------------------
# Cadastro de usuário comum (nível "user")
# ---------------------------------------------------------------------------

class CadastroUsuarioView(CreateView):
    # UserCreationForm é o formulário pronto do Django (usuário + senha + confirmação).
    # Todo usuário criado por aqui é comum (is_staff=False), ou seja, só visualiza.
    form_class = UserCreationForm
    template_name = "campeonato/cadastro_usuario.html"
    success_url = reverse_lazy("login")
    extra_context = {"tituloPagina": "Criar conta", "h1": "Criar conta", "btn": "Criar conta"}


# ---------------------------------------------------------------------------
# Partidas
# ---------------------------------------------------------------------------

class PartidaListView(LoginRequiredMixin, ListView):
    model = Partida
    template_name = "campeonato/partida_lista.html"
    context_object_name = "partidas"  # nome da variável usada no template
    extra_context = {"tituloPagina": "Partidas", "h1": "Partidas"}

    def get_queryset(self):
        partidas = Partida.objects.select_related("timeCasa", "timeFora", "arbitro").order_by("-data")

        # filtros que chegam pela URL (?busca=...&time=...&arbitro=...)
        busca = self.request.GET.get("busca", "")
        time = self.request.GET.get("time", "")
        arbitro = self.request.GET.get("arbitro", "")

        if busca:
            # Q permite usar OU: a partida aparece se o time da casa OU o visitante OU o local tiver o texto buscado
            partidas = partidas.filter(
                Q(timeCasa__nome__icontains=busca)
                | Q(timeFora__nome__icontains=busca)
                | Q(local__icontains=busca)
            )
        if time:
            # o time pode ter jogado em casa ou fora
            partidas = partidas.filter(Q(timeCasa_id=time) | Q(timeFora_id=time))
        if arbitro:
            partidas = partidas.filter(arbitro_id=arbitro)
        return partidas

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busca"] = self.request.GET.get("busca", "")
        contexto["filtroTime"] = self.request.GET.get("time", "")
        contexto["filtroArbitro"] = self.request.GET.get("arbitro", "")
        contexto["filtrando"] = any([contexto["busca"], contexto["filtroTime"], contexto["filtroArbitro"]])
        contexto["times"] = Time.objects.order_by("nome")  # opções do select de time
        contexto["arbitros"] = Arbitro.objects.order_by("nome")  # opções do select de árbitro
        return contexto


class PartidaDetailView(LoginRequiredMixin, DetailView):
    # mostra a partida e a lista de gols (o título e o placar ficam no próprio template)
    model = Partida
    template_name = "campeonato/partida_detalhe.html"


class PartidaCreateView(AdminRequiredMixin, CreateView):
    model = Partida
    form_class = PartidaForm
    template_name = "campeonato/partida_form.html"
    extra_context = {"tituloPagina": "Cadastrar Partida", "h1": "Cadastrar Partida", "btn": "Cadastrar"}

    def get_success_url(self):
        # depois de cadastrar, vai direto para o detalhe para adicionar os gols
        return reverse("detalhePartida", kwargs={"pk": self.object.pk})


class PartidaUpdateView(AdminRequiredMixin, UpdateView):
    model = Partida
    form_class = PartidaForm
    template_name = "campeonato/partida_form.html"
    extra_context = {"tituloPagina": "Editar Partida", "h1": "Editar Partida", "btn": "Salvar"}

    def get_success_url(self):
        return reverse("detalhePartida", kwargs={"pk": self.object.pk})


class PartidaDeleteView(AdminRequiredMixin, DeleteView):
    model = Partida
    template_name = "campeonato/partida_exclusao.html"
    success_url = reverse_lazy("listaPartidas")
    extra_context = {"tituloPagina": "Excluir Partida", "h1": "Excluir Partida", "btn": "Confirmar Exclusão"}


# ---------------------------------------------------------------------------
# Gols (tabela do meio da relação N:N entre Partida e Jogador)
# ---------------------------------------------------------------------------

class GolCreateView(AdminRequiredMixin, CreateView):
    # a URL é partidas/<pk>/gols/adicionar/, então o pk na URL é o da PARTIDA
    model = Gol
    form_class = GolForm
    template_name = "campeonato/gol_form.html"
    extra_context = {"tituloPagina": "Adicionar Gol", "h1": "Adicionar Gol", "btn": "Adicionar"}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        partida = get_object_or_404(Partida, pk=self.kwargs["pk"])
        # regra: no campo "jogador" só aparecem (e só são aceitos) jogadores dos dois times da partida
        form.fields["jogador"].queryset = Jogador.objects.filter(time__in=[partida.timeCasa, partida.timeFora])
        return form

    def form_valid(self, form):
        # liga o gol à partida da URL antes de salvar
        form.instance.partida_id = self.kwargs["pk"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("detalhePartida", kwargs={"pk": self.kwargs["pk"]})


class GolDeleteView(AdminRequiredMixin, DeleteView):
    model = Gol
    template_name = "campeonato/gol_exclusao.html"
    extra_context = {"tituloPagina": "Excluir Gol", "h1": "Excluir Gol", "btn": "Confirmar Exclusão"}

    def get_success_url(self):
        # depois de excluir, volta para a partida do gol
        return reverse("detalhePartida", kwargs={"pk": self.object.partida.pk})


# ---------------------------------------------------------------------------
# Times
# ---------------------------------------------------------------------------

class TimeListView(LoginRequiredMixin, ListView):
    model = Time
    template_name = "campeonato/time_lista.html"
    context_object_name = "times"
    extra_context = {"tituloPagina": "Times", "h1": "Times"}

    def get_queryset(self):
        times = Time.objects.order_by("nome")
        busca = self.request.GET.get("busca", "")
        if busca:
            times = times.filter(Q(nome__icontains=busca) | Q(bairro__icontains=busca))
        return times

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busca"] = self.request.GET.get("busca", "")
        return contexto


class TimeCreateView(AdminRequiredMixin, CreateView):
    model = Time
    form_class = TimeForm
    template_name = "campeonato/time_form.html"
    success_url = reverse_lazy("listaTimes")
    extra_context = {"tituloPagina": "Cadastrar Time", "h1": "Cadastrar Time", "btn": "Cadastrar"}


class TimeUpdateView(AdminRequiredMixin, UpdateView):
    model = Time
    form_class = TimeForm
    template_name = "campeonato/time_form.html"
    success_url = reverse_lazy("listaTimes")
    extra_context = {"tituloPagina": "Editar Time", "h1": "Editar Time", "btn": "Salvar"}


class TimeDeleteView(AdminRequiredMixin, DeleteView):
    model = Time
    template_name = "campeonato/time_exclusao.html"
    success_url = reverse_lazy("listaTimes")
    extra_context = {"tituloPagina": "Excluir Time", "h1": "Excluir Time", "btn": "Confirmar Exclusão"}


# ---------------------------------------------------------------------------
# Jogadores
# ---------------------------------------------------------------------------

class JogadorListView(LoginRequiredMixin, ListView):
    model = Jogador
    template_name = "campeonato/jogador_lista.html"
    context_object_name = "jogadores"
    extra_context = {"tituloPagina": "Jogadores", "h1": "Jogadores"}

    def get_queryset(self):
        jogadores = Jogador.objects.select_related("time").order_by("nome")

        busca = self.request.GET.get("busca", "")
        time = self.request.GET.get("time", "")
        posicao = self.request.GET.get("posicao", "")

        if busca:
            # icontains = "contém", sem diferenciar maiúscula de minúscula
            jogadores = jogadores.filter(Q(nome__icontains=busca) | Q(time__nome__icontains=busca))
        if time:
            jogadores = jogadores.filter(time_id=time)
        if posicao:
            jogadores = jogadores.filter(posicao=posicao)
        return jogadores

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busca"] = self.request.GET.get("busca", "")
        contexto["filtroTime"] = self.request.GET.get("time", "")
        contexto["filtroPosicao"] = self.request.GET.get("posicao", "")
        contexto["filtrando"] = any([contexto["busca"], contexto["filtroTime"], contexto["filtroPosicao"]])
        contexto["times"] = Time.objects.order_by("nome")
        contexto["posicoes"] = Jogador.POSICOES
        return contexto


class JogadorCreateView(AdminRequiredMixin, CreateView):
    model = Jogador
    form_class = JogadorForm
    template_name = "campeonato/jogador_form.html"
    success_url = reverse_lazy("listaJogadores")
    extra_context = {"tituloPagina": "Cadastrar Jogador", "h1": "Cadastrar Jogador", "btn": "Cadastrar"}


class JogadorUpdateView(AdminRequiredMixin, UpdateView):
    model = Jogador
    form_class = JogadorForm
    template_name = "campeonato/jogador_form.html"
    success_url = reverse_lazy("listaJogadores")
    extra_context = {"tituloPagina": "Editar Jogador", "h1": "Editar Jogador", "btn": "Salvar"}


class JogadorDeleteView(AdminRequiredMixin, DeleteView):
    model = Jogador
    template_name = "campeonato/jogador_exclusao.html"
    success_url = reverse_lazy("listaJogadores")
    extra_context = {"tituloPagina": "Excluir Jogador", "h1": "Excluir Jogador", "btn": "Confirmar Exclusão"}


# ---------------------------------------------------------------------------
# Árbitros
# ---------------------------------------------------------------------------

class ArbitroListView(LoginRequiredMixin, ListView):
    model = Arbitro
    template_name = "campeonato/arbitro_lista.html"
    context_object_name = "arbitros"
    extra_context = {"tituloPagina": "Árbitros", "h1": "Árbitros"}

    def get_queryset(self):
        arbitros = Arbitro.objects.order_by("nome")
        busca = self.request.GET.get("busca", "")
        if busca:
            arbitros = arbitros.filter(Q(nome__icontains=busca) | Q(telefone__icontains=busca))
        return arbitros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busca"] = self.request.GET.get("busca", "")
        return contexto


class ArbitroCreateView(AdminRequiredMixin, CreateView):
    model = Arbitro
    form_class = ArbitroForm
    template_name = "campeonato/arbitro_form.html"
    success_url = reverse_lazy("listaArbitros")
    extra_context = {"tituloPagina": "Cadastrar Árbitro", "h1": "Cadastrar Árbitro", "btn": "Cadastrar"}


class ArbitroUpdateView(AdminRequiredMixin, UpdateView):
    model = Arbitro
    form_class = ArbitroForm
    template_name = "campeonato/arbitro_form.html"
    success_url = reverse_lazy("listaArbitros")
    extra_context = {"tituloPagina": "Editar Árbitro", "h1": "Editar Árbitro", "btn": "Salvar"}


class ArbitroDeleteView(AdminRequiredMixin, DeleteView):
    model = Arbitro
    template_name = "campeonato/arbitro_exclusao.html"
    success_url = reverse_lazy("listaArbitros")
    extra_context = {"tituloPagina": "Excluir Árbitro", "h1": "Excluir Árbitro", "btn": "Confirmar Exclusão"}
