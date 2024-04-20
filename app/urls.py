from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include(('products.urls', 'products'), namespace='product')), 
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('suppliers/', include('suppliers.urls')),
    path('cotacoes/', include(('cotacao.urls', 'cotacao'), namespace='cotacao')),
    path('answers/', include('answers.urls', namespace='answers')), 
    path('', RedirectView.as_view(url='/accounts/login/', permanent=True), name='home'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
