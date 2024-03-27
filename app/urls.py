from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('products/', include('products.urls')),  # Certifique-se de que este namespace esteja configurado corretamente
    path('suppliers/', include('suppliers.urls')),  # E este também
    # Certifique-se de que 'quotations.urls' tem um namespace 'quotations' definido em quotations/urls.py
    path('quotations/v1/', include(('quotations.urls', 'quotations'), namespace='v1')),  
    path('', RedirectView.as_view(url='/accounts/login/', permanent=True), name='home'),  # Redireciona para login
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
