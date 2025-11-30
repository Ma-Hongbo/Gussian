import cv2
import os
import argparse
import re
from collections import defaultdict
from tqdm import tqdm

# ================= DEFAULT CONFIGURATION =================
DEFAULT_FPS = 10
# =======================================================

def parse_filename(filename):
    """
    Parses the filename to extract camera ID and iteration number.
    Expected format: pano_camera{i}_frame_{xxxxx}.png
    Example: pano_camera0_frame_00001.png
    
    Returns:
        camera_id (str): e.g., "pano_camera0"
        iteration (int): e.g., 1
    """
    # [修改说明] 正则表达式已更新
    # 匹配逻辑：
    # 1. (pano_camera\d+) -> Group 1: 捕获 pano_camera 后跟数字 (例如 "pano_camera0")
    # 2. _frame_          -> 字面量匹配中间的 "_frame_"
    # 3. (\d+)            -> Group 2: 捕获帧编号数字 (例如 "00001")
    match = re.search(r"(pano_camera\d+)_frame_(\d+)", filename)
    
    if match:
        camera_id = match.group(1)  # e.g., pano_camera0
        iteration = int(match.group(2))  # e.g., 00001 -> 1
        return camera_id, iteration
    return None, None

def get_grouped_images(directories):
    """
    Scans multiple directories, parses filenames, and groups them by Camera ID.
    
    Returns:
        dict: { "pano_camera0": [(iter, filepath), ...], "pano_camera1": [...] }
    """
    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    grouped_files = defaultdict(list)

    for directory in directories:
        if not os.path.exists(directory):
            print(f"Warning: Directory not found: {directory}")
            continue
        
        print(f"Scanning directory: {directory} ...")
        files = os.listdir(directory)
        
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_extensions:
                full_path = os.path.join(directory, f)
                
                # Parse the filename
                camera_id, iteration = parse_filename(f)
                
                if camera_id is not None:
                    # Store as tuple (iteration, full_path) for sorting later
                    grouped_files[camera_id].append((iteration, full_path))
                else:
                    # Optional: Print warning if file doesn't match pattern
                    # print(f"Skipping non-matching file: {f}")
                    pass

    return grouped_files

def create_video_for_camera(camera_id, image_data_list, output_dir, fps):
    """
    Generates a video for a specific camera, sorted by iteration.
    """
    # 1. Sort by iteration number (the first element of the tuple)
    # This merges train and test images into a single timeline based on frame number
    image_data_list.sort(key=lambda x: x[0])
    
    # Extract just the file paths after sorting
    image_paths = [item[1] for item in image_data_list]

    if not image_paths:
        return

    output_path = os.path.join(output_dir, f"{camera_id}.mp4")

    # Read first image to get dimensions
    first_img = cv2.imread(image_paths[0])
    if first_img is None:
        print(f"Error: Could not read image {image_paths[0]}")
        return
    
    height, width, layers = first_img.shape
    size = (width, height)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    print(f"Processing Video: {camera_id} ({len(image_paths)} frames)...")
    
    for img_path in tqdm(image_paths, leave=False, desc=camera_id):
        img = cv2.imread(img_path)
        if img is None:
            continue
        
        # Resize if necessary
        if (img.shape[1], img.shape[0]) != size:
            img = cv2.resize(img, size)
            
        out.write(img)

    out.release()
    print(f"Saved: {output_path}")

def parse_args():
    parser = argparse.ArgumentParser(description="Merge train/test images into videos grouped by Camera ID.")
    
    parser.add_argument("--train_dir", type=str, required=True, help="Path to training images")
    parser.add_argument("--test_dir", type=str, required=True, help="Path to testing images")
    parser.add_argument("--out_dir", type=str, required=True, help="Path to save output videos")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help=f"Frames per second (default: {DEFAULT_FPS})")
    
    return parser.parse_args()

def main():
    args = parse_args()

    # 1. Prepare output dir
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    # 2. Group images from both directories
    grouped_data = get_grouped_images([args.train_dir, args.test_dir])
    
    sorted_camera_ids = sorted(grouped_data.keys())
    print(f"\nFound {len(sorted_camera_ids)} unique cameras: {sorted_camera_ids}")

    if len(sorted_camera_ids) == 0:
        print("Error: No valid images found matching 'pano_camera{i}_frame_{xxxxx}' pattern.")
        return

    # 3. Generate one video per camera
    print("\nStarting video generation...")
    for camera_id in sorted_camera_ids:
        create_video_for_camera(
            camera_id, 
            grouped_data[camera_id], 
            args.out_dir, 
            args.fps
        )

    print("\nAll videos processed successfully!")

if __name__ == "__main__":
    main()
