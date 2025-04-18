from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

year = '2021'
month = '12'

prefix = '%s-%s' %(year, month)

f1 = 'D:\\iPhone\\%s%s__' %(year, month)
f2 = 'C:\\Users\\User\\Nextcloud\\Bilder\\2021'

folder = Path(f1).glob('*')

for file in folder:
    suffix = file.stem[-4:]
    extension = file.suffix.lower()
    print("Searching for a file starting with %s and ending with %s%s" %(prefix, suffix, extension))
    for file2 in Path(f2).glob('**/*'):
        if file2.stem.startswith(prefix) and file2.stem.endswith(suffix) and file2.suffix.lower() == file.suffix.lower():
            print("I found a matching file %s for %s" %(file2.name, file.name))
            if file.suffix.lower() in ['.jpg', '.png', '.gif']:
                img1 = mpimg.imread(file)
                img2 = mpimg.imread(file2)

                # Create subplots with 1 row and 2 columns
                fig, axs = plt.subplots(1, 2)

                # Display the first image on the left subplot
                axs[0].imshow(img1)
                axs[0].axis('off')

                # Display the second image on the right subplot
                axs[1].imshow(img2)
                axs[1].axis('off')

                # Show the combined image
                plt.show()
            answer = input("Delete?")
            if answer.lower() in ["y","yes"]:
                 os.remove(file)