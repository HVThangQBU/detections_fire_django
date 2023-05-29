from django.shortcuts import render

# Create your views here.
import datetime
import json
from pyexpat.errors import messages
import base64
import time
from importlib import import_module
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth, User
from django.contrib.auth.decorators import login_required, permission_required
import cv2
from django.db import connection
from django.http import HttpResponse, StreamingHttpResponse
from django.http.response import JsonResponse
from django.template import loader
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from detections.decorators import require_view_permission
from detections.models import Camera, Detection, CustomUser
from django.forms.models import model_to_dict
from django.http import HttpResponseNotFound, JsonResponse
from detections import EmailTelegram
import asyncio

@login_required(login_url="signin")
def index(request):
    user_object = User.objects.get(username=request.user.username)
    print("ten")
    allcam = Camera.objects.all().values()
    print("ten",allcam)
    template = loader.get_template("home.html")
    context = {
        "allcam": allcam,
        "user_object": user_object,
        "is_staff":  user_object.is_staff,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="signin")
@require_view_permission
def detailCamera(request, id):
    template = loader.get_template("detail-camera.html")
    user_object = User.objects.get(username=request.user.username)
    camera = Camera.objects.get(id_cam=id)
   
    detect_last = (
        Detection.objects.filter(name_cam=camera.name_cam)
        .order_by("-id_detect")
        .first()
    )
    detect = (
        Detection.objects.filter(name_cam=camera.name_cam)
        .order_by("-id_detect")
        .values()[:20]
    )
    cursor = connection.cursor()
    cursor.execute(
    'SELECT DISTINCT strftime("%d-%m-%Y", time_detect) AS time_detect1 '
    'FROM detections_detection '
    'ORDER BY time_detect DESC '
    'LIMIT 10;'
    )

  
    context = {
        "index_cam": id,
        "camera": camera,
        "detect": detect,
        "detect_last": detect_last,
        "cursor": cursor,
        "user_object":user_object,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='signin')
@require_view_permission
def detailHistory(request, id):
    id = id -1
    template = loader.get_template("detail-history.html")
    print("id chi so: ", id)
    queryset = Camera.objects.all()
    id_cam = queryset[id].id_cam
    camera = Camera.objects.get(id_cam=id_cam)
    # detect = Detection.objects.get(name_cam=camera.name_cam)
    detect_last = (
        Detection.objects.filter(name_cam=camera.name_cam)
        .order_by("-id_detect")
        .first()
    )


    detect = (
        Detection.objects.filter(name_cam=camera.name_cam)
        .order_by("-id_detect").values()[:20]
    )
    cursor = connection.cursor()
    cursor.execute(
    'SELECT DISTINCT strftime("%d-%m-%Y", time_detect) AS time_detect1 '
    'FROM detections_detection '
    'ORDER BY time_detect DESC '
    'LIMIT 10;'
)
    user_object = User.objects.get(username=request.user.username)
    context = {
        "camera": camera,
        "detect": detect,
        "detect_last": detect_last,
        "cursor": cursor,
        "user_object":user_object,
    }

    return HttpResponse(template.render(context, request))


# @login_required(login_url='signin')
def loadDetect(request):
    id = request.GET.get("id", None)
    print("log id came", id)
    camera = Camera.objects.get(id_cam=id)
    dct = (
        Detection.objects.filter(name_cam=camera.name_cam)
        .order_by("-id_detect")
        .values()[1]
    )

    return JsonResponse({"dct": dct}, status=200)


# @login_required(login_url='signin')
def gen(camera_stream):
    """Video streaming generator function."""
    unique_name = camera_stream.unique_name
    end = 0
    num_frames = 0
    total_time = 0
    send_detect = EmailTelegram.SendWarning()
    while True:
        time_start = time.time()

        cam_id, frame, prediction = camera_stream.get_frame(unique_name)
        if frame is None:
            break


       
        num_frames += 1
    
        time_now = time.time()
        total_time += time_now - time_start
      

        # write camera name
        cv2.putText(
            frame,
            cam_id,
            (int(0.75 * frame.shape[1]), int(0.85 * frame.shape[0])),
            0,
            1.5e-3 * frame.shape[0],
            (0, 255, 255),
            2,
        )
        
        if prediction == 1:
            print("cul", prediction)
            print(f'\t\t|____No-Fire')
        else:
            # localtime = datetime.datetime.now()
            # date_string = str(localtime.strftime("%Y-%m-%d"))
            
            nowT = datetime.datetime.now()
            date_string = str(nowT.strftime("%H:%M, %d/%m/%Y"))
            now = datetime.datetime.now().second
          
            if (now != end) & (int(now) % 59 == 0):
                end = datetime.datetime.now().second
                # send_detect.sendEmail("hoangthangdnd870@gmail.com", date_string, "Nam Lý - Trần Hưng Đạo giao Hữu Nghị",frame)
        
                # string = 'Tình trạng: Hiện tại đang có cháy \nĐịa điểm: Nam Lý - Trần Hưng Đạo giao Hữu Nghị  \nThời gian: ' + date_string + '\nXem hình ảnh để đánh giá và xử lý kịp thời.'
                # asyncio.run(send_detect.send_message_async(string, frame))
              
                # string = 'Tình trạng: Hiện tại đang có cháy \nĐịa điểm: Nam Lý - Trần Hưng Đạo giao Hữu Nghị  \nThời gian: ' + date_string + '\nVui lòng truy cập vào website để xem  hình ảnh để đánh giá và xử lý kịp thời.'
                # send_detect.sendSMS(string)
       

        # if feed_type == 'yolo':
        #     cv2.putText(frame, "FPS: %.2f" % fps, (int(0.75 * frame.shape[1]), int(0.9 * frame.shape[0])), 0,
        #                 1.5e-3 * frame.shape[0], (0, 255, 255), 2)

        frame = cv2.imencode(".jpg", frame)[
            1
        ].tobytes()  # Remove this line for test camera
        
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# @login_required(login_url='signin')
def video_feed(request, feed_type, device):
    """Video streaming route. Put this in the src attribute of an img tag."""
    cam = Camera.objects.filter(pk=device)[0]
    port = cam.port
    # port_list = (5555, 5566, 5577)
    if feed_type == "camera":
        camera_stream = import_module("detections.camera_server").Camera

        return StreamingHttpResponse(
            gen(
                camera_stream=camera_stream(cam)
            ),
            content_type="multipart/x-mixed-replace; boundary=frame",
        )

@login_required(login_url='signin')
def video_feed_one_camera(request, feed_type, device):
    """Video streaming route. Put this in the src attribute of an img tag."""

    # queryset = Camera.objects.all()
    # port_list = queryset.values_list('port', flat=True)
    # print(port_list)
    # port_list = (5555, 5566, 5577)
    cam = Camera.objects.filter(pk=device)[0]
    if feed_type == "camera":
        camera_stream = import_module("detections.camera_server").Camera

        return StreamingHttpResponse(
            gen(
                camera_stream=camera_stream(cam)
            ),
            content_type="multipart/x-mixed-replace; boundary=frame",
        )


def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            # messages.info(request, 'Credentials Invalid')
            return render(request, "signin.html")
    else:
        return render(request, "signin.html")


@login_required(login_url="signin/")
def logout(request):
    auth.logout(request)
    return redirect("signin")


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "EMAIL TAKENS")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "USERNAME TAKENS")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()
                # log user in and redirectto setting page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                # create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = CustomUser.objects.create(
                    user=user_model, id_user=user_model.id
                )
                new_profile.save()
                return redirect("")
        else:
            messages.info(request, "PASS NOT MATCHING")
            return redirect("signup")
    else:
        return render(request, "signup.html")


@login_required(login_url="signin")
def mapCamera(request):
    # create a map using Mapbox GL JS
    mapbox_access_token = "pk.eyJ1IjoiYmx1ZXJoaW5vIiwiYSI6ImNqZDJjYjZxeDFzcHUzM213MGdoOTh4dXUifQ.0St02mA2vqSMM5qsvMfngQ"
    map = {
        "access_token": mapbox_access_token,
        "style": "mapbox://styles/mapbox/streets-v11",
        "center": [-122.4194, 37.7749],  # set the initial center of the map
        "zoom": 12,  # set the initial zoom level of the map
    }
    user_object = User.objects.get(username=request.user.username)
    context = {"map": map,
               "user_object": user_object,}
    template = loader.get_template("map-camera.html")
    return HttpResponse(template.render(context, request))

# get list camera
def get(request):
    cameras = Camera.objects.all()
    camera_list = list(cameras.values())
    return JsonResponse(camera_list, safe=False)

#  search detection by time
def search_detection(request):
    user_object = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        start_time = body_data.get('start_time')
        end_time = body_data.get('end_time')
        name_cam = body_data.get('name_cam')
        print("thong tin tim kiem: ",start_time," ", end_time, " ", name_cam )
        detections = Detection.objects.filter(name_cam=name_cam, time_detect__range=[start_time, end_time])
        detection_list = list(detections.values())
        return JsonResponse(detection_list, safe=False)
    else:
        # Return an HttpResponse object indicating that the request method is not supported
        return JsonResponse({}, status=400)

@login_required(login_url="signin")
def editProfile(request):
    user_object = User.objects.get(username=request.user.username)
    print("ten")
    custom_user = CustomUser.objects.get(user_id=user_object.id)
    print("ten", custom_user.bio)
    template = loader.get_template("profile.html")
    context = {
        "user_object": user_object,
        "custom_user": custom_user,
    }
    if request.method == 'POST':
        if request.FILES.get('image') == None: 
            image = custom_user.profile_img
          
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')

        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        number_phone = request.POST.get('number_phone', '')
        address = request.POST.get('address', '')
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')
        bio = request.POST['bio']
        custom_user.profile_img = image
        custom_user.phone_number = number_phone
        custom_user.address = address
        custom_user.latitude = latitude
        custom_user.longitude = longitude
        custom_user.bio = bio
        
        custom_user.save()
        user_object.first_name = first_name
        user_object.last_name = last_name
        user_object.save()
    return HttpResponse(template.render(context, request))
