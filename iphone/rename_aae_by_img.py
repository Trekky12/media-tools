from pathlib import Path
import re


movies = Path('.').glob('*.AAE')
images = Path('.').glob('*.JPG')
for movie in movies:
    filename = movie.stem
    filename = re.sub("\s\(\d*\)", "", filename)
    print("searching for %s" %(filename))
    for image in Path('.').glob('*.JPG'):
        print(filename)
        print(str(image))
        if f"({filename})" in str(image):
            print("found %s" %image.stem)
            new_filename = image.stem.replace(filename, movie.stem)
            #print(new_filename)
            movie.rename(Path(movie.parent, f"{new_filename}{movie.suffix}"))