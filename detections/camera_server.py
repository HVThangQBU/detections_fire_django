import cv2
import time


from detections.base_camera import BaseCamera
import datetime
import os
from django.utils import timezone
from detections.detectionfire import fire_detector
from detections.models import Detection
# from detections.models import Camera as myCam

class Camera(BaseCamera):
   
    @staticmethod
    def server_frames(camera):
        num_frames = 0
        total_time = 0
        end = 0


        detector = fire_detector
        cam_id = camera.name_cam
        cap = cv2.VideoCapture(camera.urlRTSP)
        loop = not camera.urlRTSP.startswith("rtsp://")
        while True:  # main loop
            time_start = time.time()

            ret, frame = cap.read()
            # print("ret", ret)
            if not ret:
                if loop:
                    cap = cv2.VideoCapture(camera.urlRTSP)
                    continue
                else:
                    break
            # print("camera ID", cam_id)
            num_frames += 1

            prediction, frame = detector.detection_fire(frame)
            localtime = datetime.datetime.now()
            height, width, _ = frame.shape
            now = datetime.datetime.now()
            # Định dạng chuỗi ngày giờ
            formatted_date_time = now.strftime("%d/%m/%Y %H:%M:%S")
            cv2.putText(
                frame,
                "Time: " + str(formatted_date_time),
                (int(20), int(15 * 5e-3 * frame.shape[0])),
                0,
                2e-3 * frame.shape[0],
                (255, 255, 255),
                2,
            )
            if prediction == 1:
        
                # cv2.putText(
                #     frame,
                #     "No-Fire",
                #     (int(width / 16), int(height / 4)),
                #     cv2.FONT_HERSHEY_SIMPLEX,
                #     1,
                #     (0, 255, 00),
                #     2,
                #     cv2.LINE_AA,
                # )
                print("no Fire")
            else:
                # print("cul", prediction)
                # print(f'\t\t|____Fire')
                # try:
                #     os.mkdir("media/detect_image/" + cam_id)
                # except:
                #     print("An exception occurred")

                folder_path = "detections/media/detect_image/" + cam_id

                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    print("Thư mục đã tồn tại.")
                else:
                  os.mkdir("media/detect_image/" + cam_id)
                # try:

                    # date_string = localtime.strftime("%Y-%m-%d")
                    # now = datetime.datetime.now().second

                #     # print(datestring, "cam id", cam_id)
                #     path = "media/detect_image/" + cam_id + "/" + date_string

                #     os.mkdir("media/detect_image/" + cam_id + "/" + date_string)
                # except:
                #     print("An exception occurred")
                date_string = localtime.strftime("%Y-%m-%d")
                now = datetime.datetime.now().second
                path = "detections/media/detect_image/" + cam_id + "/" + date_string
                if os.path.exists(path) and os.path.isdir(path):
                    print("Thư mục đã tồn tại.")
                else:
                  os.mkdir(path)    

                # today = datetime.datetime.now()
                # print(today.strftime("%Y-%m-%d"))

                # if int(localtime.second) % 2 == 0:
             
                if (now % 5 == 0):
                    out_path = "detections/media/detect_image/" + cam_id + "/" + date_string
                    date_full = localtime.strftime("%Y-%m-%d %H:%M")
                    localtime.strftime("%d %H-%M-%S")
                    frame_name = localtime.strftime("%d %H-%M-%S") + ".jpg"
                    cv2.imwrite(os.path.join(out_path, frame_name), frame)
                    name = u"Phát hiện cháy"
                    content = u"Có cháy đang diễn ra"
                   
                    print("===========================",date_full )
                    end = datetime.datetime.now().second
                    dec = Detection.objects.create(
                        name_detect=name,
                        name_cam=cam_id,
                        content=content,
                        image_detect="detect_image/"
                        + cam_id
                        + "/"
                        + date_string
                        + "/"
                        + frame_name,
                        time_detect=date_full,
        
                    )
                    dec.save()
                if (now  % 50 == 0):
                    # print("time end",end)
                    # print(str(threading.current_thread().ident) + " Phat hien chay " + str(today))
                    cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), 30)
                # cv2.putText(
                #     frame,
                #     "Fire",
                #     (int(width / 16), int(height / 4)),
                #     cv2.FONT_HERSHEY_SIMPLEX,
                #     1,
                #     (0, 0, 255),
                #     2,
                #     cv2.LINE_AA,
                # )
            # time_now = time.time()
            # total_time += time_now - time_start
            # fps = num_frames / total_time
            # uncomment below to see FPS of camera stream\

            # cv2.putText(
            #     frame,
            #     "FPS: %.2f" % fps,
            #     (int(20), int(40 * 5e-3 * frame.shape[0])),
            #     0,
            #     2e-3 * frame.shape[0],
            #     (255, 255, 255),
            #     2,
            # )

            yield cam_id, frame, prediction
