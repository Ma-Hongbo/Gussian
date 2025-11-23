import os
import shutil

def extract_images(source_folder, target_folder, step=5):
    """
    Extracts one image every 'step' images from the source folder and copies it to the target folder.
    
    :param source_folder: Path to the directory containing original images.
    :param target_folder: Path to the directory where sampled images will be saved.
    :param step: Sampling interval (default is every 5th image).
    """
    
    # 1. Define supported image formats
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif')

    # 2. Check if source folder exists
    if not os.path.exists(source_folder):
        print(f"❌ Error: Source folder not found: '{source_folder}'")
        return

    # 3. Create target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"📂 Created new directory: {target_folder}")
    else:
        print(f"📂 Target directory already exists: {target_folder}")

    # 4. Get and filter image files
    try:
        all_files = os.listdir(source_folder)
    except Exception as e:
        print(f"❌ Error accessing source folder: {e}")
        return

    image_files = [f for f in all_files if f.lower().endswith(valid_extensions)]
    
    # 5. Sort files (Critical!)
    # Sorting ensures that the sampling corresponds to the file order (e.g., 001, 002, 003...)
    # otherwise, os.listdir might return files in random order.
    image_files.sort()
    
    total_images = len(image_files)
    if total_images == 0:
        print("⚠️ No image files found in the source folder.")
        return

    # 6. Core logic: Python list slicing
    # Syntax: list[start:end:step]
    # This takes the 0th, 5th, 10th, 15th... items.
    selected_images = image_files[::step]

    print(f"📊 Found {total_images} images. Extracting {len(selected_images)} images (1 out of every {step})...")

    # 7. Execute Copy
    count = 0
    for filename in selected_images:
        src_path = os.path.join(source_folder, filename)
        dst_path = os.path.join(target_folder, filename)
        
        try:
            # shutil.copy2 preserves metadata (creation time, etc.)
            shutil.copy2(src_path, dst_path)
            # print(f"✅ Copied: {filename}") # Uncomment this line to see details for every file
            count += 1
        except Exception as e:
            print(f"❌ Failed to copy {filename}: {e}")

    print(f"\n🎉 Done! Successfully copied {count} images to '{target_folder}'")

# ================= Configuration Area =================
if __name__ == "__main__":
    # 👇 Source directory (Where your original images are)
    # Note for Windows: Use r"" string to handle backslashes correctly
    src_dir = r"C:\Users\YourName\Downloads\All_Images"
    
    # 👇 Destination directory (Where sampled images will go)
    # The script will create this folder if it doesn't exist
    dst_dir = r"C:\Users\YourName\Downloads\Sampled_Images"
    
    # Run extraction: 1 image every 5 images
    extract_images(src_dir, dst_dir, step=5)