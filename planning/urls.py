import transactions
from django.urls import path
from . import views
urlpatterns = [
    path('', transactions.views.index, name='index'),
    path('new_period/', views.PeriodMandatoryTransactionCreate.as_view(), name='add_period'),
    path('new_period/<int:pk>/set_goal', views.set_the_goal, name='set_goal'),
    path('period/<int:pk>/edit', views.PeriodMandatoryTransactionUpdate.as_view(), name='edit_period'),
]