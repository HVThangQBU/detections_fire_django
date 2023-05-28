from imutils.video import VideoStream, WebcamVideoStream
import imagezmq
# from canhbao.models.models import Camera

path = "rtsp://user:Admin123@ndhoa92camhaithanhltd.ddns.net:554/profile2/media.smp"  # change to your IP stream address
cap = VideoStream(path)


sender = imagezmq.ImageSender(connect_to='tcp://localhost:5555')  # change to IP address and port of server thread
cam_id = 'Camera 1'  # this name will be displayed on the corresponding camera stream

stream = cap.start()
i = 0
while True:

    frame = stream.read()
    print('Sending ' + str(i))
    i = i + 1
    sender.send_image(cam_id, frame)

# read video
# from asyncore import loop
# import cv2
# import imagezmq
# import yaml

# file = "demo/video2.mp4"
# cap = cv2.VideoCapture(file)
# sender = imagezmq.ImageSender(connect_to='tcp://localhost:5555')
# # change to IP address and port of server thread
# cam_id = 'Camera 1'  # this name will be displayed on the corresponding camera stream

# #stream = cap.read()
# i = 0
# while True:
#     ret, frame = cap.read()
#     if ret:
#       # if a frame was returned, send it
#       sender.send_image(cam_id, frame)
#       i = i +1
#       print(i)


#     else:
#       # if no frame was returned, either restart or stop the stream
#       if loop:
#         cap = cv2.VideoCapture(file)
#       else:
#         break
