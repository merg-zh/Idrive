from django.urls import path
from app_first import views

app_name = "app_first"

urlpatterns = [
    path('', views.TopView, name='top'),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path('home/', views.HomeView, name="home"),
    path("ajax-list/",views.Ajax_Append_List, name="ajax-list"),
    path("ajax-left/",views.Ajax_Left_List, name="ajax-left"),
]