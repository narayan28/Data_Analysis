import os, glob
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import *  # To import support for all data types
from pyspark.sql.functions import * #To import all functions required for data manipulations
import warnings
warnings.simplefilter("ignore")

##Spark_configurations:
spark = SparkSession.builder\
    .master('local[4]')\
    .appName('mongo')\
    .config("spark.mongodb.input.uri=mongodb://127.0.0.1:27017/mydb.collection" ) \
    .config("spark.mongodb.output.uri=mongodb://127.0.0.1:27017:27017/mydb.collection") \
    .config('spark.jar.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .getOrCreate()


from pyspark.sql import functions as F
os.chdir(input("Directory :"))
file = glob.glob("*.csv") #load only csv files
for fil_ in file:
    print("File in progress", fil_)
    df = spark.read.csv(fil_, header = True)
    df.write.format('mongo').mode('append').option('spark.mongodb.output.uri', 'mongodb://127.0.0.1:27017/mydb.collection').save()
    print("written in mongodb", fil_)



    