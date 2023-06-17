#!/usr/bin/python
import cv2
import numpy as np
import os
import argparse
from datetime import datetime
import re
from tqdm import tqdm

def create_dayline_image(folder, slices):
    # Get the list of all files in directory tree at given path
    list_of_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder) for f in filenames if f.endswith(".jpg")]

    # Sort files by datetime embedded in filename
    list_of_files.sort(key = lambda x: datetime.strptime(re.search(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}", x).group(), "%Y_%m_%d_%H_%M_%S"))

    num_of_files = len(list_of_files)

    # We want 'slices' number of slices. If there are less images, use that number
    slices = slices if num_of_files >= slices else num_of_files

    # Divide total images into slices
    images_per_slice = num_of_files // slices

    final_image = None

    for i in tqdm(range(slices), desc="Creating day slices"):
        # Read image
        img = cv2.imread(list_of_files[i*images_per_slice])
        
        # Slice image vertically into 'slices' number of parts
        width = img.shape[1]
        slice_width = width // slices
        img_slice = img[:, i*slice_width:(i+1)*slice_width]
        
        # Stack slices horizontally
        if final_image is None:
            final_image = img_slice
        else:
            final_image = np.hstack((final_image, img_slice))

    # Save the final image
    date = re.search(r"\d{4}_\d{2}_\d{2}", list_of_files[0]).group()
    date = date.replace("_", "-")
    temp_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'temp')
    os.makedirs(temp_folder, exist_ok=True)
    save_path = os.path.join(temp_folder, "dayline-" + date + ".jpg")
    cv2.imwrite(save_path, final_image)
    
    # Return the path of the final image
    return save_path

# If the script is run directly, use argparse to parse folder and slices
if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, required=True, help="Folder with images")
    parser.add_argument("--slices", type=int, default=48, help="Number of slices to create")
    args = parser.parse_args()
    
    create_dayline_image(args.folder, args.slices)
