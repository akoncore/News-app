
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/',include('apps.accounts.urls')),
    path('api/v1/posts/',include('apps.main.urls')),
    path('api/v1/comments/', include('apps.comments.urls')),
      
]
