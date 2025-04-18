#!/bin/bash

# sudo apt install imagemagick

TARGET_DIR="/media/images"


# Find all HEIC files and process them

# IFS stands for Internal Field Separator.
# By default, IFS is set to whitespace (spaces, tabs, newlines),
# meaning that when you use read to get input, it splits the input into fields wherever it encounters spaces or tabs.

# Setting IFS= (an empty string) temporarily disables field splitting.
# This ensures that the full line of input is read as a single item, even if it contains spaces.

find "$TARGET_DIR" -type f \( -iname "*.heic" \) | while IFS= read -r heic_file; do
    jpg_file="${heic_file%.*}_converted.jpg"

    if [ ! -f "$jpg_file" ]; then
        echo "Converting $heic_file to $jpg_file"
        convert "$heic_file" -colorspace sRGB -gamma 1.1 -quality 90 "$jpg_file"
    else
        echo "Skipping $heic_file - $jpg_file already exists"
    fi
done
