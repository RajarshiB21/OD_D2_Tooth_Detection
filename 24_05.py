# -*- coding: utf-8 -*-
"""24/05.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1i6J0F114yTRTe9OHBMCn8n1KAhTzP1G2
"""

!pip install pyyaml==5.1

import torch
TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
# Install detectron2 that matches the above pytorch version
# See https://detectron2.readthedocs.io/tutorials/install.html for instructions
!pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/$CUDA_VERSION/torch$TORCH_VERSION/index.html
# If there is not yet a detectron2 release that matches the given torch + CUDA version, you need to install a different pytorch.

# exit(0)  # After installation, you may need to "restart runtime" in Colab. This line can also restart runtime

from google.colab import drive
drive.mount('/content/drive')

!pip install 'git+https://github.com/facebookresearch/detectron2.git'

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

import numpy as np
import os,json,cv2,random
from google.colab.patches import cv2_imshow

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

from detectron2.data.datasets import register_coco_instances
register_coco_instances("Fillings", {}, "/content/drive/MyDrive/Dental/Fillings/train.json", "/content/drive/MyDrive/Dental/Fillings/train")

sample_metadata = MetadataCatalog.get("Fillings")
dataset_dicts = DatasetCatalog.get("Fillings")

import random

for d in random.sample(dataset_dicts, 4):
    img = cv2.imread(d["file_name"])
    visualizer = Visualizer(img[:, :, ::-1], metadata=sample_metadata, scale=0.25)
    vis = visualizer.draw_dataset_dict(d)
    cv2_imshow(vis.get_image()[:, :, ::-1])

from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
import os

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
cfg.DATASETS.TRAIN = ("Fillings",)
cfg.DATASETS.TEST = ()   # no metrics implemented for this dataset
cfg.DATALOADER.NUM_WORKERS = 2
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")# initialize from model zoo
cfg.SOLVER.IMS_PER_BATCH = 2
cfg.SOLVER.BASE_LR = 0.02
cfg.SOLVER.MAX_ITER = 200   # 300 iterations seems good enough, but you can certainly train longer
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # faster, and good enough for this toy dataset
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # 3 classes (Person, Helmet, Car)

os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=True)
trainer.train()

cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
cfg.DATASETS.TEST = ("Fillings",)
predictor = DefaultPredictor(cfg)

from detectron2.utils.visualizer import ColorMode

for d in random.sample(dataset_dicts, 4):    
    im = cv2.imread(d["file_name"])
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1],
                   metadata=sample_metadata, 
                   scale=1, 
                   instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
    )
    v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2_imshow(v.get_image()[:, :, ::-1])

def show_image(imm):

  image = cv2.imread(imm)
  predictor = DefaultPredictor(cfg)
  outputs = predictor(image)
  viz = Visualizer(image[:,:,::-1], 
                   MetadataCatalog.get(cfg.DATASETS.TRAIN[0]),
                   scale=0.25) #images are loaded by opencv in BGR format and hence need to be converted to RGB
  output = viz.draw_instance_predictions(outputs["instances"].to("cpu"))
  cv2_imshow(output.get_image()[:,:,::-1])#Converted back to BGR

import numpy as np

list_images = os.listdir('/content/drive/MyDrive/Dental/Fillings/test')
arr_images = np.asarray(list_images)

def show_image(imm):

  image = cv2.imread(imm)
  predictor = DefaultPredictor(cfg)
  outputs = predictor(image)
  viz = Visualizer(image[:,:,::-1], 
                   MetadataCatalog.get(cfg.DATASETS.TRAIN[0]),
                   scale=1) #images are loaded by opencv in BGR format and hence need to be converted to RGB
  output = viz.draw_instance_predictions(outputs["instances"].to("cpu"))
  cv2_imshow(output.get_image()[:,:,::-1])#Converted back to BGR

base_path = '/content/drive/MyDrive/Dental/Fillings/test'

for i in range(len(arr_images)):

  image_path = os.path.join(base_path,list_images[i])
  show_image(image_path)

