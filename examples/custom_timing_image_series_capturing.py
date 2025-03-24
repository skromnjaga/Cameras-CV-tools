'''An example of capturing from Baumer camera with custom timing: capture 50 images every 30 seconds.
The example demonstrates the possibility of recording images with a specified number and capture start time in
a programmatic way. The result is saved in sequentially numbered files, and the corresponding timestamps for images
are saved in a separate file.

The example requires NeoAPI from Baumer to work: 
https://www.baumer.com/us/en/product-overview/industrial-cameras-image-processing/software/baumer-neoapi/c/42528
'''
import json
import time
from datetime import datetime

import cv2

# Import cameras_cv_tools from relative path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from cameras_cv_tools.camera_baumer import CameraBaumer as Camera
from cameras_cv_tools.camera_generic_web import CameraWeb as Camera
from cameras_cv_tools.capturing import capture_images


if __name__ == "__main__":
    # Define capturing parameters
    IMAGES_TO_CAPTURE_IN_ONE_SERIES = 50
    TIME_PERIOD_BETWEEN_SERIES = 30 # s

    # Define path to store images
    PATH_TO_STORE_IMAGES = os.path.join(os.curdir, 'capture_images')

    # Define lambda for generating file names for images saving
    IMAGES_FILE_NAMES_MASK = lambda cam_num, img_num: f'image{img_num:05d}.png'
    # Define lambda for OpenCV named window to display capturing images
    IMSHOW_WINDOW_MASK = lambda x=None: 'Capturing images'

    # Connect to Baumer camera
    cameras = Camera.get_available_cameras(cameras_num_to_find=1)
    camera = cameras[0]
    print("Camera has been connected...")
    
    # Set defaut camera parameters
    camera.gain = 1
    camera.exposure = 20_000
    camera.frame_rate_enable = True
    camera.frame_rate = 25.0

    # Create named window to display capturing images
    cv2.namedWindow(IMSHOW_WINDOW_MASK(), cv2.WINDOW_NORMAL)
    cv2.resizeWindow(IMSHOW_WINDOW_MASK(), 1000, 800)
    
    # Create path with datetime.now to store images for current capturing
    now = datetime.now()
    images_series_path = os.path.join(PATH_TO_STORE_IMAGES, f'images_series_{now:%Y-%m-%d_%H-%M}')
    os.makedirs(images_series_path)

    # Create dictionary to store image series data
    images_series = {}
    images_series['CreatedDate'] = f'{now}'
    
    image_series_file = os.path.join(images_series_path, 'images_series.json')

    # Variables to store capturing process data
    recorded_info_all = []
    images_captured = 0
    start_capture = False

    start_time = time.perf_counter()

    try:
        while True:
            # Capture image from camera
            img, _ = camera.get_image()

            # Display captured image
            cv2.imshow(IMSHOW_WINDOW_MASK(_), img)
            k = cv2.waitKey(1)

            if k == ord(' ') or time.perf_counter() - start_time > TIME_PERIOD_BETWEEN_SERIES:
                # By pressing space (' ') or time beetween capturing > TIME_PERIOD_BETWEEN_SERIES begin new capturing
                start_time = time.perf_counter()
                start_capture = True
                images_to_capture = IMAGES_TO_CAPTURE_IN_ONE_SERIES
            elif k == ord('r'):
                # Special option to run continiuos capturing without images count limit by pressing 'r' button
                start_capture = True
                images_to_capture = 0
            elif k == ord('q'):
                # By pressing 'q' button - end script
                break

            if start_capture:
                # Start recording images from camera
                recorded_info = capture_images(
                    camera,
                    path_to_store_images=images_series_path,
                    images_file_names_mask=IMAGES_FILE_NAMES_MASK,
                    images_to_capture=images_to_capture,
                    start_image_number=images_captured,
                    imshow_windows_mask=IMSHOW_WINDOW_MASK)
                
                # Add data from capturing (images file names and timestamps) to images series dictionary
                recorded_info_all.extend(recorded_info)
                # Calculate total images count with for sequential numbering of files 
                images_captured = images_captured + len(recorded_info)

                start_capture = False

        # Close camera connection
        camera.camera.Disconnect()
    finally:
        # Store images file names and timestamps to images series dictionary
        images_series['StoredImages'] = recorded_info_all

        # Save images series data to file
        with open(image_series_file, 'x', encoding='utf8') as image_series_file:
            json.dump(images_series, image_series_file, indent=4)
            print('Images series file saved')
