@echo off
echo Creating directory structure...

:: Create directories
mkdir static\css
mkdir static\js
mkdir templates

:: Create empty files
type nul > app.py
type nul > downloader.py
type nul > static\css\style.css
type nul > static\js\main.js
type nul > templates\index.html

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Install required packages
pip install flask pytube

echo Project structure created successfully!
echo Now copy the code into respective files and run with: python app.py
pause