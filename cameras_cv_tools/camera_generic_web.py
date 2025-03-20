'''Module contains Camera class implementation for generic web camera using OpenCV.

Todo:
    * Add setting for codec in VideoWriter_fourcc
'''
import time

import cv2
import numpy as np

from .camera import Camera


class CameraWeb(Camera):
    '''Camera class implementation for generic web camera using OpenCV.
    '''
    def __init__(self, width:int=1920, height:int=1080, id:int=0):
        self.camera = cv2.VideoCapture(id, cv2.CAP_DSHOW)
        if self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            self.type = 'web'

            # Sync system and camera time
            self.system_timestamp_shift = time.time_ns()
        else:
            raise ValueError('Camera cannot be oppened')
    

    @staticmethod
    def get_available_cameras(cameras_num_to_find:int=2) -> list[Camera]:
        # Empty list to return founded cameras
        cameras = []
        
        # Try to find defined number of cameras
        for i in range(cameras_num_to_find):
            try:
                cameras.append(CameraWeb(id=i))
            except ValueError:
                # Skip camera with i id
                pass

        return cameras


    def get_image(self) -> tuple[np.ndarray|int]:
        if self.camera.isOpened:
            _, image = self.camera.read()
            timestamp = time.time_ns()
            return image, timestamp


    @property 
    def focus(self):  
        return self.camera.get(cv2.CAP_PROP_FOCUS)
        
    @focus.setter  
    def focus(self, x):  
        self.camera.set(cv2.CAP_PROP_FOCUS, x)


    @property
    def exposure(self):  
        return self.camera.get(cv2.CAP_PROP_EXPOSURE)
        
    @exposure.setter
    def exposure(self, x):  
        self.camera.set(cv2.CAP_PROP_EXPOSURE, x)


    @property
    def brightness(self):
        return self.camera.get(cv2.CAP_PROP_BRIGHTNESS)

    @brightness.setter
    def brightness(self, x):
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, x)


    @property
    def gamma(self):
        return self.camera.get(cv2.CAP_PROP_GAMMA)

    @gamma.setter
    def gamma(self, x):
        self.camera.set(cv2.CAP_PROP_GAMMA, x)


    @property
    def auto_exposure(self):
        return self.camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)

    @auto_exposure.setter
    def gain(self, x):
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, x)
