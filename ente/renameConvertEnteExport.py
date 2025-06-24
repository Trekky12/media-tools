import os
import json
import shutil
from datetime import datetime
from PIL import Image
import pillow_heif
import re
import sys
import hashlib
import os
import piexif

pillow_heif.register_heif_opener()

filesWithoutMetadataFile = []

def get_creation_time_from_ente_meta(meta_file, file):
    try:
        with open(meta_file, 'r') as f:
            data = json.load(f)
            # retrieve file names from json
            if not (data.get('info') is None):
                filenames = data.get("info").get("fileNames")
                if file in filenames:
                    if file in filesWithoutMetadataFile:
                        filesWithoutMetadataFile.remove(file)
                        print(f"Found file {file} in {meta_file}")
                
                    return data.get("creationTime")
                
                print(f"Error: file {file} is not in metadata file {meta_file} listed")
                filesWithoutMetadataFile.append(file)
                return None
            else:
                filename = data.get("title")
                if file == filename:
                    return data.get("creationTime").get("timestamp")
                print(f"Error: file {file} is not in metadata file {meta_file} listed")
                filesWithoutMetadataFile.append(file)
                return None
    except Exception as e:
        print(f"Error reading metadata file {meta_file}: {e}")
        return None

def get_creation_time_from_exif(file):
    try:
        image = Image.open(file)
        exif_bytes = image.info.get("exif")
        if exif_bytes:
            exif_dict = piexif.load(exif_bytes)
            date_str = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
            if date_str:
                return datetime.strptime(date_str.decode(), '%Y:%m:%d %H:%M:%S')

    except Exception as e:
        print(f"Failed to read EXIF from {file}: {e}")

    return None

def get_creation_time_from_file(file):
    try:
        stat = os.stat(file)
        if hasattr(stat, 'st_birthtime'):
            return datetime.fromtimestamp(stat.st_birthtime)
        else:
            return datetime.fromtimestamp(stat.st_mtime)
    except Exception as e:
        print(f"File time error in {file}: {e}")
        return datetime.now()

def rename_and_copy_file(src, dst_root, creation_time):
    try:
        new_name = os.path.basename(src)
        file_name, file_ext = os.path.splitext(new_name)
      
        # skip photos which are already named YYYY-MM-DD
        if re.match(r"^(20[0-9]{2})-(0[1-9]|1[0-2])-(0[1-9]|[1,2][0-9]|3[0,1])", file_name):
            #print(f"File seems to be already renamed: {file_name}")
            pass
        elif creation_time:
            if isinstance(creation_time, datetime):
                dt = creation_time
            else:
                if isinstance(creation_time, (int, float)):
                    dt = datetime.fromtimestamp(creation_time)
                else:
                    dt = datetime.fromisoformat(creation_time)
            new_name = dt.strftime(f"%Y-%m-%d %H.%M.%S ({file_name}){file_ext}")
        
        dst_dir = os.path.dirname(src).replace(os.path.dirname(src_root), os.path.dirname(dst_root), 1)
        dst_path = os.path.join(dst_dir, new_name)
                
        if not os.path.exists(dst_path):
            os.makedirs(dst_dir, exist_ok=True)
            
            shutil.copy2(src, dst_path)
            print(f"Copied {src} -> {dst_path}")
        else:
            pass
            #print(f"Skipped: {dst_path} already exists.")
        return dst_path
    except Exception as e:
        print(f"Error renaming or copying file {src}: {e}")
        return None

def apply_gamma(image, gamma=1.1):
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    inv_gamma = 1.0 / gamma
    table = [int((i / 255.0) ** inv_gamma * 255) for i in range(256)]

    if image.mode == "RGB":
        return image.point(table * 3)
    else:
        return image.point(table)

def convert_heic_to_jpg(heic_path, remove = False):
    file_name, _ = os.path.splitext(heic_path)
    jpg_path = f"{file_name}_converted.jpg"
    if not os.path.exists(jpg_path):
        try:
            if pillow_heif.is_supported(heic_path):
                im = Image.open(heic_path)
                icc_profile = im.info.get('icc_profile')

                # copy exif
                exif_bytes = im.info.get('exif')
                if exif_bytes:
                    try:
                        exif_dict = piexif.load(exif_bytes)
                        exif_bytes = piexif.dump(exif_dict)
                        print(f"Copied EXIF from {heic_path}")
                    except Exception as e:
                        print(f"Could not parse EXIF from HEIC: {e}")
                        exif_bytes = b''
                else:
                    exif_bytes = b''
                    print(f"No EXIF found in {heic_path}")

                # increase gamma
                im = apply_gamma(im, gamma=1.1)

                im.save(jpg_path, "JPEG", quality=90, icc_profile=icc_profile, exif=exif_bytes)
                print(f"Converted {heic_path} to {jpg_path}")
                if remove:
                    os.remove(heic_path)
                    print(f"Deleted {heic_path}")

        except Exception as e:
            print(f"Error converting {heic_path}: {e}")
    else:
        #print(f"Skipped: {jpg_path} already exists.")
        pass

def process_folder(src_root, dst_root):
    for root, dirs, files in os.walk(src_root):
        # CLI export metadata folder
        metafolder = ".meta"
        # desktop export metadata folder
        if not os.path.exists(os.path.join(root, metafolder)):
            metafolder = "metadata"
        
        # Skip the metadata folder
        if metafolder in dirs:
            dirs.remove(metafolder)

        for file in files:
            file_name, file_ext = os.path.splitext(file)
            src_file = os.path.join(root, file)

            # =============================================            
            #       Search for ente metadata folder
            # =============================================
            meta_suffixes = [
                # regular case
                f"{file_ext}", 
                # live photo image has sometimes the jpg extension with the metadata file having the HEIC extension
                # IMG_0510.HEIC.json => "fileNames": [ "IMG_0510.jpg", IMG_0510.mov" ]
                ".HEIC",
                # live photos video (mov) is sometimes listed in the metadata file having the JPG extension
                # there was no case where a image having the HEIC extension was listed in a metadata file having the JPG extension but you never know
                ".JPG",   
                # second file with same names (TODO: improve for multiple duplicate names)
                f"_1.{file_ext}", 
                # second file (_1) where image has sometimes the jpg extension with the metadata file having the HEIC extension
                "_1.HEIC" 
            ]
            
            # sometimes upper and sometimes lowercase
            # IMG_0025.JPG.json => "fileNames": [ "IMG_0025.jpg", IMG_0025.mov" ]
            suffixes = meta_suffixes + [suffix.lower() for suffix in meta_suffixes] + [suffix.upper() for suffix in meta_suffixes]
            
            creation_time = None
            for suffix in suffixes:
                meta_file = os.path.join(root, metafolder, f"{file_name}{suffix}.json")
                if os.path.isfile(meta_file):
                    creation_time = get_creation_time_from_ente_meta(meta_file, file)
                    if creation_time:
                        break
            else:
                print(f"{src_file}: No metadata file found.")

            if not creation_time:
                print(f"{src_file}: Invalid or missing creationTime from ente metadata")
            
                # =============================================            
                #       use EXIF Date
                # =============================================        
                creation_time = get_creation_time_from_exif(src_file)
                if not creation_time:
                    print(f"{src_file}: Invalid or missing creationTime from EXIF")

                    # =============================================            
                    #       use Creation Date
                    # =============================================        
                    creation_time = get_creation_time_from_file(src_file)

            dst_file = rename_and_copy_file(src_file, dst_root, creation_time)
            if not dst_file:
                continue


            if pillow_heif.is_supported(dst_file):
                convert_heic_to_jpg(dst_file)

'''
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
'''

def compareTimes(file1, file2):
    mtime1 = os.path.getmtime(file1)
    mtime2 = os.path.getmtime(file2)
    
    return mtime1 == mtime2

def process_deleted(src_root, dst_root):
    dst_files = []
    for root, dirs, files in os.walk(dst_root):
      for file in files:
          file_name, file_ext = os.path.splitext(file)
          dst_file_full_path = os.path.join(root, file)
          dst_file = os.path.relpath(dst_file_full_path, dst_root)
          
          old_file = os.path.join(src_root, dst_file)
          file_exists = False
          
          if not file.endswith("_converted.jpg"):
              regex = f"\\((.*?)\\){file_ext}"
              
              match = re.search(regex, file)

              if match:                  
                  old_file_renamed = os.path.join(src_root, os.path.dirname(dst_file), f"{match.group(1)}{file_ext}")
                  #print(f"Original filename for {dst_file} is {old_file}.")
                  if os.path.isfile(old_file):
                      file_exists = compareTimes(old_file, dst_file_full_path)
                  elif os.path.isfile(old_file_renamed):
                      file_exists = compareTimes(old_file_renamed, dst_file_full_path)
                  #print(f"File exists or is the same: {file_exists}")
              elif os.path.isfile(old_file):
                  file_exists = compareTimes(old_file, dst_file_full_path)
                  #print(f"Original filename for {file} not found. {file_exists}")
              
              if not file_exists:
                  print(f"Original file missing, deleting this file {dst_file_full_path}")
                  os.remove(dst_file_full_path)
                  
                  jpg_path = os.path.join(root, f"{file_name}_converted.jpg")
                  if os.path.exists(jpg_path):
                      print("Delete corresponding jpg")
                      os.remove(jpg_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 renameConvertEnteExport.py <src folder>/ <dst folder>/")
        sys.exit(1)

    src_root = sys.argv[1]
    dst_root = sys.argv[2]

    print(f"Start Delete: {datetime.now()}")
    process_deleted(src_root, dst_root)
    print(f"Start Copy & Convert: {datetime.now()}")
    process_folder(src_root, dst_root)
    print(f"End: {datetime.now()}")
