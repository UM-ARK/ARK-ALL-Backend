"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path,include
import api.views as api

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('test_user/', api.test_user),
    path('test_user2/', api.test2_user),
    path('test_activity/',api.test_activity),
    path('test_activity2/',api.test2_activity),
    path('test_club/', api.test_club),
    path('test_club2/', api.test2_club),


    path('api/',include(("api.urls",'api'),namespace='api')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

