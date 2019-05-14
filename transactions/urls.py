from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('<int:pk>/delete/', views.TransactionDelete.as_view(), name='transaction_delete'),
]