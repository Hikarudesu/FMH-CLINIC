"""URL configuration for the billing app — Services and Statement of Account."""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Services Management (Products/Medications)
    path('services/', views.service_list,
         name='billable_items'),
    path('services/create/', views.ServiceCreateView.as_view(),
         name='billable_item_create'),
    path('services/<int:pk>/update/',
         views.ServiceUpdateView.as_view(), name='billable_item_update'),
    path('services/<int:pk>/delete/',
         views.service_delete, name='billable_item_delete'),

    # Statement of Account - Admin Management
    path('statement/', views.statement_generator_form,
         name='statement_generator'),
    path('statement/save/', views.save_statement,
         name='save_statement'),
    path('statements/', views.statement_list,
         name='statement_list'),
    path('statement/<int:statement_id>/', views.statement_detail,
         name='statement_detail'),
    path('statement/<int:statement_id>/edit/', views.edit_statement,
         name='edit_statement'),
    path('statement/<int:statement_id>/release/', views.release_statement,
         name='release_statement'),
    path('statement/<int:statement_id>/delete/', views.delete_statement,
         name='delete_statement'),

    # Customer Portal - Statement Viewing
    path('my-statements/', views.my_statements,
         name='my_statements'),
    path('my-statements/<int:statement_id>/', views.view_statement,
         name='view_statement'),
]
