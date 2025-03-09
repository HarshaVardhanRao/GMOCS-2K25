from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_ticket, name='generate_ticket'),
    path('ticket/<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('confirm-payment/<uuid:ticket_id>/', views.confirm_payment, name='confirm_payment'),
    path('events/', views.event_list, name='event_list'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('registrations/', views.registration_list, name='registration_list'),
    path('login',views.login_user, name='login'),
    path("deploy", views.deploy_view, name="deploy"),
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
