'''An example of synchronized capturing from two Baumer cameras with capture_images function.

The example requires NeoAPI from Baumer to work: 
https://www.baumer.com/us/en/product-overview/industrial-cameras-image-processing/software/baumer-neoapi/c/42528
'''
import json

import neoapi # type: ignore

# Import cameras_cv_tools from relative path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cameras_cv_tools.camera_baumer import CameraBaumer
from cameras_cv_tools.capturing import capture_images


def initialize_cameras(
    cam_to_found_number: int = 1, 
    cameras_serial_numbers: list[str] = []
    ) -> list[CameraBaumer]:

    # Synchronize two Baumer cameras, first set as trigger signal output (master) and second as
    # triggered by input signal (slave) 
    cameras = CameraBaumer.get_available_cameras(cam_to_found_number, cameras_serial_numbers)
    for i, camera in enumerate(cameras):
        if i == 0: 
            camera.line_selector = neoapi.LineSelector_Line1 
            camera.line_mode = neoapi.LineMode_Output 
            camera.line_source = neoapi.LineSource_ExposureActive 
         
        # Set next camera as slave for trigger wait 
        if i != 0: 
            camera.trigger_mode = neoapi.TriggerMode_On

    return cameras


if __name__ == "__main__":
    RESULTS_PATH = r"results"
    
    cameras = initialize_cameras(cam_to_found_number=2)
    print("Camera has been connected...")
    
    # Set cameras' capturing parameters
    for camera in cameras:
        camera.gain = 2
        camera.exposure = 10_000
        camera.frame_rate_enable = True
        camera.frame_rate = 30.0

    recorded_info = capture_images(cameras)

    # Store recorded info to JSON for using in futher processing
    with open('recorded_data.json', 'w') as fp:
        json.dump(recorded_info, fp, indent=4)
        print('Recorded data is saved to recorded_data.json') 