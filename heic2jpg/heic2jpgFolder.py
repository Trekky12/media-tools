import os
from PIL import Image
import pillow_heif

def convert_heic_to_jpg(heic_path):
    file_name, file_ext = os.path.splitext(heic_path)
    jpg_path = f"{file_name}_converted.jpg"
    if not os.path.exists(jpg_path):
        try:
            if pillow_heif.is_supported(heic_path):
                im = Image.open(heic_path)
                icc_profile = im.info.get('icc_profile')
                im.save(jpg_path, "JPEG", quality=90, icc_profile=icc_profile)
                print(f"Converted {heic_path} to {jpg_path}")
        except Exception as e:
            print(f"Error converting {heic_path}: {e}")
    else:
        print(f"Skipped: {jpg_path} already exists.")
    '''
    if os.path.exists(jpg_path):
        print(f"Delete: {jpg_path}")
        os.remove(jpg_path)
    '''

def convert_all_heic_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.heic'):
                heic_path = os.path.join(root, file)
                convert_heic_to_jpg(heic_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python heic2jpgFolder.py <folder>")
        sys.exit(1)

    folder = sys.argv[1]
    pillow_heif.register_heif_opener()
    print(f"Starting conversion of .HEIC files in directory: {folder}")
    convert_all_heic_files(folder)
