import cv2
from PIL import Image
import time
import yaml
import torch
import os
import datetime
import torchvision.transforms as transforms
from detections.modelsDetection import shufflenetv2
from detections.models import Detection
import threading


class CameraDetectionFire(object):
  def __init__(self):
    with open('detections/config.yml') as f:
      self.config = yaml.load(f, Loader=yaml.FullLoader)
      args = self.config
      global device
    if args["cpu"]:
        device = torch.device('cpu')
    else:
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    if args["cpu"] and args["trt"]:
        print(f'\n>>>>TensorRT runs only on gpu. Exit.')
        exit()

    print('\n\nBegin {fire, no-fire} classification :')
    self.np_transforms = self.data_transform(self.config["models"]["md1"])
    
    # model load
    if self.config["models"]["md1"] == "shufflenetonfire":
        self.model = shufflenetv2.shufflenet_v2_x0_5(
            pretrained=False, layers=[
                4, 8, 4], output_channels=[
                24, 48, 96, 192, 64], num_classes=1)
        if self.config["weight"]:
            w_path = self.config["weight"]
        else:
            w_path = 'detections/weights/shufflenet_ff.pt'
        self.model.load_state_dict(torch.load(w_path, map_location=device))
    else:
        print('Invalid Model.')
        exit()

    print(f'|__Model loading: {self.config["models"]["md1"]}')

    self.model.eval()
    self.model.to(device)

  # data transform
  def data_transform(self, model):
    # transforms needed for shufflenetonfire
    if model == 'shufflenetonfire':
      np_transforms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
      ])
    # transforms needed for nasnetonfire
    if model == 'nasnetonfire':
      np_transforms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
      ])

    return np_transforms

  # read/process image and apply tranformation
  def read_img(self, frame):
    small_frame = cv2.resize(frame, (224, 224), cv2.INTER_AREA)
    small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    small_frame = Image.fromarray(small_frame)
    small_frame = self.np_transforms(small_frame).float()
    small_frame = small_frame.unsqueeze(0)
    small_frame = small_frame.to(device)

    return small_frame

  # model prediction on image
  def run_model_img(self, frame):
    output = self.model(frame)
    pred = torch.round(torch.sigmoid(output))
    print(torch.sigmoid(output))
    return pred
  
  def detection_fire(self, frame):
    fps = []
    start_t = time.time()
    small_frame = self.read_img(frame)
    # model prediction
    prediction = self.run_model_img(small_frame)
    stop_t = time.time()
    fps_frame = int(1 / (stop_t - start_t))
    fps.append(fps_frame)
    sum = 0
    localtime = datetime.datetime.now()
    return prediction, frame
  
fire_detector = CameraDetectionFire()