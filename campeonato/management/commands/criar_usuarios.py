from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # uso: python manage.py criar_usuarios
    help = "Cria os dois usuários de exemplo: admin (pode tudo) e usuario (só visualiza)"

    def handle(self, *args, **options):
        usuarios = [
            # (login, senha, is_staff, is_superuser)
            ("admin", "admin123", True, True),
            ("usuario", "usuario123", False, False),
        ]
        for login, senha, staff, superuser in usuarios:
            user, criado = User.objects.get_or_create(username=login)
            user.set_password(senha)  # set_password guarda a senha criptografada
            user.is_staff = staff
            user.is_superuser = superuser
            user.save()
            nivel = "admin" if staff else "user"
            acao = "criado" if criado else "atualizado"
            self.stdout.write(self.style.SUCCESS(f"Usuário '{login}' ({nivel}) {acao} - senha: {senha}"))
