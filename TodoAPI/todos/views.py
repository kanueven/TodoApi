from django.shortcuts import render, redirect
import requests

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
API_BASE_URL = 'http://localhost:8000/api/'
def login_view(request):
    if request.method == 'GET':
        return render(request,'todos/login.html')
    if request.method =='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        response = requests.post(f'{API_BASE_URL}auth/login/',
                                 json={'email': email, 'password': password})
        
        if response.status_code == 200:
            data = response.json()
            request.session['access_token'] = data['access']
            request.session['refresh_token'] = data['refresh']
            request.session['username']=email.split('@')[0]
            return redirect('todos:lists')
        return render(request,'todos/login.html', 
                      {'error': 'Invalid credentials',
                       'email': email
                       })
    
def register_view(request):
    if request.method == 'GET':
        return render(request, 'todos/register.html')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        response = requests.post(f'{API_BASE_URL}auth/register/', json={
            'username': username,
            'email': email,
            'password': password
        })
        
        if response.status_code == 201:
            return redirect(request, 'todos:login')
        
        errors = response.json()
        error_message = next(iter(errors.values()))[0]
        
        return render(request, 'todos/register.html', {
            'error': error_message,
            'username': username,
            'email': email,
        })
def logout_view(request):
    request.session.flush()
    return redirect('todos:login')
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