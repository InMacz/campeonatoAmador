from django.db import models

class Time(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome") # unique=True impede dois times com o mesmo nome
    bairro = models.CharField(max_length=100, verbose_name="Bairro")

    def __str__(self):
        return self.nome

class Jogador(models.Model):
    POSICOES = [
        ("goleiro", "Goleiro"),
        ("zagueiro", "Zagueiro"),
        ("lateral", "Lateral"),
        ("meio", "Meio-campo"),
        ("atacante", "Atacante"),
    ] # o primeiro valor é salvo no banco e o segundo é o que aparece na tela

    nome = models.CharField(max_length=100, verbose_name="Nome")
    posicao = models.CharField(max_length=20, choices=POSICOES, verbose_name="Posição")
    numeroCamisa = models.PositiveIntegerField(verbose_name="Número da camisa")
    # 1:N — um time tem vários jogadores, e cada jogador é de um time só
    time = models.ForeignKey(Time,
    on_delete=models.CASCADE,
    related_name="jogadores",
    verbose_name="Time",) # com o related_name podemos usar time.jogadores.all()

    def __str__(self):
        return f"{self.nome} ({self.time})"

    def totalGols(self):
        return self.gols.count()

class Arbitro(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")

    def __str__(self):
        return self.nome

class Partida(models.Model):
    # duas relações 1:N com Time: um time joga várias partidas em casa e várias fora.
    # como as duas apontam para Time, cada uma precisa de um related_name diferente
    timeCasa = models.ForeignKey(Time,
    on_delete=models.CASCADE,
    related_name="partidasCasa",
    verbose_name="Time da casa",)
    timeFora = models.ForeignKey(Time,
    on_delete=models.CASCADE,
    related_name="partidasFora",
    verbose_name="Time visitante",)
    # 1:N — um árbitro apita várias partidas, e cada partida tem um árbitro só.
    # SET_NULL: se o árbitro for excluído, a partida continua existindo, só fica sem árbitro
    arbitro = models.ForeignKey(Arbitro,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="partidas",
    verbose_name="Árbitro",)
    # N:N — uma partida tem gols de vários jogadores, e um jogador marca gols em várias partidas.
    # o through diz que a tabela do meio é a Gol, assim conseguimos guardar o minuto de cada gol
    jogadores = models.ManyToManyField(Jogador,
    through="Gol",
    related_name="partidas",
    verbose_name="Jogadores que marcaram",)
    data = models.DateTimeField(verbose_name="Data e hora")
    local = models.CharField(max_length=100, verbose_name="Local")

    def __str__(self):
        return f"{self.timeCasa} x {self.timeFora}"

    def golsCasa(self):
        return self.gols.filter(jogador__time=self.timeCasa).count() # conta só os gols de jogadores do time da casa

    def golsFora(self):
        return self.gols.filter(jogador__time=self.timeFora).count()

    def placar(self):
        return f"{self.timeCasa} {self.golsCasa()} x {self.golsFora()} {self.timeFora}"

class Gol(models.Model):
    # tabela do meio da relação N:N entre Partida e Jogador
    partida = models.ForeignKey(Partida,
    on_delete=models.CASCADE,
    related_name="gols",
    verbose_name="Partida",) # com o related_name podemos usar partida.gols.all()
    jogador = models.ForeignKey(Jogador,
    on_delete=models.CASCADE,
    related_name="gols",
    verbose_name="Jogador",)
    minuto = models.PositiveIntegerField(verbose_name="Minuto")

    class Meta:
        ordering = ["minuto"] # os gols sempre aparecem em ordem de minuto

    def __str__(self):
        return f"{self.minuto}' - {self.jogador.nome}"
