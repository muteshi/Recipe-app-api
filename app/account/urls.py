from django.urls import path

from . import views

app_name = 'account'


urlpatterns = [
    path('account-create/', views.CreateUserAccountView.as_view(),
         name='account-create'),
    path('account-token/', views.CreateTokentView.as_view(),
         name='account-token')
]
