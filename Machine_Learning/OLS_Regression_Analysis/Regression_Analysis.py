import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import geopandas as gpd
import datetime
import os, glob
import statsmodels.api as sm
import json
import sys
import geopandas as gpd
from shapely import wkb
from shapely.geometry import Polygon, MultiPolygon
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)
def regression_gis(input_shpFile,input_feature_columns,dependent_variable, outputfile_path, output_summary_path,this_py_file):
    gdf = gpd.read_file(input_shpFile)
    dfm = gdf.dropna(subset= input_features)
    cols = ["variables","Coefficient[a]","StdError","t-Statistic","Probability[b]"]


    X_train = dfm[~dfm[dependent_variable].isna()][input_feature_columns]

    X_test = dfm[input_feature_columns]
    X_test.dropna(inplace = True)


    y_train = dfm[~dfm[dependent_variable].isna()][dependent_variable]


    dfp = dfm[dfm[dependent_variable].isna()]


    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    X_train2 = sm.add_constant(X_train)
    model = sm.OLS(y_train, X_train2)
    results = model.fit()

    dfm[f"{dependent_variable}_predicted"] = regressor.predict(X_test)
    dfm['residual'] = dfm[[dependent_variable,f"{dependent_variable}_predicted"]].apply(lambda x: x[0]-x[1], axis=1)

    tabledict = pd.read_html(results.summary().tables[1].as_html(), header=0, index_col=0)[0].reset_index()
    tabledict = tabledict.rename(columns={x:y for x,y in zip(tabledict.columns[:5],cols)}).to_dict(orient='records')
    var1 = pd.read_html(results.summary().tables[0].as_html(), header=None, index_col=0)[0].reset_index()
    var2 = pd.read_html(results.summary().tables[2].as_html(), header=None, index_col=0)[0].reset_index()
    ddict = {}
    for i, r in var1.iterrows():
        ddict[r[0].replace(':','')] = r[1]
        if r[2] is not np.nan:
            ddict[r[2].replace(':','')] = r[3]

    for i, r in var2.iterrows():
        ddict[r[0].replace(':','')] = r[1]
        ddict[r[2].replace(':','')] = r[3]

    for i,key in enumerate(['intercept']+input_feature_columns):
        tabledict[i]['variables'] = key
        val = tabledict[i]['Probability[b]']
        if val<=0.05 :
            tabledict[i]['Probability[b]'] = str(val)+str('*')
    if ddict['Prob (F-statistic)'] <= 0.05:
        v = ddict['Prob (F-statistic)']
        ddict['Prob (F-statistic)'] = f"{v}*"
    ddict['table'] = tabledict

    if not os.path.isdir(r"output"):
        os.mkdir(r"output")
    new_summary = this_py_file +'\\' + output_summary_path
    with open(new_summary, 'w') as f:
        json.dump(ddict, f, indent=2)


    new_output = this_py_file + '\\' + outputfile_path

    dfm.to_file(new_output,driver='GeoJSON')
    return dfm

this_py_file = os.path.dirname(os.path.abspath(input("Shape filename with directory :")))
inputfile_path = this_py_file + '\\' + input("Filename only :")
outputfile_path = input("output file name :")
output_summary_path = input("output summary in text format :")
input_features = input("Input feature :")
dependent_var = input("Dependent Variable :")
regression_gis(inputfile_path,input_features,dependent_var, outputfile_path, output_summary_path,this_py_file) 