"""
Main module that comprises of the Flask App for hosting the webpage,
along with the fraud analysis
"""
import sys
import os
import json
import pandas as pd
import joblib
#import seaborn as sns
#import matplotlib.pyplot as plt
from flask import Flask, request, render_template, session
from flask import send_file

sys.path.append(os.path.abspath("./FraudDetection/models"))

# pylint: disable=C0413
# pylint: disable=R1735
import plotly
import plotly.express as px
import plotly.graph_objects as go
# from models import loda_anomaly_detection
# from models import ecod_anomaly_detection
# from models import copod_anomaly_detection
# from models import iforest_anomaly_detection
# from models import suod_anomaly_detection

def read_data():
    """
    Function to read csv files
    parameters: None
    return: Preprocessed data from fraud, beneficiary, inpatient, outpatient.
    raise FileExistsError: raises an exception when file is not found
    """
    try:
        preprocessed=pd.read_csv("./FraudDetection/data/preprocessed.csv")
        return preprocessed
    except FileExistsError as error:
        raise error


def create_directory_if_not_exists(directory):
    """
    Create a directory if it does not exist.
    Args:
        directory (str): The name of the directory to be created.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def state_wise_visualization(inpatient_final_df,state_mapping):
    """
    Computes the state wise distribution of frauds.
    Args:
        inpatient_final_df : Dataframe have preprocessed data.
        state_mapping : Dataframe having state code to state name mapping.
    """
    grouped = pd.pivot_table(inpatient_final_df.groupby(
        ['PotentialFraud','Abbreviation'])['BeneID'].count().reset_index(),
        values = 'BeneID', index=['Abbreviation'],
        columns = 'PotentialFraud').reset_index()
    grouped.reset_index(drop = True)
    grouped.fillna(0,inplace=True)
    grouped['Total'] = grouped['No'] + grouped['Yes']
    grouped['% Frauds'] = grouped['Yes']*100/grouped['Total']
    grouped.sort_values(by = ['% Frauds'],inplace=True, ascending = False)
    grouped.loc[grouped['Total'] > 100].head(10)
    grouped = grouped[['Abbreviation','% Frauds']]
    grouped.fillna(0,inplace=True)
    grouped = grouped.merge(state_mapping, on = 'Abbreviation',how = 'inner')
    grouped['% Frauds'] = grouped['% Frauds'].apply(lambda x: round(x,1))
    fig = go.Figure(data=go.Choropleth(
             locations=grouped['Abbreviation'],
             z=grouped['% Frauds'].astype(float),
             locationmode='USA-states',
             colorscale="Viridis_r",
             autocolorscale=False,
             text=grouped['State_Name'], # hover text
             marker_line_color='white', # line markers between states
        ))
    fig.update_layout(
        title_text ='<b>% of Frauds by State</b>',
        title_x=0.5,
        geo = dict(
        scope='usa',
        projection=go.layout.geo.Projection(type = 'albers usa'),
        showlakes=True, # lakes
        lakecolor='rgb(255, 255, 255)'),
        )
    fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0},font=dict(
        family="Arial",
        size=8,
        color="RebeccaPurple"))
    return fig


def first_visualization(inpatient_final_df):
    """
    Creates a visualization for the trend observed in number of days admitted.
    Args:
        inpatient_final_df : Dataframe have preprocessed data.
    """
    grouped = pd.pivot_table(inpatient_final_df.groupby(
         ['PotentialFraud','Days_Admitted_Bucket'])['BeneID'].count().
         reset_index(), values = 'BeneID',    index=['Days_Admitted_Bucket'],
         columns = 'PotentialFraud').reset_index()
    grouped.reset_index(drop = True)
    grouped.fillna(0,inplace=True)
    grouped['Total'] = grouped['No'] + grouped['Yes']
    grouped['% Frauds'] = grouped['Yes']*100/grouped['Total']
    grouped.sort_values(by = ['% Frauds'],inplace=True, ascending = True)
    grouped['% Frauds'] = grouped['% Frauds'].apply(lambda x: round(x,1))
    fig = px.bar(grouped, x='Days_Admitted_Bucket', y='% Frauds',color = '% Frauds',
           labels={"Days_Admitted_Bucket": "<b>Number of Days Admitted</b>"})
    #fig.update_traces(marker_color=['#071633', '#0DEFFF'], showlegend=False)
    fig.update_layout(yaxis_range=[40,80], margin={"r":0,"t":0,"l":0,"b":0},font=dict(
        family="Arial",
        size=8,
        color="RebeccaPurple"))
    return fig
    #fig.show()
    #axis = sns.barplot(x = 'Days_Admitted_Bucket',
    #        y = '% Frauds',
    #        data = grouped)
    #axis.set(xlabel='Number of Days Admitted', ylabel='% Frauds')
    #plt.savefig('FraudDetection/static/images/days_admitted_visualization.jpg')

def third_visualization(inpatient_final_df):
    """
    Creates a visualization for the trend observed in Diagnosis Group Code.
    Args:
        inpatient_final_df : Dataframe have preprocessed data.
    """
    grouped = pd.pivot_table(inpatient_final_df.groupby(
    ['PotentialFraud','DiagnosisGroupCode'])['BeneID'].count().
    reset_index(), values = 'BeneID', index=['DiagnosisGroupCode'],
        columns = 'PotentialFraud').reset_index()
    grouped.reset_index(drop = True)
    grouped.fillna(0,inplace=True)
    grouped['Total'] = grouped['No'] + grouped['Yes']
    grouped['% Frauds'] = grouped['Yes']*100/grouped['Total']
    grouped.sort_values(by = ['% Frauds'],inplace=True, ascending = False)
    top_five_df = grouped.loc[grouped['Total'] > 50].head(5)
    bottom_five_df = grouped.loc[grouped['Total'] > 50].tail(5)
    grouped = pd.concat([bottom_five_df,top_five_df])
    grouped.sort_values(by = ['% Frauds'],inplace=True, ascending = True)
    grouped['% Frauds'] = grouped['% Frauds'].apply(lambda x: round(x,1))
    fig = px.bar(grouped, x='DiagnosisGroupCode', y='% Frauds',color = '% Frauds', labels={
                     "DiagnosisGroupCode": "<b>Diagnosis Code</b>"})
    #fig.update_traces(marker_color=['#071633', '#0DEFFF'], showlegend=False)
    fig.update_layout(yaxis_range=[20,80], margin={"r":0,"t":0,"l":0,"b":0}, font=dict(
        family="Arial",
        size=8,
        color="RebeccaPurple"))
    return fig
    #axis = sns.barplot(x = 'DiagnosisGroupCode',
    #        y = '% Frauds',
    #        data = grouped)
    #axis.set(xlabel='Diagnosis Group Code', ylabel='% Frauds')
    #plt.savefig('FraudDetection/static/images/DiagnosisGroupCode.jpg')


def fourth_visualization(inpatient_final_df):
    """
    Creates a visualization for the trend observed in Claim Amount reimbursed.
    Args:
        inpatient_final_df : Dataframe have preprocessed data.
    """
    grouped = pd.pivot_table(inpatient_final_df.groupby(
          ['PotentialFraud','InscClaimAmtReimbursed_Bucket'])['BeneID'].count().
          reset_index(), values = 'BeneID', index=['InscClaimAmtReimbursed_Bucket'],
          columns = 'PotentialFraud').reset_index()
    grouped.reset_index(drop = True)
    grouped.fillna(0,inplace=True)
    grouped['Total'] = grouped['No'] + grouped['Yes']
    grouped['% Frauds'] = grouped['Yes']*100/grouped['Total']
    grouped.sort_values(by = ['% Frauds'],inplace=True, ascending = True)
    grouped.loc[grouped['Total'] > 20].head(50)
    grouped['% Frauds'] = grouped['% Frauds'].apply(lambda x: round(x,1))
    fig = px.bar(grouped, x='InscClaimAmtReimbursed_Bucket', y='% Frauds',
              color = '% Frauds', labels={
              "InscClaimAmtReimbursed_Bucket": "<b>Insurance Amount Claimed</b>"})
    #fig.update_traces(marker_color=['#071633', '#0DEFFF'], showlegend=False)
    fig.update_layout(yaxis_range=[40,80], margin={"r":0,"t":0,"l":0,"b":0},font=dict(
        family="Arial",
        size=8,
        color="RebeccaPurple"
    ))
    fig.update_xaxes(tickangle=25)
    return fig
    #axis = sns.barplot(x = 'InscClaimAmtReimbursed_Bucket',
    #        y = '% Frauds',
    #        data = grouped)
    #axis.set(xlabel='Insurance Claim Amount Reimbursed', ylabel='% Frauds')
    #plt.savefig('FraudDetection/static/images/Amount_Reimbursed.jpg')


def test_visualization1(new_test_data):
    """
    Creates a visualization for the test data.
    Args:
        new_test_data : Dataframe having test data.
    """
    dataframe = new_test_data
    check  = (dataframe['PotentialFraud'].value_counts()).reset_index()
    test = dataframe.groupby('PotentialFraud')['InscClaimAmtReimbursed'].sum().reset_index()
    check  = pd.merge(check, test, left_on='index',
     right_on= 'PotentialFraud', how= 'inner')
    check['PotentialFraud_x'].round(1)
    check['index'] = (check['index'].
             map({1: 'Fraud', 0: 'Not Fraud'}))
    labels = check['index']
    values = check['PotentialFraud_x']
    custom_data= check['InscClaimAmtReimbursed']
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values,
     customdata=custom_data,
    hovertemplate='<br>Total Insurance Claim Amount: $%{customdata}</br>'))
    fig.update_layout(title='% of Frauds', paper_bgcolor='rgba(75,46,131,1)',
margin={"r":50,"t":0,"l":50,"b":0}, legend_title_font_color="white",
title_font_color="white",font_color="white")
    return fig

def test_visualization2(new_test_data):
    """
    Creates a visualization for the test data.
    Args:
        inpatient_final_df : Dataframe have preprocessed data.
    """
    dataframe = new_test_data
    funnel_inpatient = pd.DataFrame()
    funnel_inpatient.at[0, 'metric'] = 'Total Transactions'
    funnel_inpatient.at[0, 'number'] = dataframe.shape[0]
    funnel_inpatient.at[1, 'metric'] = 'Patients'
    funnel_inpatient.at[1, 'number'] = dataframe.loc[dataframe['is_Inpatient'] == 1].shape[0]
    funnel_inpatient.at[2, 'metric'] = 'Fraud Transactions'
    funnel_inpatient.at[2, 'number'] = dataframe.loc[(dataframe['PotentialFraud'] == 1)
        & (dataframe['is_Inpatient'] ==   1)].shape[0]
    funnel_outpatient = pd.DataFrame()
    funnel_outpatient.at[0, 'metric'] = 'Total Transactions'
    funnel_outpatient.at[0, 'number'] = dataframe.shape[0]
    funnel_outpatient.at[1, 'metric'] = 'Patients'
    funnel_outpatient.at[1, 'number'] = dataframe.loc[dataframe['is_Inpatient'] == 0].shape[0]
    funnel_outpatient.at[2, 'metric'] = 'Fraud Transactions'
    funnel_outpatient.at[2, 'number'] = dataframe.loc[(dataframe['PotentialFraud'] == 1)&
         (dataframe['is_Inpatient'] == 0)].shape[0]
    funnel_inpatient['label'] = 'Inpatient'
    funnel_outpatient['label'] = 'Outpatient'
    funnel = pd.concat([funnel_outpatient,funnel_inpatient])
    funnel.drop_duplicates(subset = ['metric','number'], inplace=True)
    funnel.loc[funnel['metric'] == 'Total Transactions', 'label'] = 'Total Transactions'
    #number = funnel['number']
    #metric = funnel['metric']
    fig = px.funnel(funnel, x='number', y='metric', color='label')
    fig.update_layout(paper_bgcolor='rgba(75,46,131,1)',
      margin={"r":100,"t":20,"l":100,"b":20}, legend_title_text='Type of Patient',
      legend_title_font_color="white", title_font_color="white",
 font_color="white", yaxis_title=None,hovermode=False)
    fig.update_yaxes(matches=None, showticklabels=True, visible=True, automargin=True)
    return fig

JSON_FILES = './FraudDetection/script/json'

if __name__ == '__main__':

    UPLOAD_DIR = './FraudDetection/script/uploads'
    create_directory_if_not_exists(UPLOAD_DIR)

    app = Flask(__name__, template_folder=os.path.abspath('./FraudDetection/templates'),
                static_folder=os.path.abspath('./FraudDetection/static'))

    app.secret_key = 'my_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'
    ####Only Added here as global variables to reduce latency time of website ##########
    training_data = pd.read_csv("./FraudDetection/data/training_data.csv")
    #dataframe = pd.read_pickle("./FraudDetection/data/training_data.pkl")
    fig5 = test_visualization1(training_data)
    fig6 = test_visualization2(training_data)
    def initialize_app(application):
        """
        Initializes the Flask app with the session object.
        Args:
            application (Flask): The Flask app object to be initialized.
        """
        print("Inside initialize App")
        application.config.from_object(__name__)


    initialize_app(app)

    @app.route('/')
    def home():
        """
        Renders the start page HTML template.
        Returns:
            str: The rendered HTML template.
        """
        state_mapping = pd.read_csv("./FraudDetection/data/State_Mapping.csv")
        inpatient_final_df = pd.read_csv("./FraudDetection/data/visualization.csv")
        inpatient_final_df['PotentialFraud'] = (inpatient_final_df['PotentialFraud'].
             map({1: 'Yes', 0: 'No'}))
        fig1 = first_visualization(inpatient_final_df)
        fig3 = third_visualization(inpatient_final_df)
        fig4 = fourth_visualization(inpatient_final_df)
        fig = state_wise_visualization(inpatient_final_df,state_mapping)
        graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('start-page.htm',graphJSON=graphjson,
        graphjson1 = graphjson1,graphjson3 = graphjson3,graphjson4 = graphjson4)

    @app.route('/home-page')
    def home_page():
        """
        Renders the start page.
        Returns:
            A rendered HTML template.
        """
        state_mapping = pd.read_csv("./FraudDetection/data/State_Mapping.csv")
        inpatient_final_df = pd.read_csv("./FraudDetection/data/visualization.csv")
        inpatient_final_df['PotentialFraud'] = (inpatient_final_df['PotentialFraud'].
             map({1: 'Yes', 0: 'No'}))
        fig1 = first_visualization(inpatient_final_df)
        fig3 = third_visualization(inpatient_final_df)
        fig4 = fourth_visualization(inpatient_final_df)
        fig = state_wise_visualization(inpatient_final_df,state_mapping)
        graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('start-page.htm',graphJSON=graphjson,
        graphjson1 = graphjson1,graphjson3 = graphjson3,graphjson4 = graphjson4)
        #print("Inside home page")
        #return render_template('start-page.htm')

    @app.route('/user-page')
    def user_page():
        """
        Render the user page, which displays the performance of the models.
        Returns:
            str: The HTML content to be displayed on the user page.
        """
        filepath = os.path.join(JSON_FILES, 'models_performance_sup_unsup.json')
        with open(filepath, encoding='utf-8') as fname:
            models = json.load(fname)
        best_model_name = None
        best_f1 = -1
        best_mcc = -1
        best_time = float('inf')
        for model_name, model_details in models.items():
            f1_value = model_details['f1']
            mcc = model_details['mcc']
            time_to_predict = model_details['time']
            # print(model_name, f1, mcc, time_to_predict)
            count_improvement = 0
            if f1_value > best_f1:
                count_improvement += 1
            if mcc > best_mcc:
                count_improvement += 1
            if time_to_predict < best_time:
                count_improvement += 1
            if count_improvement >= 2:
                best_f1 = f1_value
                best_mcc = mcc
                best_time = time_to_predict
                best_model_name = model_name

        session['filepath'] = filepath
        session['best_model_name'] = best_model_name
        session['models'] = models
        try:
            best_model_name = session.get('best_model_name')
        except ValueError:
            best_model_name = None

        graphjson5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson6 = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
        print('here')
        return render_template('user-page.htm', models=models, best_model=best_model_name,
                            filepath=filepath, graphjson5 = graphjson5,graphjson6 = graphjson6)


    @app.route('/upload-csv', methods=['POST'])
    def upload_csv():
        """
        Uploads a CSV file and displays the best performing model on the user page.
        Returns:
            str: A message indicating whether a file was uploaded or not.
        """
        # filepath1 = os.path.join(JSON_FILES, 'models_performance_sup_unsup.json')
        # with open(filepath1, encoding='utf-8') as fname:
        #     models = json.load(fname)
        # best_model_name = None
        # best_f1 = -1
        # best_mcc = -1
        # best_time = float('inf')
        # for model_name, model_details in models.items():
        #     f1_value = model_details['f1']
        #     mcc = model_details['mcc']
        #     time_to_predict = model_details['time']
        #     count_improvement = 0
        #     if f1_value > best_f1:
        #         count_improvement += 1
        #     if mcc > best_mcc:
        #         count_improvement += 1
        #     if time_to_predict < best_time:
        #         count_improvement += 1
        #     if count_improvement >= 2:
        #         best_f1 = f1_value
        #         best_mcc = mcc
        #         best_time = time_to_predict
        #         best_model_name = model_name
        if 'csv-file' not in request.files:
            return 'No file selected'
        file = request.files['csv-file']
        if file.filename == '':
            return 'No file selected'
        contents = file.read().decode('utf-8')

        filepath2 = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath2, 'w', encoding='utf-8') as fname:
            fname.write(contents)

        session['filepath'] = filepath2
        #session['best_model_name'] = best_model_name
        #session['models'] = models

        new_test_data = pd.read_csv(filepath2)
        xgb = joblib.load('./FraudDetection/script/pickle/xgb')
        y_pred = xgb.predict(new_test_data)
        new_test_data['PotentialFraud'] = y_pred.astype(int)

        fig7 = test_visualization1(new_test_data)
        fig8 = test_visualization2(new_test_data)
        graphjson5 = json.dumps(fig7, cls=plotly.utils.PlotlyJSONEncoder)
        graphjson6 = json.dumps(fig8, cls=plotly.utils.PlotlyJSONEncoder)
        print('here')

        new_test_data.to_csv('./FraudDetection/script/uploads/new_test_data.csv',index=False)

        return render_template('user-page.htm', models=session['models'],
        best_model=session['best_model_name'],
        filepath=session['filepath'],
        graphjson5 = graphjson5,graphjson6 = graphjson6)


    @app.route('/download-csv', methods=['POST'])
    def download_csv():
        """
        Detects anomalies using the deployed model and returns CSV file of the fraudulent claims.
        Returns:
            flask.Response: The HTTP response containing the fraudulent claims in a CSV file.
        """
        filepath = './uploads/new_test_data.csv'

        # pylint: disable = E1123
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True
            # attachment_filename = 'Frauds.csv'
    )

    app.run(debug=True)
