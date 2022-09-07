import os, shutil, glob                     ## for directory, read the type of file from folder
import pymongo                              ## for mongodb queries
import pandas as pd                         ## for read the files
import numpy as np                          ## for numerical calculation
import matplotlib.pyplot as plt             ## for visualization
import seaborn as sns                       ## for visualization
import skmob                                ## Scikit Mobility
import geopandas as gpd                     ## To read the Geospatial data
import shapely                              ## for geometry Conversion
import shapely.geometry                     ## geometry conversion string to wkb
from numpy.linalg import norm
from shapely.geometry import Point, Polygon, LineString, MultiLineString, MultiPoint, MultiPolygon
from pymongo import MongoClient             ## Mongoclient will help us to connect with databases

client = MongoClient("mongodb://localhost:27017/",username="xxxxx",password="xxxxx")  ## if mongodb installed locally, use localhost or 127.0.0.1: port number
db = client.mydb.collection_name                           ##client. Mongo database name. collection name

data_from_mongo = db.find({},{})                                             ##use mongodb query here...........


dataframe = pd.DataFrame(list(data_from_mongo))                               ## to create pandas dataframe, convert the cursor into list 
                #or
dataframe = pd.DataFrame([doc for doc in data_from_mongo])

dataframe.to_csv("filename.csv", index = False)                                ##to save csv file  
