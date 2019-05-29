from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('new_account/<str:acc_type>/', views.add_account, name='add_account'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('<int:pk>/delete/', views.TransactionDelete.as_view(), name='transaction_delete'),
    path('accounts/<int:pk>/delete/', views.AccountDelete.as_view(), name='account_delete'),
    path('accounts/<int:pk>/edit/', views.AccountUpdate.as_view(), name='account_update'),
]