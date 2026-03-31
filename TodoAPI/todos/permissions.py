from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
        # if the object is a TodoList, check if the owner is the logged in user
            return obj.owner == request.user
        # if the object is a TodoItem, we go up to its list and check the owner from there
        if hasattr(obj, 'todo_list'):
            return obj.todo_list.owner == request.user
        return False