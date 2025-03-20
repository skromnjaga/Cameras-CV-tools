'''Module with functions for capturing images from one or several cameras using multiprocessing.
Module allows to realize synchronous capturing of images from several cameras at a higher speed 
than when using direct image saving.

An example of how to use the module can be found in synchronized_baumer_camera_capture.py.
'''
import os
import time
from collections.abc import Callable

from queue import Empty
import multiprocessing as mp
from multiprocessing import Queue, Manager
from multiprocessing.managers import ValueProxy

import cv2

from .camera import Camera


def store_images_process(
        queue: Queue, 
        files_stored: ValueProxy[int]
    ) -> None:
    '''The function performs storing images from the queue to files.
    Used for multiprocessing storing images from capture_images function.

    Args:
        queue (Queue): queue of images and file names to store them
        files_stored (ValueProxy[int]): count of images stored by the function
    '''    

    while True:
        try:
            file_name, img = queue.get(timeout=2)
        except Empty:
            # Queue closed
            break
        
        cv2.imwrite(file_name, img)
        
        files_stored.value = files_stored.value + 1


def capture_images(
        cameras: Camera|list[Camera],
        path_to_store_images: str,
        images_to_capture: int = 0,
        start_image_number: int = 0,
        images_file_names_mask: Callable[[int, int], str] = lambda cam_num, image_num: f'camera_{cam_num}_{image_num}.png',
        imshow_windows_mask: Callable[[int], str] = lambda cam_num: f'camera_{cam_num}',
        processes_to_run: int = 4
    ) -> list[list[tuple[int, str]]]:
    '''The function simultaneous captures images from the passed camera list and saving them to files.
    To speed up the saving process multiprocessing is used. 

    Args:
        cameras (Camera | list[Camera]): camera or list of cameras from which capturing performed.
        path_to_store_images (str): path to sotre captured images.
        images_to_capture (int, optional): number of images to capture, if set to 0 infinity number of images is captured.
        Defaults to 0.
        start_image_number (int, optional): start image number used in file mask to generate storing file name.
        Can be used to continue storing files in several function calls. Defaults to 0.
        images_file_names_mask (Callable[[int, int], str], optional): lambda function with mask to generate file name to
        store images. Lambda function use camera num in list and current image number as parameters.
        Defaults to lambda cam_num, image_num: f'camera_{cam_num}_{image_num}.png'.
        imshow_windows_mask (Callable[[int], str]): lambda function with mask to generate OpenCV named window to display
        capturing images. Lambda function use camera num as parameter. Can be used to display capturing images in
        named windows defined outside function. Defaults to lambda cam_num: f'camera_{cam_num}'.
        processes_to_run (int, optional): number of multiprocessing process to use in storing images to files.
        Defaults to 4.

    Returns:
        recorded_info (list[list[tuple[int, str]]]): list of list of simultaneous captured images for defined cameras with
        images timestamps and file names.
    '''    

    # If one camera passed, then create list for unification
    if isinstance(cameras, Camera):
        cameras = [cameras]
    
    images_captured = 0
    
    files_to_store_queue = Queue()

    manager = Manager()
    files_stored = manager.Value('i', 0)

    processes = [
        mp.Process(target=store_images_process, args=[files_to_store_queue, files_stored]) for _ in range(processes_to_run)]

    # Start images storing processes
    [proc.start() for proc in processes]
    
    # Create windows to show captured images
    for cam_num, camera in enumerate(cameras):
        cv2.namedWindow(imshow_windows_mask(cam_num), cv2.WINDOW_NORMAL) 
        cv2.resizeWindow(imshow_windows_mask(cam_num), 1000, 800)

    images_captured_start = images_captured
    files_stored_start = files_stored.value
    start = time.perf_counter()
    recorded_info = []

    while (images_to_capture == 0 or images_captured < images_to_capture):

        sync_recorded_info = []

        for cam_num, camera in enumerate(cameras):
            img, timestamp = camera.get_image()
            
            cv2.imshow(imshow_windows_mask(cam_num), img)

            file_name = images_file_names_mask(cam_num, images_captured + start_image_number)
            file_path = os.path.join(path_to_store_images, file_name)

            files_to_store_queue.put((file_path, img))
            
            sync_recorded_info.extend((timestamp, file_name))

        recorded_info.append(sync_recorded_info)
        
        images_captured = images_captured + 1

        k = cv2.waitKey(1)

        if time.perf_counter() - start > 1:
            fps_read = (images_captured - images_captured_start) / (time.perf_counter() - start)
            fps_write = (files_stored.value - files_stored_start) / (time.perf_counter() - start)
            print(f'Images captured {images_captured}, FPS {fps_read:.1f}, write speed {fps_write:.1f}, queue size {files_to_store_queue.qsize()}')

            images_captured_start = images_captured
            files_stored_start = files_stored.value
            start = time.perf_counter() 
        
        if k == 27:  # Escape
            break

    print(f'Stopping capturing, waiting for {files_to_store_queue.qsize()} files to write in parallel processes..')
    files_to_store_queue.close()

    for process in processes:
        process.join()

    print(f'Captured stopped: {images_captured * len(cameras)} images captured, {files_stored.value} files written')

    return recorded_info