import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import RestaurantLocation
from restaurants.forms import RestaurantLocationCreateForm

User = get_user_model()

# ==========================================
# FIXTURES (Fábrica de Datos Falsos)
# ==========================================

@pytest.fixture
def test_user(db):
    """Crea un usuario dueño del restaurante"""
    return User.objects.create_user(username='chef', password='password123')

@pytest.fixture
def test_restaurant(db, test_user):
    """Crea un restaurante de prueba. Nota: categoría en minúsculas intencionalmente."""
    return RestaurantLocation.objects.create(
        owner=test_user,
        name='Pizza Planet',
        location='Santiago',
        category='italian' 
    )

# ==========================================
# TESTS (La Red de Seguridad)
# ==========================================

@pytest.mark.django_db
class TestRestaurantLogic:

    def test_pre_save_signal_slug_and_category(self, test_restaurant):
        """Prueba: Verifica que el pre_save capitalice la categoría y genere el slug"""
        
        # 1. 'italian' debería haberse convertido automáticamente en 'Italian'
        assert test_restaurant.category == 'Italian'
        
        # 2. El slug no estaba provisto, debería haberse autogenerado (ej. pizza-planet)
        assert test_restaurant.slug is not None
        assert 'pizza-planet' in test_restaurant.slug

    def test_restaurant_list_view_authenticated(self, client, test_user, test_restaurant):
        """Prueba: Un usuario logueado puede ver su lista de restaurantes"""
        client.login(username='chef', password='password123')
        
        # Asumiendo namespace 'restaurants'
        try:
            url = reverse('restaurants:list') 
        except:
            url = reverse('list')

        response = client.get(url)

        assert response.status_code == 200
        assert 'Pizza Planet' in response.content.decode('utf-8')

    def test_restaurant_create_form_validation(self):
        """Prueba: El formulario rechaza el nombre 'Hello' según la regla de negocio"""
        form_data = {'name': 'Hello', 'location': 'Centro', 'category': 'Cafe'}
        form = RestaurantLocationCreateForm(data=form_data)
        
        # El formulario NO debe ser válido
        assert not form.is_valid()
        # Debe contener nuestro mensaje de error personalizado
        assert 'Not a valid name' in form.errors['name']

    def test_custom_queryset_search(self, test_restaurant):
        """Prueba: El manager customizado (search) encuentra correctamente por nombre o categoría"""
        
        # Búsqueda que DEBERÍA encontrarlo
        qs_found = RestaurantLocation.objects.search('Pizza')
        assert qs_found.count() == 1

        # Búsqueda que NO debería encontrarlo
        qs_not_found = RestaurantLocation.objects.search('Tacos')
        assert qs_not_found.count() == 0