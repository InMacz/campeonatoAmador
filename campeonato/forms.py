from django import forms
from .models import Arbitro, Gol, Jogador, Partida, Time

class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ["nome", "bairro"]

class JogadorForm(forms.ModelForm):
    class Meta:
        model = Jogador
        fields = ["nome", "posicao", "numeroCamisa", "time"]

class ArbitroForm(forms.ModelForm):
    class Meta:
        model = Arbitro
        fields = ["nome", "telefone"]

class PartidaForm(forms.ModelForm):
    class Meta:
        model = Partida
        fields = ["timeCasa", "timeFora", "arbitro", "data", "local"] # os gols são adicionados depois, na página de detalhe da partida
        widgets = {
            # type="datetime-local" faz o navegador mostrar um seletor de data e hora
            "data": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def clean(self):
        dados = super().clean()
        if dados.get("timeCasa") and dados.get("timeCasa") == dados.get("timeFora"):
            raise forms.ValidationError("Um time não pode jogar contra ele mesmo.")
        return dados

class GolForm(forms.ModelForm):
    class Meta:
        model = Gol
        fields = ["jogador", "minuto"]
