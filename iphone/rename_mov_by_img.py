from pathlib import Path


movies = Path('.').glob('*.mov')
images = Path('.').glob('*.JPG')
for movie in movies:
    print("searching for %s" %(movie.stem))
    for image in Path('.').glob('*.JPG'):
        print(movie.stem)
        print(str(image))
        if f"({movie.stem})" in str(image):
            print("found %s" %image.stem)
            movie.rename(Path(movie.parent, f"{image.stem}{movie.suffix}"))