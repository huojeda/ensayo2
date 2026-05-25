import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()

# ==========================================
# FIXTURES (Fábrica de Datos Falsos)
# ==========================================

@pytest.fixture
def test_user_admin(db):
    """Crea el primer usuario (obtendrá id=1 para evitar errores en post_save)"""
    return User.objects.create_user(username='admin_muypicky', password='password123', email='admin@test.com')

@pytest.fixture
def test_user_normal(db, test_user_admin):
    """Crea un segundo usuario de prueba"""
    return User.objects.create_user(username='tester_profile', password='password123', email='tester@test.com')

# ==========================================
# TESTS (La Red de Seguridad)
# ==========================================

@pytest.mark.django_db
class TestProfileLogic:

    def test_profile_is_created_on_user_creation(self, test_user_admin):
        """Prueba: Verifica que el Signal (post_save) crea automáticamente un perfil al crear un usuario"""
        # Si el usuario tiene perfil, esto no arrojará error
        assert hasattr(test_user_admin, 'profile')
        assert isinstance(test_user_admin.profile, Profile)

    def test_toggle_follow_manager(self, test_user_admin, test_user_normal):
        """Prueba: Verifica que la lógica de seguir/dejar de seguir usuarios funciona en la BD"""
        
        # 1. Por regla de negocio (post_save), el nuevo usuario YA sigue al admin (id=1)
        assert test_user_normal in test_user_admin.profile.followers.all()

        # 2. Al presionar el botón por primera vez, lo DEJA DE SEGUIR
        profile_, is_following = Profile.objects.toggle_follow(test_user_normal, test_user_admin.username)
        
        assert is_following is False
        assert test_user_normal not in profile_.followers.all()

        # 3. Al presionar el botón de nuevo, lo VUELVE A SEGUIR
        profile_, is_following = Profile.objects.toggle_follow(test_user_normal, test_user_admin.username)
        
        assert is_following is True
        assert test_user_normal in profile_.followers.all()

    def test_profile_detail_view_authenticated(self, client, test_user_admin, test_user_normal):
        """Prueba: Un usuario logueado puede ver el perfil de otro usuario activo"""
        
        # Nos aseguramos de que el usuario al que visitaremos esté activo
        test_user_admin.is_active = True
        test_user_admin.save()

        # Iniciamos sesión con el usuario normal
        client.login(username='tester_profile', password='password123')
        
        # Visitamos el perfil del admin. (Asumiendo que el namespace en el urls.py principal es 'profiles')
        # Si arroja error de reverse, cambiaremos 'profiles:detail' por 'detail'
        try:
            url = reverse('profiles:detail', kwargs={'username': test_user_admin.username})
        except:
            url = reverse('detail', kwargs={'username': test_user_admin.username})

        response = client.get(url)
        
        assert response.status_code == 200
        assert test_user_admin.username in response.content.decode('utf-8')