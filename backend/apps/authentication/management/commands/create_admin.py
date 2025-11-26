from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un usuario administrador'

    def handle(self, *args, **options):
        email = 'admin@somacor.cl'
        password = 'Admin123!'
        first_name = 'Administrador'
        last_name = 'Sistema'
        rut = '11111111-1'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'El usuario {email} ya existe'))
            user = User.objects.get(email=email)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Contraseña actualizada para {email}'))
        else:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rut=rut
            )
            self.stdout.write(self.style.SUCCESS(f'Superusuario {email} creado exitosamente!'))

        self.stdout.write(self.style.SUCCESS('\nCredenciales:'))
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Contraseña: {password}')
