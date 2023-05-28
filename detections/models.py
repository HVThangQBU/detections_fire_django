from datetime import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionManager
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


User = get_user_model()


class Camera(models.Model):
    id_cam = models.AutoField(primary_key=True)
    name_cam = models.CharField(max_length=100)
    port = models.IntegerField(default=2222)
    name_location = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150, blank=True)
    user = models.CharField(max_length=100)
    latitude = models.CharField(max_length=150, blank=True)
    longitude = models.CharField(max_length=150, blank=True)
    urlRTSP = models.CharField(max_length=100, default=None)


    def __str__(self):
        return self.name_cam


class Detection(models.Model):
    id_detect =  models.AutoField(primary_key=True)
    name_detect = models.CharField(max_length=100)
    name_cam = models.CharField(max_length=100)
    content = models.TextField()
    image_detect = models.ImageField(upload_to="detect_image", default="bienbao.png")
    time_detect = models.DateTimeField()


    def __str__(self):
        return self.name_detect

    def save(self, *args, **kwargs):
        if not self.time_detect:
            self.time_detect = timezone.now()
        super().save(*args, **kwargs)




class CustomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(
        upload_to="profile_images", default="blank-profile-picture.png"
    )
    phone_number = models.CharField(max_length=20)
    address = models.TextField(max_length=50, blank=True)
    id_group = models.IntegerField(default=2)
 

    def __str__(self):
        return self.user.username

    class Meta:
        permissions = [
            ("view_camera", "Can view camera"),
            ("edit_camera", "Can edit camera"),
            ("can_view_detail_camera", "Can view detail camera"),
        ]

class CustomGroup(Group):
    description = models.CharField(max_length=100)
# @permission_required('canhbao.view_customuser')

class Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    can_view_by_name_came = models.BooleanField(default=False)
    can_edit_by_name_came = models.BooleanField(default=False)

