from django.contrib import admin
from .models import Time, Jogador, Arbitro, Partida, Gol


class JogadorInline(admin.TabularInline):
    # mostra os jogadores dentro da página do time (relação 1:N)
    model = Jogador
    extra = 0


class GolInline(admin.TabularInline):
    # mostra os gols dentro da página da partida (tabela do meio do N:N)
    model = Gol
    extra = 0


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ["nome", "bairro"]
    search_fields = ["nome", "bairro"]
    inlines = [JogadorInline]


@admin.register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = ["nome", "numeroCamisa", "posicao", "time"]
    list_filter = ["time", "posicao"]  # filtros na lateral direita do admin
    search_fields = ["nome"]


@admin.register(Arbitro)
class ArbitroAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone"]
    search_fields = ["nome", "telefone"]


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ["__str__", "data", "local", "arbitro"]
    list_filter = ["arbitro", "data"]
    search_fields = ["timeCasa__nome", "timeFora__nome", "local"]
    inlines = [GolInline]


@admin.register(Gol)
class GolAdmin(admin.ModelAdmin):
    list_display = ["partida", "jogador", "minuto"]
    list_filter = ["jogador__time"]
