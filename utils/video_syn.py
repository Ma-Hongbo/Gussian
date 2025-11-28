import cv2
import os
import math
import argparse
from tqdm import tqdm

# ================= DEFAULT CONFIGURATION =================
# These are used if you don't provide arguments via command line
DEFAULT_FPS = 30
DEFAULT_NUM_VIDEOS = 12
DEFAULT_PATTERN_TRAIN = 7
DEFAULT_PATTERN_TEST = 1
# =======================================================

def get_image_files(directory):
    """
    Retrieves all image files from a directory and sorts them by filename.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    # List comprehension to filter files by extension
    files = [
        os.path.join(directory, f) 
        for f in os.listdir(directory) 
        if os.path.splitext(f)[1].lower() in valid_extensions
    ]
    # Sort files naturally/alphabetically to ensure correct sequence
    files.sort(key=lambda x: x.lower())
    return files

def create_video_from_paths(image_paths, output_path, fps):
    """
    Generates an MP4 video from a list of image paths.
    """
    if not image_paths:
        print(f"Warning: No images for {output_path}, skipping.")
        return

    # Read the first image to determine video resolution
    first_img = cv2.imread(image_paths[0])
    if first_img is None:
        print(f"Error: Could not read image {image_paths[0]}")
        return
    
    height, width, layers = first_img.shape
    size = (width, height)

    # Initialize VideoWriter using mp4v codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    print(f"Processing: {output_path} ({len(image_paths)} frames)...")
    
    # Use tqdm for a progress bar
    for img_path in tqdm(image_paths, leave=False):
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Skipping corrupted image {img_path}")
            continue
            
        # Resize image if dimensions do not match the first frame
        if (img.shape[1], img.shape[0]) != size:
            img = cv2.resize(img, size)
            
        out.write(img)

    out.release()
    print(f"Done: {output_path}")

def parse_args():
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser(description="Merge train and test renders into sequential videos.")
    
    # Required arguments for paths
    parser.add_argument("--train_dir", type=str, required=True, help="Path to the folder containing training images")
    parser.add_argument("--test_dir", type=str, required=True, help="Path to the folder containing testing images")
    parser.add_argument("--out_dir", type=str, required=True, help="Path to save the generated videos")

    # Optional arguments (with defaults)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help=f"Frames per second (default: {DEFAULT_FPS})")
    parser.add_argument("--num_videos", type=int, default=DEFAULT_NUM_VIDEOS, help=f"Number of video splits (default: {DEFAULT_NUM_VIDEOS})")
    
    return parser.parse_args()

def main():
    # 1. Parse arguments
    args = parse_args()

    # 2. Create output directory if it doesn't exist
    if not os.path.exists(args.out_dir):
        print(f"Creating output directory: {args.out_dir}")
        os.makedirs(args.out_dir)

    # 3. Load and sort file lists
    print("Reading file lists...")
    try:
        train_files = get_image_files(args.train_dir)
        test_files = get_image_files(args.test_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    print(f"Found Train images: {len(train_files)}")
    print(f"Found Test images: {len(test_files)}")

    # 4. Interleave images based on the 7:1 pattern
    full_sequence = []
    t_idx = 0
    v_idx = 0
    
    # Loop until we run out of images in the shorter list or train list is exhausted
    while t_idx < len(train_files) and v_idx < len(test_files):
        # Add a chunk of train images
        chunk_train = train_files[t_idx : t_idx + DEFAULT_PATTERN_TRAIN]
        full_sequence.extend(chunk_train)
        t_idx += len(chunk_train)
        
        # Add a chunk of test images
        if v_idx < len(test_files):
            full_sequence.append(test_files[v_idx])
            v_idx += DEFAULT_PATTERN_TEST

    total_frames = len(full_sequence)
    print(f"Total merged frames: {total_frames}")
    
    if total_frames == 0:
        print("Error: Not enough images to merge.")
        return

    # 5. Split the full sequence into parts
    frames_per_video = math.ceil(total_frames / args.num_videos)
    
    for i in range(args.num_videos):
        start_idx = i * frames_per_video
        end_idx = min((i + 1) * frames_per_video, total_frames)
        
        if start_idx >= total_frames:
            break
            
        batch_paths = full_sequence[start_idx:end_idx]
        output_name = os.path.join(args.out_dir, f"video_{i+1:02d}.mp4")
        
        create_video_from_paths(batch_paths, output_name, args.fps)

    print("\nAll videos processed successfully!")

if __name__ == "__main__":
    main()
