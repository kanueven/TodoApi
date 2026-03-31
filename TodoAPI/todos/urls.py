from django.urls import path
from .views import RegisterView, LoginView, ProfileView
from rest_framework_nested import routers
from .views import TodoListViewSet, TodoItemViewSet

router = routers.DefaultRouter()
router.register(r'todolists', TodoListViewSet, basename='todolist')

todo_lists_router = routers.NestedDefaultRouter(router, r'todolists', lookup= r'todolist')
todo_lists_router.register(r'todo-items', TodoItemViewSet, basename='todolist-items')

urlpatterns = [
   *router.urls,
   *todo_lists_router.urls,
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    
   
]

