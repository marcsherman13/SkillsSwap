from django.urls import path
from . import views

urlpatterns = [
    # Home and skill browsing
    path('', views.home, name='home'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/<int:pk>/', views.skill_detail, name='skill_detail'),
    
    # Skill management (requires login)
    path('skills/create/', views.skill_create, name='skill_create'),
    path('skills/<int:pk>/edit/', views.skill_update, name='skill_update'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
    
    # Reviews (requires login)
    path('skills/<int:pk>/review/create/', views.create_review, name='create_review'),
    path('skills/<int:skill_id>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('skills/<int:skill_id>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    
    # Messaging (requires login)
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/send/<int:recipient_id>/', views.send_message, name='send_message'),
    path('messages/send/<int:recipient_id>/skill/<int:skill_id>/', views.send_message, name='send_message_skill'),
    path('messages/conversation/<int:other_user_id>/', views.view_conversation, name='view_conversation'),
    path('messages/reply/<int:other_user_id>/', views.reply_message, name='reply_message'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
