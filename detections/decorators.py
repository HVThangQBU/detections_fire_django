from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404


from detections.models import Camera, Permission



def can_view_camera(user, camera):
    try:
        permission = Permission.objects.get(user=user, camera=camera)
        return permission.can_view_by_name_came
    except Permission.DoesNotExist:
        return False

def can_edit_camera(user, camera):
    try:
        permission = Permission.objects.get(user=user, camera=camera)
        return permission.can_edit_by_name_came
    except Permission.DoesNotExist:
        return False

def require_view_permission(func):
    def wrapper(request, id, *args, **kwargs):
        camera = get_object_or_404(Camera, id_cam=id)
        if can_view_camera(request.user, camera):
            return func(request, id, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper

def require_edit_permission(func):
    def wrapper(request, id, *args, **kwargs):
        queryset = Camera.objects.all()
        id_cam = queryset[id].id_cam
        camera = get_object_or_404(Camera, id_cam=id_cam)
        if can_edit_camera(request.user, camera):
            return func(request, id_cam, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper
