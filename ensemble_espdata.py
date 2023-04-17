# -*- coding: utf-8 -*-
"""Ensemble_espData.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18mErQ3YBq1Pp9V4kUZFqBzHtoALFtmJ-
"""

import pandas as pd
# from keras.models import Sequential
# from keras.layers import Dense
# import keras
import xgboost
# from tensorflow.keras import layers
# import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier

# tf.config.experimental_run_functions_eagerly(True)

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report

# from sklearn.metrics import plot_confusion_matrix 
import numpy as np
from sklearn.linear_model import RidgeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from numpy import mean
from numpy import std
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
import time
import pickle


def get_accuracy_data():
    # Load data
    df = pd.read_csv('esp_all_denoised_D1.csv')

    # Separate features and target variable
    X = df.iloc[:, 0:51]
    y = df.iloc[:, 51]

    # Train the model
    clf1 = RidgeClassifier()
    clf2 = LinearDiscriminantAnalysis()
    clf3 = RandomForestClassifier(n_estimators=100, max_depth=37, random_state=42)
    ensemble = VotingClassifier(estimators=[('gnb', clf1), ('lda', clf2), ('rfc', clf3)], voting='hard')
    clf = ensemble.fit(X, y)

    # Predict energy consumption after retrofitting
    E1 = 1000  # Energy consumption of the building before retrofitting (in kWh)
    E2_pred = clf.predict(X)  # Predicted energy consumption of the building after retrofitting (in kWh)

    # Calculate potential energy savings
    potential_savings = ((E1 - E2_pred) / E1) * 100

    # Calculate accuracy of the model
    cv = KFold(n_splits=10, random_state=42, shuffle=True)
    scores = cross_val_score(ensemble, X, y, scoring='accuracy', cv=cv, n_jobs=-1)
    accuracy_mean = np.mean(scores)
    accuracy_std = np.std(scores)

    # Return results
    return {"mean": accuracy_mean, "std": accuracy_std, "potential_savings": potential_savings}




def get_energy_consumption_data():
    # Load data
    df = pd.read_csv('esp_all_denoised_D1.csv')

    # Separate features and target variable
    X = df.iloc[:, 0:51]
    y = df.iloc[:, 51]

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    clf = xgboost.XGBRegressor(objective ='reg:squarederror', colsample_bytree = 0.3, learning_rate = 0.1,
                               max_depth = 5, alpha = 10, n_estimators = 100, random_state=42)
    clf.fit(X_train, y_train)

    # Predict energy consumption after retrofitting
    E1 = 1000  # Energy consumption of the building before retrofitting (in kWh)
    E2_pred = clf.predict(X_test)  # Predicted energy consumption of the building after retrofitting (in kWh)

    # Calculate potential energy savings
    potential_savings = ((E1 - E2_pred.mean()) / E1) * 100

    # Calculate root mean squared error of the model
    rmse = np.sqrt(metrics.mean_squared_error(y_test, E2_pred))

    # Return results
    return {"mean": E2_pred.mean(), "std": E2_pred.std(), "rmse": rmse, "potential_savings": potential_savings}

