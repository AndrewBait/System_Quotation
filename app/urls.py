from django.contrib import admin
from django.urls import path, include  # 'include' já está importado
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('products/', include('products.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('cotacoes/', include('cotacao.urls', namespace='cotacao')),  
    path('', RedirectView.as_view(url='/accounts/login/', permanent=True), name='home'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
