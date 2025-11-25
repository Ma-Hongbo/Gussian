import os
import re
import shutil
import argparse
import cv2
import numpy as np
from ultralytics import YOLO

def merge_pano_images(src_root, dst_root, camera_count=12):
    """
    Copy images from pano_camera{i} folders inside src_root
    into dst_root, and rename them as pano_camera{i}_originalFilename.
    After merging, delete the original pano_camera folders.
    """
    # Ensure the destination folder exists
    os.makedirs(dst_root, exist_ok=True)

    # Track folders that were successfully processed
    processed_folders = []

    # Iterate through camera folders
    for i in range(camera_count):
        src_dir = os.path.join(src_root, f"pano_camera{i}")

        if not os.path.exists(src_dir):
            print(f"⚠️ Folder not found: {src_dir}")
            continue

        # Iterate through images inside this folder
        for file_name in os.listdir(src_dir):
            src_path = os.path.join(src_dir, file_name)
            if os.path.isfile(src_path):
                new_name = f"pano_camera{i}_{file_name}"
                dst_path = os.path.join(dst_root, new_name)
                shutil.copy2(src_path, dst_path)

        print(f"✅ Processed folder: pano_camera{i}")
        processed_folders.append(src_dir)

    # Delete original folders only after success
    print("\n🗑 Deleting original pano_camera folders...")
    for folder in processed_folders:
        try:
            shutil.rmtree(folder)
            print(f"   - Deleted: {folder}")
        except Exception as e:
            print(f"   ❌ Failed to delete {folder}: {e}")

    print(f"\n🎉 Completed! Merged images saved in: {dst_root}")

def replace_ext_jpg_to_png(content):
    """Replace all .jpg / .JPG with .png"""
    content = content.replace(".jpg", ".png")
    content = content.replace(".JPG", ".png")
    return content

def modify_pano_ids(content):
    """
    Replace any pattern ' <number> pano' to ' 1 pano'
    Pattern: whitespace + digits + whitespace + pano
    """
    pattern = r'\s(\d+)\s+pano'
    replacement = r' 1 pano'
    return re.sub(pattern, replacement, content)

def replace_frame(content):
    """Replace all '/frame' with '_frame'"""
    return content.replace('/', '_')

def process_images_txt(file_path):
    """Run all modification steps on the given images.txt file"""
    if not os.path.exists(file_path):
        print(f"❌ Error: File does not exist → {file_path}")
        return

    print(f"📌 Processing file: {file_path}")

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply all modifications
    content = replace_ext_jpg_to_png(content)
    content = modify_pano_ids(content)
    content = replace_frame(content)

    # Write updated content back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("🎉 All replacements completed!")


# Load YOLOv8 segmentation model (auto-download if not available)
model = YOLO("yolo11x-seg.pt")  # Model supports instance segmentation

def person_mask(image_path, save_path="mask.png"):
    # Read image
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    # Run inference
    results = model(img)

    # Initialize mask: background = 1, person = 0
    final_mask = np.ones((h, w), dtype=np.uint8)

    for r in results:
        if r.masks is not None:
            for cls, mask in zip(r.boxes.cls, r.masks.data):
                if int(cls) == 0:  # COCO class 0 = person
                    m = mask.cpu().numpy()
                    m = cv2.resize(m, (w, h))  # Resize mask to original image size
                    m = (m > 0.5).astype(np.uint8)

                    # Set person region to 0
                    final_mask[m == 1] = 0

    # Save mask image (0 = black for person, 255 = white for background)
    cv2.imwrite(save_path, final_mask * 255)

    return final_mask

def process_images_in_folder(input_folder, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all files in the folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Only process image files
            image_path = os.path.join(input_folder, filename)
            mask_filename = f"mask_{filename}"
            save_path = os.path.join(output_folder, mask_filename)

            # Generate segmentation mask
            print(f"Processing {filename}...")
            person_mask(image_path, save_path)

    print("All masks are generated and saved.")

def keep_first_four_cameras(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Header: first 2 comment lines + number of cameras (line 3)
    header = lines[:3]  
    first_camera = lines[3:4]   # Only line for CAMERA_ID = 1

    # Update number of cameras to 1
    header[2] = "# Number of cameras: 1\n"

    new_content = header + first_camera

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_content)

    print("✅ cameras.txt updated: Only CAMERA_ID = 1 is kept.")

def convert_jpg_to_png_overwrite(input_dir):
    """
    Convert all .jpg/.jpeg images in input_dir to .png format,
    and delete the original .jpg/.jpeg files.
    """

    for file in os.listdir(input_dir):
        if file.lower().endswith((".jpg", ".jpeg")):
            src_path = os.path.join(input_dir, file)
            png_name = os.path.splitext(file)[0] + ".png"
            dst_path = os.path.join(input_dir, png_name)

            try:
                img = Image.open(src_path).convert("RGB")
                img.save(dst_path, "PNG")
                print(f"[OK] {file} → {png_name}")

                os.remove(src_path)
                print(f"[DEL] Removed original: {file}")

            except Exception as e:
                print(f"[ERROR] Failed to convert {file}: {e}")

    print("\n🎉 Overwrite conversion completed!")


def main():
    # prepare base dir 
    # create new dir_process(root)

    # '''
    # python c:\Users\TSingSV\Desktop\colmap\python\examples\panorama_sfm.py --input_image_path {dir} --output_path {dir_process}
    # python c:\Users\TSingSV\Desktop\colmap\scripts\python\read_write_model.py --input_model {dir_process}\sparse\0 --input_format .bin --output_model {dir_process}\sparse\0 --output_format .txt
    # then run this script
    # python c:\Users\TSingSV\Desktop\colmap\scripts\python\read_write_model.py --input_model {dir_process}\sparse\0 --input_format .txt --output_model {dir_process}\sparse\0 --output_format .bin
    # '''

    parser = argparse.ArgumentParser(description="Process 720 dataset automatically.")
    parser.add_argument(
        "--root",
        type=str,
        required=True,
        help="Root directory, e.g., C:\\Users\\TSingSV\\Desktop\\datas\\720_process"
    )

    args = parser.parse_args()

    root = args.root

    masks_dir = os.path.join(root, "masks")   # <-- create masks folder

    # Create masks folder if not exists
    if os.path.exists(masks_dir):
        shutil.rmtree(masks_dir)
        print("Old masks folder deleted.")

    os.makedirs(masks_dir, exist_ok=True)

    print(f"Created/checked mask directory: {masks_dir}")


    # Auto paths
    images_dir = os.path.join(root, "images")
    depths_dir = os.path.join(root, "depths")
    images_txt = os.path.join(root, "sparse", "0", "images.txt")
    camera_txt = os.path.join(root, "sparse", "0", "cameras.txt")
    os.makedirs(depths_dir, exist_ok=True)

    # convert_jpg_to_png_overwrite(images_dir)

    # keep_first_four_cameras(camera_txt)

    # # Run tasks
    # merge_pano_images(images_dir, images_dir)
    process_images_txt(images_txt)

    # Mask Generation
    # process_images_in_folder(images_dir, masks_dir)

    print("🎉 ALL DONE!")

    # '''
    # then run the depth map generation
    # python Depth-Anything-V2/run.py --encoder vitl --pred-only --grayscale --img-path {images_dir}  --outdir {depths_dir}
    # python utils/make_depth_scale.py --base_dir {root}  --depths_dir {depths_dir}
    # then run the png generation
    # '''


if __name__ == "__main__":

    main()

