from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import RedirectView

from .views import (
    CadastroUsuarioView,
    PartidaListView, PartidaCreateView, PartidaUpdateView, PartidaDeleteView, PartidaDetailView,
    GolCreateView, GolDeleteView,
    TimeListView, TimeCreateView, TimeUpdateView, TimeDeleteView,
    JogadorListView, JogadorCreateView, JogadorUpdateView, JogadorDeleteView,
    ArbitroListView, ArbitroCreateView, ArbitroUpdateView, ArbitroDeleteView,
)

# toda view baseada em classe é ligada na URL com .as_view()
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="listaPartidas")),  # página inicial mostra a lista de partidas

    # login / logout / criar conta (LoginView e LogoutView já vêm prontas no Django)
    path("login/", LoginView.as_view(
        template_name="campeonato/login.html",
        redirect_authenticated_user=True,
        extra_context={"tituloPagina": "Entrar", "h1": "Entrar"},
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("cadastro/", CadastroUsuarioView.as_view(), name="cadastroUsuario"),

    path("partidas/", PartidaListView.as_view(), name="listaPartidas"),
    path("partidas/cadastrar/", PartidaCreateView.as_view(), name="cadastrarPartida"),
    path("partidas/editar/<int:pk>/", PartidaUpdateView.as_view(), name="editarPartida"),
    path("partidas/excluir/<int:pk>/", PartidaDeleteView.as_view(), name="excluirPartida"),
    path("partidas/<int:pk>/", PartidaDetailView.as_view(), name="detalhePartida"),
    path("partidas/<int:pk>/gols/adicionar/", GolCreateView.as_view(), name="adicionarGol"),  # pk = partida
    path("gols/excluir/<int:pk>/", GolDeleteView.as_view(), name="excluirGol"),  # pk = gol

    path("times/", TimeListView.as_view(), name="listaTimes"),
    path("times/cadastrar/", TimeCreateView.as_view(), name="cadastrarTime"),
    path("times/editar/<int:pk>/", TimeUpdateView.as_view(), name="editarTime"),
    path("times/excluir/<int:pk>/", TimeDeleteView.as_view(), name="excluirTime"),

    path("jogadores/", JogadorListView.as_view(), name="listaJogadores"),
    path("jogadores/cadastrar/", JogadorCreateView.as_view(), name="cadastrarJogador"),
    path("jogadores/editar/<int:pk>/", JogadorUpdateView.as_view(), name="editarJogador"),
    path("jogadores/excluir/<int:pk>/", JogadorDeleteView.as_view(), name="excluirJogador"),

    path("arbitros/", ArbitroListView.as_view(), name="listaArbitros"),
    path("arbitros/cadastrar/", ArbitroCreateView.as_view(), name="cadastrarArbitro"),
    path("arbitros/editar/<int:pk>/", ArbitroUpdateView.as_view(), name="editarArbitro"),
    path("arbitros/excluir/<int:pk>/", ArbitroDeleteView.as_view(), name="excluirArbitro"),
]
