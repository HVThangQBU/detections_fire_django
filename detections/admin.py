from django.contrib import admin

# Register your models here.
from detections.models import Camera,Detection, CustomUser,CustomGroup, Permission

admin.site.register(Permission)
# #
admin.site.register(Camera)
# #
admin.site.register(Detection)
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(CustomGroup)


