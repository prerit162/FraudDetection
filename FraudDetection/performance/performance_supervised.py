"""
This module prints the performance of the fraud detection models
as present on the models_performance.json file
"""
import sys
import os
import time
import pandas as pd
import json
import pickle
import joblib

sys.path.append(os.path.abspath("./FraudDetection/models"))

# pylint: disable=C0413
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score, recall_score, f1_score, matthews_corrcoef
import xgboost as xgb


def read_data():
    """
    Function to read csv files
    parameters: None
    return: Preprocessed data from fraud, beneficiary, inpatient, outpatient.
    raise FileExistsError: raises an exception when file is not found
    """
    try:
        preprocessed = pd.read_csv("./FraudDetection/data/preprocessed.csv")
        return preprocessed
    except FileExistsError as error:
        raise error


def compute_performance_metrics(model_to_test, X_train, X_test, y_train, y_test):
    """
    Computes the performance metrics for the given model and test data.
    Args:
        model_to_test: The fraud detection model to evaluate.
        x_test: The test data to evaluate.
        y_test: The true labels for the test data.
    Returns:
        A dictionary with the computed performance metrics.
    """

    print(model_to_test)

    if model_to_test == "Logistic Regression":
        start_time = time.time()
        logreg = LogisticRegression(max_iter=1000)
        logreg.fit(X_train, y_train)
        y_pred = logreg.predict(X_test)
        end_time = time.time()

    if model_to_test == "Random Forest":
        start_time = time.time()
        # Instantiate model with 100 decision trees
        rf = RandomForestRegressor(n_estimators = 5, random_state = 42)
        # Train the model on training data
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test).round()
        end_time = time.time()

    if model_to_test == "XG Boost":
        start_time = time.time()
        xgb_cl = xgb.XGBClassifier()
        # Fit
        xgb_cl.fit(X_train, y_train)
        # Predict
        y_pred = xgb_cl.predict(X_test)
        end_time = time.time()
        #save model
        file_name = "./FraudDetection/script/pickle/xgb"
        joblib.dump(xgb_cl, file_name)
    
    precision = round(precision_score(y_test, y_pred), 3)
    recall = round(recall_score(y_test, y_pred), 3)
    f1_value = round(f1_score(y_test, y_pred), 3)
    mcc = round(matthews_corrcoef(y_test, y_pred), 3)
    total_time = round((end_time - start_time), 3)
    performance_dict = {
        "precision": precision,
        "recall": recall,
        "f1": f1_value,
        "mcc": mcc,
        "time": total_time
        }
    return performance_dict


if __name__ == '__main__':

    models = {
        "LR": "Logistic Regression",
        "RF": "Random Forest",
        "XGB": "XG Boost"
    }

    # Provide the paths to the preprocessed dataset and the actual labels
    fraud_data = read_data()
    x_data = fraud_data.drop(columns='PotentialFraud')
    y_labels = fraud_data['PotentialFraud']

    # Replace and Drop NA cols
    x_data['DeductibleAmtPaid'] = x_data['DeductibleAmtPaid'].fillna(0)
    x_data.dropna(axis=1, inplace=True)

    # Make the data file as per model requirement
    x_data = x_data.select_dtypes(exclude=['object'])

    X_train, X_test, y_train, y_test = train_test_split(x_data, y_labels,
    shuffle = True,test_size=0.3,random_state=1)
    performance = {}
    for model_name, model in models.items():
        print(f"Computing performance for {model_name}...")
        performance[model_name] = compute_performance_metrics(model, X_train, X_test, y_train, y_test)

print("\n\n")
for model_name, model_performance in performance.items():
    print(model_name, model_performance)



FILENAME = "./FraudDetection/script/json/models_performance_supervised.json"
with open(FILENAME, "w", encoding='utf-8') as outfile:
    json.dump(performance, outfile)
