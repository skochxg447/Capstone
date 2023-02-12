# StockProgram
This project is my capstone project for my python honors class. 

It is not intended for use as financial advice, but feel free to download it for personal use or learning.

## What It Does
This app will use python and sqlite (which is included with Python 2.5 and newer), to pull data from the Yahoo! Finance website, parse it, and put it into a database. It only pulls data from the past year, but the code can be altered for more data (further back) if you want it. The program includes failsafes for inputs from the user and many options for accessing the data, which can be built on for a more useful program, or even application if you want. 

### No Requirements needed

* I ran a pipreqs to see if anything was needed for this program to run and the answer was no. 

* Although, you will need python downloaded in case you don't already have it. 

* But most computers come with python 2.7 installed, which is good enough for this program.

* Try using this command in your terminal if you dont have python:

<img width="163" alt="Screen Shot 2023-02-12 at 1 19 12 PM" src="https://user-images.githubusercontent.com/123999256/218337823-d1eda334-b6d9-441a-b298-17e4154c7713.png">

If that doesn't work:

<img width="150" alt="Screen Shot 2023-02-12 at 1 17 48 PM" src="https://user-images.githubusercontent.com/123999256/218337756-ffda2b49-53c7-4a32-8299-e219fb547c62.png">


And as a last resort try:

<img width="162" alt="Screen Shot 2023-02-12 at 1 16 47 PM" src="https://user-images.githubusercontent.com/123999256/218337702-63632d41-91ad-4ee1-954f-3c62da0c7b32.png

#Make the program work
To make the program work, just type this in the terminal:

python3 StockPull.py

or if you have an older version of python:

python StockPull.py
