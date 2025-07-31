from django.urls import path
from . import views

urlpatterns = [
    path('home',views.dashboard,name="dashboard"),
    path('logout',views.logout_view, name='logout_view'),
  
    path('',views.kreditbee_login,name="kreditbee_login"),
    path('approval-letter',views.create_letter,name="create_letter"),
    path('emi-calulator',views.emiCalculator,name="emiCalculator"),
    path('approvalletter-list',views.approvalletter,name="approvalletter"),
    path('addbank',views.addbank,name="addbank"),
    path('show-banks/', views.show_banks, name='show_banks'),
    path('edit-bank/<int:pk>/', views.edit_bank, name='edit_bank'),
    path('delete-bank/<int:pk>/', views.delete_bank, name='delete_bank'),
  
    path('ajax/get-bank-details/', views.get_bank_details, name='get_bank_details'),

    path('edit-letter/<int:pk>/', views.edit_letter, name='edit_letter'),
    path('download-letter/<int:pk>/', views.download_pdf, name='download_pdf'),
  



]
