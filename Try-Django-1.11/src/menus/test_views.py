import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from menus.models import Item
from restaurants.models import RestaurantLocation

User = get_user_model()

# ==========================================
# FIXTURES (Fábrica de Datos Falsos)
# ==========================================

@pytest.fixture
def test_user(db):
    """Crea un usuario de prueba"""
    return User.objects.create_user(username='tester', password='password123')

@pytest.fixture
def test_restaurant(db, test_user):
    """Crea un restaurante falso asociado al usuario"""
    return RestaurantLocation.objects.create(
        owner=test_user,
        name='Tacos El Vuelo',
        location='Santiago',
        category='Mexicana'
    )

@pytest.fixture
def test_item(db, test_user, test_restaurant):
    """Crea un plato (item) de prueba en el menú"""
    return Item.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        name='Taco al Pastor',
        contents='Cerdo, Piña, Cilantro',
        public=True
    )

# ==========================================
# TESTS (La Red de Seguridad)
# ==========================================

@pytest.mark.django_db
class TestMenuViews:

    def test_item_list_view_authenticated(self, client, test_user, test_item):
        """Prueba: Un usuario logueado puede ver su lista de items y devuelve código 200"""
        client.login(username='tester', password='password123')
        url = reverse('menus:list') # Asumiendo que el namespace es 'menus'
        response = client.get(url)
        
        assert response.status_code == 200
        # Verificamos que el item que creamos aparezca en el HTML
        assert 'Taco al Pastor' in response.content.decode('utf-8')

    def test_item_list_view_unauthenticated(self, client):
        """Prueba: Un usuario anónimo es bloqueado y redirigido al login (302)"""
        url = reverse('menus:list')
        response = client.get(url)
        
        assert response.status_code == 302 # Redirección por el LoginRequiredMixin
        assert 'login' in response.url

    def test_item_create_view_post(self, client, test_user, test_restaurant):
        """Prueba: Un usuario puede crear un nuevo plato enviando un POST"""
        client.login(username='tester', password='password123')
        url = reverse('menus:create')
        
        # Simulamos los datos que enviaría el formulario HTML
        data = {
            'restaurant': test_restaurant.id,
            'name': 'Quesadilla',
            'contents': 'Queso, Tortilla',
            'excludes': 'Cebolla',
            'public': True
        }
        
        response = client.post(url, data)
        
        # Si fue exitoso, Django suele redirigir al DetailView del nuevo objeto (código 302)
        assert response.status_code == 302
        # Comprobamos que el objeto realmente se guardó en la base de datos
        assert Item.objects.filter(name='Quesadilla').exists()