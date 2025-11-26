from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('notas/login/', views.notas_login, name='notas_login'),
    path('notas/logout/', views.notas_logout, name='notas_logout'),
    path('notas/<int:pk>/', views.notas_estudiante, name='notas_estudiante'),
    path('notas/<int:pk>/cambiar-clave/', views.cambiar_clave, name='cambiar_clave'),
    # Estudiantes
    path('estudiantes/', views.estudiantes_list, name='estudiantes_list'),
    path('estudiantes/nuevo/', views.estudiantes_create, name='estudiantes_create'),
    path('estudiantes/<int:pk>/editar/', views.estudiantes_update, name='estudiantes_update'),
    path('estudiantes/<int:pk>/eliminar/', views.estudiantes_delete, name='estudiantes_delete'),
    # Asignaturas
    path('asignaturas/', views.asignaturas_list, name='asignaturas_list'),
    path('asignaturas/nuevo/', views.asignaturas_create, name='asignaturas_create'),
    path('asignaturas/<int:pk>/editar/', views.asignaturas_update, name='asignaturas_update'),
    path('asignaturas/<int:pk>/eliminar/', views.asignaturas_delete, name='asignaturas_delete'),
]


