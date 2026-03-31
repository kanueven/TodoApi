from .models import User, TodoList, TodoItem
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer, TodoListSerializer,TodoItemSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from .permissions import IsOwner
from datetime import datetime

# Create your views here.
class RegisterView(APIView):
    def post(self,request):
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({'error': 'Invalid credentials'},
                            status = status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        
        return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status = status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data,status = status.HTTP_200_OK)
    def put(self,request):
        serializer = UserSerializer(request.user, data = request.data,partial = True )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class TodoListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = TodoListSerializer
    def get_queryset(self):
        return TodoList.objects.filter(
            owner=self.request.user,
            # completed = False,
            # priority = 'high',
            # due_date__lte = datetime.today()
            )
    def perform_create(self,serializer):
        serializer.save(owner=self.request.user)
class TodoItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = TodoItemSerializer
    def get_queryset(self):
        return TodoItem.objects.filter(todo_list__owner=self.request.user,
                                       todo_list=self.kwargs['todolist_pk'])
    
    def perform_create(self, serializer):
        todo_list = TodoList.objects.get(pk=self.kwargs['todolist_pk'],
                                         owner=self.request.user)
        serializer.save(todo_list=todo_list)