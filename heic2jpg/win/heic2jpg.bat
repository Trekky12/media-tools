@echo off

setlocal enabledelayedexpansion

set "scriptDir=%~dp0"

rem Check if the ImageMagick folder exists
if not exist "%scriptDir%ImageMagick-7.1.0-Q16" (
    echo Error: ImageMagick directory not found!
    pause
    exit /b
)


:: set "inputFile=%~1"
:: set "outputFile=%~dpn1_converted.jpg"

for %%F in (%*) do (
    rem Set input and output file paths
    set "inputFile=%%~F"
    set "outputFile=%%~dpnF_converted.jpg"

    echo Processing File: "!inputFile!"

    "%scriptDir%\ImageMagick-7.1.0-Q16\magick.exe" convert "!inputFile!" -colorspace sRGB -gamma 1.1 -quality 90 "!outputFile!"
)