#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 13:14:58 2022

@author: Narayan Das
"""

import pandas as pd
import geopandas as gpd
from scipy import spatial
import os
import sys

def similarity_search(Training_filename, Test_filename, fieldnames,numResults,allRank, similarType, matchMethod, outputfilename):
    if Training_filename.endswith(".csv"):
        gdf1 = pd.read_csv(Training_filename)
        gdf2 = pd.read_csv(Test_filename)
    elif Training_filename.endswith(".xlsx"):
        gdf1 = pd.read_excel(Training_filename)
        gdf2 = pd.read_excel(Test_filename)
    elif Training_filename.endswith(".xls"):
        gdf1 = pd.ExcelFile(Training_filename)
        gdf2 = pd.ExcelFile(Test_filename)
    else:
        gdf1 = gpd.read_file(Training_filename)
        gdf2 = gpd.read_file(Test_filename) 

    gdf1.dropna(inplace=True)
    gdf2.dropna(inplace=True)
    gdf2["Cand_ID"] = list(range(0, len(gdf2)))
    gdf1["Cand_ID"] = list(range(0, len(gdf1)))
    gdf_1 = gdf1[fieldnames]
    gdf_2 = gdf2[fieldnames]
    gdf_1.loc['mean'] = gdf_1.mean()
    gdf_3 = pd.concat([gdf_2, gdf_1[-1:]])
    
    ##Attribte Values Search
    if matchMethod == "ATTRIBUTE_VALUES":
        for i in gdf_3.columns:
            x_mean,x_std = gdf_3[i].mean(),gdf_3[i].std()
            gdf_3[i+"standardization"] = gdf_3[i].apply(lambda x: (x-x_mean)/x_std)
            x_m = gdf_3[i+"standardization"][-1:]
            gdf_3[i+"Z_trans"] = gdf_3[i+"standardization"].apply(lambda x: (x-x_m)**2)
        gdf_4 = gdf_3.filter(regex = 'Z_trans$', axis = 1)
        gdf_3['Similarity Score'] = gdf_4[gdf_4.columns].sum(axis =1)
        gdf_3 = gdf_3[:-1]
        gdf_3['Similarity Rank'] = gdf_3['Similarity Score'].rank(method='min')
        gdf_3['Disimilarity Rank'] = gdf_3['Similarity Score'].rank(ascending=False,method='min')
    ##Attribute Rank
    elif matchMethod == "RANKED_ATTRIBUTE_VALUES":
        for i in gdf_3.columns:
            gdf_3[i+"_rank"] = gdf_3[i].rank(method = 'min')
            x_rank = gdf_3.loc['mean'][i+"_rank"]
            gdf_3[i+"_sqdif"] = gdf_3[i+"_rank"].apply(lambda x: (x-x_rank)**2)
        gdf_3 = gdf_3[:-1]
        gdf_4 = gdf_3.filter(regex = '_sqdif$', axis = 1)
        gdf_3['Similarity Score'] = gdf_4[gdf_4.columns].sum(axis =1)
        gdf_3['Similarity Rank'] = gdf_3['Similarity Score'].rank(method='min')
        gdf_3['Disimilarity Rank'] = gdf_3['Similarity Score'].rank(ascending=False,method='min')
    else:
        ##Cosine Similarity Search ATTRIBUTE_PROFILES
        for i in gdf_3.columns:
            x_mean,x_std = gdf_3[i].mean(),gdf_3[i].std()
            gdf_3[i+"standardization"] = gdf_3[i].apply(lambda x: (x-x_mean)/x_std)
        gdf_4 = gdf_3.filter(regex = 'standardization$', axis = 1)
        lis = []
        x = gdf_4.values
        y = gdf_4.loc['mean'].values
        for i in range(0,len(gdf_4)):
            result = 1-spatial.distance.cosine(x[i],y)
            lis.append(result)
        gdf_3['Similarity Score'] = lis
        gdf_3 = gdf_3[:-1]
        gdf_3['Similarity Rank'] = gdf_3['Similarity Score'].rank(ascending=False, method='min')
        gdf_3['Disimilarity Rank'] = gdf_3['Similarity Score'].rank(ascending=True,method='min')

    gdf_3["Cand_ID"] = list(range(0, len(gdf_3)))
    gdf_5 = gdf_3[['Cand_ID','Similarity Score','Similarity Rank','Disimilarity Rank']]
    gdf_6 = gdf2.merge(gdf_5, on ='Cand_ID', how = 'left')
    gdf_6 = gdf_6.reset_index(drop= True)
    gdf_7 = pd.concat([gdf1, gdf_6])
    gdf_7.fillna(0, inplace= True)
    if similarType != "MOST_SIMILAR":
        gdf_7 = gdf_7.sort_values("Disimilarity Rank").reset_index(drop = True)
    else:
        gdf_7 = gdf_7.sort_values("Similarity Rank").reset_index(drop = True)
    if allRank!= 1:
        gdf_7 = gdf_7[:numResults+len(gdf1)]
    if Training_filename.endswith(".csv"):
        output = gdf_7.to_csv(outputfilename+".csv", index=False)
    elif Training_filename.endswith(".xlsx"):
        output = gdf_7.to_excel(outputfilename+".xlsx", index=False)
    elif Training_filename.endswith(".xls"):
        output = gdf_7.to_excel(outputfilename+".xlsx",index=False)
    else:
        output = gpd.GeoDataFrame(gdf_7).to_file(outputfilename+".geojson", driver = 'GeoJSON')
    return output
input_file_name = sys.argv[1]
target_file_name = sys.argv[2]
output_file_name = sys.argv[3]
fieldnames = (sys.argv[4]).split(',')
numResults = int(sys.argv[5])
similarityType = sys.argv[6]    ##### Other Option: 'MOST_DISSIMILAR'
"""
MatchMethodOptions = 
['ATTRIBUTE_VALUES', 'RANKED_ATTRIBUTE_VALUES','ATTRIBUTE_PROFILES']
"""
matchMethod = sys.argv[7]
allRank = sys.argv[8]
this_py_file = os.path.dirname(os.path.abspath(__file__))
path = this_py_file
input_file_path = path + '/' + input_file_name
target_file_path = path + '/' + target_file_name
output_file_path = path + '/' + output_file_name
similarity_search(Training_filename = input_file_path, Test_filename = target_file_path, fieldnames = fieldnames, numResults=numResults, allRank = allRank, similarType = similarityType,matchMethod = matchMethod, outputfilename = output_file_path)