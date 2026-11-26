from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Arbitro, Gol, Jogador, Partida, Time


class BaseTeste(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("admin", password="senha123", is_staff=True)
        cls.usuario = User.objects.create_user("usuario", password="senha123")

        cls.timeA = Time.objects.create(nome="Vila Nova", bairro="Centro")
        cls.timeB = Time.objects.create(nome="União", bairro="Jardim")
        cls.timeC = Time.objects.create(nome="Estrela", bairro="Bairro Alto")
        cls.arbitro = Arbitro.objects.create(nome="Carlos", telefone="1199999")
        cls.outroArbitro = Arbitro.objects.create(nome="Roberto", telefone="1188888")

        cls.joao = Jogador.objects.create(nome="João", posicao="atacante", numeroCamisa=9, time=cls.timeA)
        cls.pedro = Jogador.objects.create(nome="Pedro", posicao="goleiro", numeroCamisa=1, time=cls.timeB)
        cls.lucas = Jogador.objects.create(nome="Lucas", posicao="atacante", numeroCamisa=10, time=cls.timeC)

        data = timezone.make_aware(datetime(2026, 11, 1, 15, 0))
        cls.partida = Partida.objects.create(
            timeCasa=cls.timeA, timeFora=cls.timeB, arbitro=cls.arbitro, data=data, local="Campo do Centro"
        )
        cls.outraPartida = Partida.objects.create(
            timeCasa=cls.timeC, timeFora=cls.timeB, arbitro=cls.outroArbitro, data=data, local="Arena Sul"
        )
        Gol.objects.create(partida=cls.partida, jogador=cls.joao, minuto=10)
        Gol.objects.create(partida=cls.partida, jogador=cls.joao, minuto=40)
        Gol.objects.create(partida=cls.partida, jogador=cls.pedro, minuto=70)


class RelacionamentosTeste(BaseTeste):
    def test_um_para_muitos(self):
        # 1:N — Time -> Jogadores
        self.assertEqual(list(self.timeA.jogadores.all()), [self.joao])
        # 1:N — Árbitro -> Partidas
        self.assertEqual(list(self.arbitro.partidas.all()), [self.partida])

    def test_muitos_para_muitos(self):
        # N:N — Partida <-> Jogador, pela tabela Gol
        self.assertEqual(set(self.partida.jogadores.all()), {self.joao, self.pedro})
        self.assertEqual(list(self.joao.partidas.distinct()), [self.partida])
        self.assertEqual(self.partida.placar(), "Vila Nova 2 x 1 União")


class AcessoTeste(BaseTeste):
    def test_visitante_vai_para_login(self):
        resposta = self.client.get(reverse("listaPartidas"))
        self.assertRedirects(resposta, reverse("login") + "?next=" + reverse("listaPartidas"))

    def test_user_pode_ver(self):
        self.client.force_login(self.usuario)
        for nome in ["listaPartidas", "listaTimes", "listaJogadores", "listaArbitros"]:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200)
        self.assertEqual(self.client.get(reverse("detalhePartida", args=[self.partida.pk])).status_code, 200)

    def test_user_nao_pode_alterar(self):
        self.client.force_login(self.usuario)
        urls = [
            reverse("cadastrarTime"),
            reverse("editarTime", args=[self.timeA.pk]),
            reverse("excluirTime", args=[self.timeA.pk]),
            reverse("cadastrarPartida"),
            reverse("editarPartida", args=[self.partida.pk]),
            reverse("cadastrarJogador"),
            reverse("cadastrarArbitro"),
            reverse("adicionarGol", args=[self.partida.pk]),
            reverse("excluirGol", args=[self.partida.gols.first().pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403, url)
        # tentar excluir mandando POST direto também é bloqueado
        self.assertEqual(self.client.post(reverse("excluirTime", args=[self.timeA.pk])).status_code, 403)
        self.assertTrue(Time.objects.filter(pk=self.timeA.pk).exists())
        self.assertEqual(
            self.client.post(reverse("adicionarGol", args=[self.partida.pk]), {"jogador": self.joao.pk, "minuto": 80}).status_code,
            403,
        )

    def test_user_nao_ve_botoes_de_admin(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("listaTimes"))
        self.assertNotContains(resposta, reverse("cadastrarTime"))
        self.assertNotContains(resposta, reverse("editarTime", args=[self.timeA.pk]))

    def test_admin_pode_cadastrar_editar_excluir(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(reverse("cadastrarTime"), {"nome": "Novo FC", "bairro": "Norte"})
        self.assertRedirects(resposta, reverse("listaTimes"))
        novo = Time.objects.get(nome="Novo FC")

        self.client.post(reverse("editarTime", args=[novo.pk]), {"nome": "Novo FC", "bairro": "Sul"})
        novo.refresh_from_db()
        self.assertEqual(novo.bairro, "Sul")

        self.client.post(reverse("excluirTime", args=[novo.pk]))
        self.assertFalse(Time.objects.filter(pk=novo.pk).exists())

    def test_cadastro_cria_usuario_comum(self):
        self.client.post(reverse("cadastroUsuario"), {
            "username": "novato", "password1": "SenhaForte!2026", "password2": "SenhaForte!2026",
        })
        self.assertFalse(User.objects.get(username="novato").is_staff)


class PartidaGolTeste(BaseTeste):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_adicionar_gol(self):
        resposta = self.client.post(reverse("adicionarGol", args=[self.partida.pk]), {"jogador": self.pedro.pk, "minuto": 85})
        self.assertRedirects(resposta, reverse("detalhePartida", args=[self.partida.pk]))
        self.assertEqual(self.partida.golsFora(), 2)

    def test_gol_de_jogador_de_outro_time_e_recusado(self):
        resposta = self.client.post(reverse("adicionarGol", args=[self.partida.pk]), {"jogador": self.lucas.pk, "minuto": 5})
        self.assertEqual(resposta.status_code, 200)  # mostra a página de novo com o erro
        self.assertFalse(Gol.objects.filter(jogador=self.lucas).exists())

    def test_time_nao_joga_contra_ele_mesmo(self):
        resposta = self.client.post(reverse("cadastrarPartida"), {
            "timeCasa": self.timeA.pk, "timeFora": self.timeA.pk, "data": "2026-11-20T10:00", "local": "X",
        })
        self.assertContains(resposta, "Um time não pode jogar contra ele mesmo.")

    def test_editar_partida(self):
        resposta = self.client.post(reverse("editarPartida", args=[self.partida.pk]), {
            "timeCasa": self.timeA.pk, "timeFora": self.timeB.pk, "arbitro": self.arbitro.pk,
            "data": "2026-11-01T15:00", "local": "Campo Novo",
        })
        self.assertRedirects(resposta, reverse("detalhePartida", args=[self.partida.pk]))
        self.partida.refresh_from_db()
        self.assertEqual(self.partida.local, "Campo Novo")

    def test_excluir_gol(self):
        gol = self.partida.gols.first()  # gol do João aos 10'
        resposta = self.client.post(reverse("excluirGol", args=[gol.pk]))
        self.assertRedirects(resposta, reverse("detalhePartida", args=[self.partida.pk]))
        self.assertEqual(self.partida.placar(), "Vila Nova 1 x 1 União")


class FiltrosTeste(BaseTeste):
    def setUp(self):
        self.client.force_login(self.usuario)

    def listaDe(self, nome, chave, **filtros):
        return list(self.client.get(reverse(nome), filtros).context[chave])

    def test_filtros_de_partida(self):
        self.assertEqual(self.listaDe("listaPartidas", "partidas", time=self.timeA.pk), [self.partida])
        self.assertEqual(self.listaDe("listaPartidas", "partidas", arbitro=self.outroArbitro.pk), [self.outraPartida])
        self.assertEqual(self.listaDe("listaPartidas", "partidas", busca="arena"), [self.outraPartida])
        self.assertEqual(len(self.listaDe("listaPartidas", "partidas", time=self.timeB.pk)), 2)  # União jogou as duas (fora)

    def test_filtros_de_jogador(self):
        self.assertEqual(self.listaDe("listaJogadores", "jogadores", posicao="goleiro"), [self.pedro])
        self.assertEqual(self.listaDe("listaJogadores", "jogadores", time=self.timeC.pk), [self.lucas])
        self.assertEqual(self.listaDe("listaJogadores", "jogadores", posicao="atacante", time=self.timeA.pk), [self.joao])

    def test_busca_de_time_e_arbitro(self):
        self.assertEqual(self.listaDe("listaTimes", "times", busca="jardim"), [self.timeB])
        self.assertEqual(self.listaDe("listaArbitros", "arbitros", busca="rob"), [self.outroArbitro])
