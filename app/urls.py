from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('products/', include(('products.urls', 'products'), namespace='product')), 
        path('accounts/', include('accounts.urls', namespace='accounts')),
        path('suppliers/', include('suppliers.urls')),
        path('cotacoes/', include(('cotacao.urls', 'cotacao'), namespace='cotacao')),
        path('', RedirectView.as_view(url='/accounts/login/', permanent=True), name='home'),
        
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
