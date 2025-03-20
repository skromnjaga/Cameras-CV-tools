'''Module contains Camera class implementation for Baumer cameras using NeoAPI.

The module requires NeoAPI from Baumer to work: 
https://www.baumer.com/us/en/product-overview/industrial-cameras-image-processing/software/baumer-neoapi/c/42528
'''
import time
import numpy as np

import neoapi # type: ignore

from .camera import Camera


class CameraBaumer(Camera):
    '''Camera class implementation for Baumer cameras using NeoAPI.

    Note:
        The module requires NeoAPI from Baumer to work.
    '''
    def __init__(self, camera: neoapi.Cam, serial_number: str = None):
        self.camera = camera
        
        if serial_number is not None:
            self.camera.Connect(serial_number)            
        else:
            self.camera.Connect()
        self.type = 'baumer'
        
        # Sync system and camera time
        if self.camera.f.TimestampReset.IsAvailable():
            self.camera.f.TimestampReset.Execute()        
            self.system_timestamp_shift = time.time_ns()
        else:
            self.system_timestamp_shift = 0


    @staticmethod
    def get_available_cameras(
        cameras_num_to_find: int = 1, 
        cameras_serial_numbers: list[str] = []
        ) -> list[Camera]:
        # Empty list to return founded cameras
        cameras = []
        
        while cameras_num_to_find > 0:
            # Get next camera from neoapi
            if len(cameras_serial_numbers) == 0:
                camera = CameraBaumer(neoapi.Cam())
            else:
                # Connect devices by serial number
                camera = CameraBaumer(neoapi.Cam(), cameras_serial_numbers[-1])
                if camera.camera.f.DeviceSerialNumber.value not in cameras_serial_numbers:
                    raise Exception(f'Error, camera serial number is not {cameras_serial_numbers[-1]}')
                cameras_serial_numbers.pop()

            cameras.append(camera)
            cameras_num_to_find = cameras_num_to_find - 1

        return cameras


    def get_image(self) -> tuple[np.ndarray|int]:
        # Get image from Baumer camera
        baumer_image = self.camera.GetImage()

        # Convert it to numpy array
        img = baumer_image.GetNPArray()
        img = img.reshape(img.shape[0], img.shape[1])
        
        # Get timestamp in system time (approximately)
        timestamp = baumer_image.GetTimestamp() + self.system_timestamp_shift
        return img, timestamp


    @property
    def exposure(self):
        return self.camera.f.ExposureTime.value

    @exposure.setter
    def exposure(self, x):
        self.camera.f.ExposureTime.value = x


    @property
    def gain(self):
        return self.camera.f.Gain.value

    @gain.setter
    def gain(self, x):
        self.camera.f.Gain.value = x


    @property
    def gamma(self):
        return self.camera.f.Gamma.value

    @gamma.setter
    def gamma(self, x):
        self.camera.f.Gamma.value = x


    @property
    def exposure_auto(self):
        return self.camera.f.ExposureAuto.value

    @exposure_auto.setter
    def exposure_auto(self, x):
        self.camera.f.ExposureAuto.value = x


    @property
    def trigger_mode(self):
        return self.camera.f.TriggerMode.value

    @trigger_mode.setter
    def trigger_mode(self, x):
        self.camera.f.TriggerMode.value = x


    @property
    def line_selector(self):
        return self.camera.f.LineSelector.value

    @line_selector.setter
    def line_selector(self, x):
        self.camera.f.LineSelector.value = x


    @property
    def line_mode(self):
        return self.camera.f.LineMode.value

    @line_mode.setter
    def line_mode(self, x):
        self.camera.f.LineMode.value = x


    @property
    def line_source(self):
        return self.camera.f.LineSource.value

    @line_source.setter
    def line_source(self, x):
        self.camera.f.LineSource.value = x


    @property
    def frame_rate_enable(self):
        return self.camera.f.AcquisitionFrameRateEnable.value

    @frame_rate_enable.setter
    def frame_rate_enable(self, x):
        self.camera.f.AcquisitionFrameRateEnable.value = x


    @property
    def frame_rate(self):
        return self.camera.f.AcquisitionFrameRate.value

    @frame_rate.setter
    def frame_rate(self, x):
        self.camera.f.AcquisitionFrameRate.value = x