
'''Abstract camera interface.

The module contains an abstract class for the camera, to avoid direct 
dependencies on camera manufacturers' APIs. Specific implementations 
of classes for working with cameras are contained in files: 
camera_generic_web.py, camera_baumer.py and others.
'''
from abc import ABC, abstractmethod

import numpy as np


class Camera(ABC):
    '''An abstract camera class to abstract away from the specific hardware 
    implementation and the camera API used in the tools.
    '''    
    @staticmethod
    @abstractmethod
    def get_available_cameras(
        cameras_num_to_find: int = 1
        ) -> list['Camera']:
        '''
        Returns list of available cameras in system.
        
        Args:
            cameras_num_to_find (int): The number of cameras to try to find. Defaults to 1.

        Returns:
            cameras (list[Camera]): List of available cameras in system.
        '''


    @abstractmethod
    def get_image(self) -> tuple[np.ndarray|int]:
        '''
        Get image and timestamp from camera.
        
        Returns:
            image (np.ndarray): Image as numpy array (2D or 3D depending on color mode).
            timestamp (int): Timestamp in nanoseconds corresponding to the system time 
                since January 1, 1970 (in Unix format).
        '''