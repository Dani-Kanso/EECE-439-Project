from django.urls import path
from . import views

urlpatterns = [
    path('success/', views.success, name='success'),
    path('', views.list_contacts, name='contacts-list'),
    path('add/', views.home, name='contacts-add'),
    path('admin-info/', views.index, name='admin-info'),
    path('contacts/', views.list_contacts, name='contacts-list'),
    path('contacts/<int:pk>/edit/', views.edit_contact, name='contacts-edit'),
    path('contacts/<int:pk>/delete/', views.delete_contact, name='contacts-delete'),
    path('recommendations/', views.recommend_contacts, name='contacts-recommendations'),
]
