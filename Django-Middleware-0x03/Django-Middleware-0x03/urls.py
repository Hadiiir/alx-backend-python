from django.contrib import admin
from django.urls import path
from chats import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add your other URL patterns here
]