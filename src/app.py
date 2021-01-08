import torch
import cv2
import numpy as np
import mss

from torch import nn
from torchvision.transforms import ToTensor, Resize, Pad

from camera import Camera
from displayer import Displayer


class App:
    def __init__(self, model_checkpoint, background_output):
        self.tensor = ToTensor()
        device = torch.device("cuda")
        self.precision = torch.float16

        model = torch.jit.load(model_checkpoint)
        model.backbone_scale = 0.25
        model.refine_mode = "sampling"
        model.refine_sample_pixels = 80_000

        self.model = model.to(device)

        self.width, self.height = 1280, 720
        w, h = int(self.width / 2), int(self.height / 2)
        self.padding = [0, 0, w, h]
        self.size = [h, w]

        self.cam = Camera(width=self.width, height=self.height)
        self.dsp = Displayer("MattingV2", w, h)
        
        self.bgr = None
        tgt = cv2.imread(background_output)
        tgt = self.cv2_frame_to_cuda(tgt)
        tgt = Resize([self.height, self.width])(tgt)

    def step(self, sct):
        if self.dsp.state == True:
            self.bgr = None
            frame = self.cam.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.dsp.step(frame)
        elif self.bgr == None:
            frame = self.cam.read()
            self.bgr = self.cv2_frame_to_cuda(frame)
        else:
            pad0 = Pad(self.padding, 0)
            pad1 = Pad(self.padding, 1)
            resize = Resize(self.size)

            frame = self.cam.read()
            src = self.cv2_frame_to_cuda(frame)
            pha, fgr = self.model(src, self.bgr)[:2]

            tgt = self.cv2_frame_to_cuda(np.array(sct.grab(sct.monitors[1])))
            tgt = Resize([self.height, self.width])(tgt)

            layer1 = pad0(resize(pha * fgr))
            layer2 = pad1(resize(1 - pha)) * tgt
            res = layer1 + layer2
            res = res.mul(255).byte().cpu().permute(0, 2, 3, 1).numpy()[0]

            x, y, w, h = self.dsp.step(res)
            left, top, right, bottom = x, y, self.width - (x + w), self.height - (y + h)

            self.padding = [left, top, right, bottom]
            self.size = [h, w]

    def cv2_frame_to_cuda(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.tensor(frame).unsqueeze_(0).cuda().to(self.precision)

    def run(self):
        with torch.no_grad():
            with mss.mss(display=":0.0") as sct:
                while True:
                    self.step(sct)


app = App("torchscript_mobilenetv2_fp16.pth", "demo_image.jpg")
app.run()