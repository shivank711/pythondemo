#load necessary pkgs
from plotly.graph_objs import *
from dash.dependencies import Input
from plotly import tools
import plotly.graph_objs as go
import plotly.figure_factory as ff
import os
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import base64
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
np.set_printoptions(precision=2)


df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
df_2= pd.read_csv("/home/shivank/Dash-App-master/data/210_2h.csv")
#print(df_2['flag'].value_counts())
df_3= pd.read_csv("/home/shivank/Dash-App-master/data/210_3h.csv")
df_4= pd.read_csv("/home/shivank/Dash-App-master/data/210_4h.csv")
#print(df_3['flag'].value_counts())
df['IMG_URL']='https://www.drugbank.ca/structures/DB01000/thumb.svg'
df['NAME']=df['patient id']
df['DESC']=np.nan

app = dash.Dash()
app.config['suppress_callback_exceptions']=True
app.title = " ML Utility"
app.scripts.config.serve_locally = True
if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


def add_markers(figure_data, molecules, plot_type = 'scatter3d'):
    indices = []
    drug_data = figure_data[0]
    for m in molecules:
        hover_text = drug_data['text']
        for i in range(len(hover_text)):
            if m == hover_text[i]:
                indices.append(i)

    if plot_type == 'histogram2d':
        plot_type = 'scatter'

    traces = []
    for point_number in indices:
        trace = dict(
            x = [ drug_data['x'][point_number] ],
            y = [ drug_data['y'][point_number] ],
            marker = dict(
                color = 'red',
                size = 10,
                opacity = 0.6,
                symbol = 'cross'
            ),
            type = plot_type
        )

        if plot_type == 'scatter3d':
            trace['z'] = [ drug_data['z'][point_number] ]

        traces.append(trace)
    return traces

def scatter_plot_3d(
        z,
        zlabel,
        x = df['patient id'],
        y = df['time_c'],
        color = df['patient id'],
        xlabel = 'patient_id',
        ylabel = 'time_c',
        plot_type = 'scatter3d',
        markers = []):

    def axis_template_3d( title, type='linear' ):
        return dict(
            showbackground = True,
            backgroundcolor = BACKGROUND,
            gridcolor = 'rgb(255, 255, 255)',
            title = title,
            type = type,
            zerolinecolor = 'rgb(255, 255, 255)'
        )

    def axis_template_2d(title):
        return dict(
            xgap = 10, ygap = 10,
            backgroundcolor = BACKGROUND,
            gridcolor = 'rgb(255, 255, 255)',
            title = title,
            zerolinecolor = 'rgb(255, 255, 255)',
            color = '#444'
        )

    def blackout_axis( axis ):
        axis['showgrid'] = False
        axis['zeroline'] = False
        axis['color']  = 'white'
        return axis

    data = [ dict(
        x = x,
        y = y,
        z = z,
        mode = 'markers',
        marker = dict(
                colorscale = COLORSCALE,
                colorbar = dict( title = "Patient Id" ),
                line = dict( color = '#444' ),
                reversescale = True,
                sizeref = 45,
                sizemode = 'diameter',
                opacity = 0.7,
                size=5,
                color = color,
            ),
        text = df['NAME'],
        type = plot_type,
    ) ]

    layout = dict(
        font = dict( family = 'Raleway' ),
        hovermode = 'closest',
        margin = dict( r=20, t=0, l=0, b=0 ),
        showlegend = False,
        scene = dict(
            xaxis = axis_template_3d( xlabel ),
            yaxis = axis_template_3d( ylabel ),
            zaxis = axis_template_3d( zlabel),
            camera = dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0.08, y=2.2, z=0.08)
            )
        )
    )

    if plot_type == 'scatter':
        layout['xaxis'] = axis_template_2d(xlabel)
        layout['yaxis'] = axis_template_2d(zlabel)
        layout['plot_bgcolor'] = BACKGROUND
        layout['paper_bgcolor'] = BACKGROUND
        del layout['scene']
        data = [dict(
            x=x,
            y=z,
            mode='markers',
            marker=dict(
                colorscale=COLORSCALE,
                colorbar=dict(title="Molecular<br>Weight"),
                line=dict(color='#444'),
                reversescale=True,
                sizeref=45,
                sizemode='diameter',
                opacity=0.7,
                size=7,
                color=color,
            ),
            text=df['NAME'],
            type=plot_type,
        )]

    if len(markers) > 0:
        data = data + add_markers( data, markers, plot_type = plot_type )

    return dict( data=data, layout=layout )


BACKGROUND = 'rgb(230, 230, 230)'

COLORSCALE = [ [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"],
                [0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"] ]


FIGURE = scatter_plot_3d(z=df['Heart Rate'],zlabel='Heart Rate')
STARTING_DRUG = 1
DRUG_DESCRIPTION = df.loc[df['NAME'] == STARTING_DRUG]['DESC'].iloc[0]
DRUG_IMG="http://static3.businessinsider.de/image/5910666a50ade324008b4600-100-100/der-verstrende-grund-warum-babys-immer-spter-sprechen-lernen.jpg"


def annotate(table):
    l=[
        {
            "x": "control",
            "y": "control",
            "font": {"color": "white"},
            "showarrow": False,
            "text": table[0][0],
            "xref": "x1",
            "yref": "y1"
        },
        {
            "x": "control",
            "y": "case",
            "font": {"color": "white"},
            "showarrow": False,
            "text": table[1][0],
            "xref": "x1",
            "yref": "y1"
        },
        {
            "x": "case",
            "y": "control",
            "font": {"color": "white"},
            "showarrow": False,
            "text": table[0][1],
            "xref": "x1",
            "yref": "y1"
        },
        {
            "x": "case",
            "y": "case",
            "font": {"color": "white"},
            "showarrow": False,
            "text": table[1][1],
            "xref": "x1",
            "yref": "y1"
        },
    ]
    return l

def randomforest(combine,variable_used):
    feature = variable_used
    train_set, test_set = train_test_split(combine, test_size=0.40, random_state=100)
    train_set = train_set.reset_index().drop('index', axis=1)
    test_set = test_set.reset_index().drop('index', axis=1)
    forest_reg = RandomForestClassifier(random_state=40, class_weight={0: 1, 1: 8})
    param_dist = {"max_depth": range(1, 100),
                  "max_features": [0.1,0.3,0.5,0.7,0.9],
                  "min_samples_split": range(2, 30),
                  "min_samples_leaf": range(1, 20),
                  "bootstrap": [True, False],
                  "n_estimators":[10,30,50,70,100,200,500]
                  }
    rand_search = RandomizedSearchCV(forest_reg, param_dist, cv=3, scoring='precision', verbose=False, n_jobs=-1)
    rand_search.fit(train_set[feature], train_set['flag'])
    best = rand_search.best_estimator_
    pred = best.predict(test_set[feature])
    table = confusion_matrix(test_set['flag'],pred)
    #print(table[1][1])
    return table,feature,best.feature_importances_

def SVM(combine,variable_used):
    best = SVC(random_state=40, C=1, class_weight={0: 1, 1: 8})
    auc = 0
    train_set, test_set = train_test_split(combine, test_size=0.4, random_state=100)
    feature = variable_used
    train_set = train_set.reset_index().drop('index', axis=1)
    test_set = test_set.reset_index().drop('index', axis=1)
    svc = SVC(random_state=40, class_weight={0: 1, 1: 10})
    param_dist = {"C": range(1, 10),
                  "kernel": ["linear", "rbf", "poly"],
                  "degree": range(2, 5),
                  }
    rand_search = RandomizedSearchCV(svc, param_dist, cv=3, scoring='f1', verbose=False)
    rand_search.fit(train_set[feature], train_set['flag'])
    best = rand_search.best_estimator_
    pred = best.predict(test_set[feature])
    table = confusion_matrix(test_set['flag'],pred)
    return table

def logistic(combine,variable_used):
    train_set, test_set = train_test_split(combine, test_size=0.40, random_state=100)
    feature = variable_used
    train_set = train_set.reset_index().drop('index', axis=1)
    test_set = test_set.reset_index().drop('index', axis=1)
    logistic = LogisticRegression(random_state=40, class_weight={0: 1, 1: 10})
    param_dist = {"C": range(1, 10),
                  "penalty": ['l1', 'l2']
                  }
    rand_search = RandomizedSearchCV(logistic, param_dist, cv=3, scoring='precision', verbose=False)
    rand_search.fit(train_set[feature], train_set['flag'])
    best = rand_search.best_estimator_
    pred = best.predict(test_set[feature])
    table = confusion_matrix(test_set['flag'],pred)
    return table

def GradientBoosting(combine,variable_used):
    best = GradientBoostingClassifier(random_state=40)
    auc = 0
    feature = variable_used
    train_set, test_set = train_test_split(combine, test_size=0.4, random_state=100)
    train_set = train_set.reset_index().drop('index', axis=1)
    test_set = test_set.reset_index().drop('index', axis=1)
    for i in range(0, 20):
        boosting = GradientBoostingClassifier(random_state=40)
        param_dist = {"learning_rate": [0.01,0.05,0.1,0.5],
                      "n_estimators": [20,50,100,200,500,1000],
                      'min_samples_split':[2,4,10],
                      'min_samples_leaf':range(1,5),
                      'subsample':[0.2,0.5,1],
                      'max_features':[0.2,0.4,0.6,0.8,1]
                      }
        rand_search = RandomizedSearchCV(boosting, param_dist, cv=3, scoring='recall', verbose=False)
        rand_search.fit(train_set[feature], train_set['flag'])

        pred = rand_search.predict(test_set[feature])
        curr_auc = roc_auc_score(test_set['flag'], pred)
        if curr_auc > auc:
            best = rand_search.best_estimator_
            auc = curr_auc
    pred = best.predict(test_set[feature])
    table = confusion_matrix(test_set['flag'],pred)
    Importance = best.feature_importances_
    return table,feature,Importance

image_filename = '/home/shivank/Dash-App-master/img/logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([
        html.Div(
            # html.H2("KPMG",
            #     style={
            #         'color': '#4D637F',
            #         'font-family': 'Dosis',
            #             'display': 'inline',
            #             'font-size': '6.0rem',
                        
            #     }
            #     )
            

        html.Img(src='data:image/png;base64,{}'.format(encoded_image))

            ),
        html.H4('ML Utility',
                    style={
                        'position': 'relative',
                        'top': '0px',
                        'left': '10px',
                        'font-family': 'Dosis',
                        'display': 'inline',
                        'font-size': '6.0rem',
                        'color': '#4D637F'
                    }),
#
    html.Div(id='waitfor'),
    dcc.Upload(
        id='upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    html.Div(id='output'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),


#
        html.Div(
            dcc.Tabs(
                tabs=[
                    {'label': 'Data Input', 'value' : 3},
                    {'label': 'Descriptive Analysis', 'value': 1},
                    {'label': 'Feature Selection', 'value': 4},
                    {'label': 'Data Stratification', 'value':5},
                    {'label': 'Model Fitting', 'value': 2},
                    

                ],
                value=3,
                id='tabs',
                vertical= True,
                style={
                    'height': '100vh',
                    'borderRight': 'thin lightgrey solid',
                    'textAlign': 'left'
                }
            ),
            style={'width': '20%', 'float': 'left'}
        ),
        html.Div(
            html.Div(id='tab-output'),
            style={'width': '80%', 'float': 'right'}
        ),
        # html.Div(
        #     html.Div(id='output'),
        #     style={'width': '80%', 'float': 'right'}
        # )
    ], style={
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto',
    }


)

# app.layout = html.Div([
#     html.H2("ML Utility"),
#     ])
pre_style = {
    'whiteSpace': 'pre-wrap',
    'wordBreak': 'break-all',
    'whiteSpace': 'normal'
}

#


#@app.callback(Output('output','children'),Input('tabs','value'))




@app.callback(Output('output', 'children'),
              [Input('upload', 'contents')])
def update_output(contents):
        # return html.Div([
        #     html.H2("in the call back of upload")

        #     ])
    if contents is not None :
        print("in the upload call back")
        content_type, content_string = contents.split(',')
        if 'csv' in content_type:
            df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
            return html.Div([
                dt.DataTable(rows=df.to_dict('records')),
                html.Hr()
                #html.Div('Raw Content'),
                #html.Pre(contents, style=pre_style)
            ])
        elif 'image' in content_type:
            return html.Div([
                html.Img(src=contents),
                html.Hr(),
                #html.Div('Raw Content'),
                html.Pre(contents, style=pre_style)
            ])
        else:
            # xlsx will have 'spreadsheet' in `content_type` but `xls` won't
            # have anything
            try:
                df = pd.read_excel(io.BytesIO(base64.b64decode(content_string)))
                return html.Div([
                    dt.DataTable(rows=df.to_dict('records')),
                    html.Hr(),
                    #html.Div('Raw Content'),
                    html.Pre(contents, style=pre_style)
                ])
            except:
                return html.Div([
                    html.Hr(),
                    #html.Div('Raw Content'),
                    html.Pre(contents, style=pre_style)
                ])

#

@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_content(value):
    if value == 1:
        return  html.Div([
            
        html.Div([
                dcc.Dropdown(
                        id='variable',
                        options=[{'label': i, 'value': i} for i in df.columns if i not in
                                 ['flag','time','comment','time of arrest','patient id','Time Frequency','time_c','DESC','IMG_URL','NAME']]+
                                [{'label':"numer of records",'value':"number of records"},
                                 {'label':"total hours in ICU", 'value':'total hours in ICU'}
                                ],
                        value='sex'
                    )
                    ]),
            html.Div(id='visualization')])
    if value == 2:
        return html.Div([
            
        html.Div([

            dcc.Dropdown(
                id='model',
                options=[{'label':'Logistic Regression','value':'Logistic Regression'},
                         {'label': 'Random Forest', 'value': 'Random Forest'},
                         {'label': 'SVM','value':'SVM'},
                         {'label': 'Boosting','value':'Boosting'},
                         {'label': 'Random Forest vs Boosting','value':'rfvsboost'}],
                placeholder = "Select models"
            )
        ]),
        html.Div([
            dcc.Dropdown(
                id='khours',
                options=[{'label':'2 hours','value' :'2 hours'},{'label':'3 hours','value':'3 hours'},{'label':'4 hours','value':'4 hours'}],
                placeholder = 'Select hours to merge'
            )
        ]),
        html.Div([
            dcc.Dropdown(
                id='variable used',
                multi=True,
                placeholder='Select variables used in the model'
            )
        ]),
        html.Button('Build Model', id='button'),
            html.Div([
                dcc.Graph(id='confusion matrix')
            ],
                style={'margin-top': '10'}
            )
            ])

    if value == 4:
        return html.Div([
#            html.H2("this is feature selection"),
        html.Div([
            dcc.Dropdown(
                id='khours',
                options=[{'label':'2 hours','value' :'2 hours'},{'label':'3 hours','value':'3 hours'},{'label':'4 hours','value':'4 hours'}],
                placeholder = 'Select hours to merge'
            )
        ]),
        html.Div([
            dcc.Dropdown(
                id='variable used',
                multi=True,
                placeholder='Select variables used in the model'
            )
        ]),

            
       ]),

    # if value == 3:
    #     return html.Div([
    #         html.Div([
    #             html.H2("select data")
    #             ]),
    #         html.Div(id='waitfor'),
    #             dcc.Upload(
    #                 id='upload',
    #                 children=html.Div([
    #                     'Drag and Drop or ',
    #                     html.A('Select a File')
    #                 ]),
    #                 style={
    #                     'width': '100%',
    #                     'height': '60px',
    #                     'lineHeight': '60px',
    #                     'borderWidth': '1px',
    #                     'borderStyle': 'dashed',
    #                     'borderRadius': '5px',
    #                     'textAlign': 'center',
    #                     'margin': '10px'
    #                 }
    #             ),
    #         html.Div(id='output'),
    #         html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    #         html.H2("Data Input"),

    if value == 5 :
        return html.Div([
            html.Div(html.P("Training Testing Split: ")),
            html.Div([
                dcc.Dropdown(
                  id='my-dropdown',
                    options=[
                        {'label': '60 : 40', 'value': '6040'},
                        {'label': '65 : 45', 'value': '6545'},
                        {'label': '70 : 30', 'value': '7030'},
                        {'label': '75 : 25', 'value': '7525'},
                        {'label': '80 : 20', 'value': '8020'},
                    ],
                    value='6040'
                ),

            ])






        ])    



        #]),




@app.callback(
    dash.dependencies.Output('visualization','children'),
    [dash.dependencies.Input('variable','value')]
)

def update_visualization(variable):
    if variable not in ['age','Dry Weight','sex','number of records',
                        'total hours in ICU']:
        df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
        df['IMG_URL'] = 'https://www.drugbank.ca/structures/DB01000/thumb.svg'
        df['NAME'] = df['patient id']
        df['DESC'] = np.nan
        df = df.set_index('patient id')
        # set text
        for i in df.index.unique():
            print(i)
            text0=list((df.loc[i,'time'].values))
            text1 = list(zip([a[-5:] for a in text0], list(df.loc[i, variable].values)))
            text = [(a,b) for (a,b) in text1 if np.isnan(b)==False]
            df.loc[i, 'DESC'] = str(text)
        patient_id = df.index.unique()
        df = df.reset_index()
        return html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.P('SELECT patient(s) to highlight in the plot.')],
                        style={'margin-left': '10px'}),
                    dcc.Dropdown(id='chem_dropdown',
                                 value = [STARTING_DRUG],
                                 options = [{'label':i,'value':i} for i in patient_id],
                                 multi=True)
                ], className='twelve columns')
            ], className='row'),
            # Row 2: Hover Panel and Graph
            html.Div([
                html.Div([
                    html.Img(id='chem_img', src=DRUG_IMG),

                    html.Br(),

                    html.A(STARTING_DRUG,
                           id='chem_name',
                           href="https://www.drugbank.ca/drugs/DB01002",
                           target="_blank"),

                    html.P(DRUG_DESCRIPTION,
                           id='chem_desc',
                           style=dict(maxHeight='400px', fontSize='12px')),

                ], className='three columns', style=dict(height='300px', marginTop=25)),

                html.Div([

                    dcc.RadioItems(
                        id='charts_radio',
                        options=[
                            dict(label='3D Scatter', value='scatter3d'),
                            dict(label='2D Scatter', value='scatter')
                        ],
                        labelStyle=dict(display='inline'),
                        value='scatter3d'
                    ),

                    dcc.Graph(id='clickable-graph',
                              style=dict(width='700px'),
                              hoverData=dict(points=[dict(pointNumber=0)]),
                              figure=FIGURE),

                ], className='nine columns', style=dict(textAlign='center')),

            ], className='row')
        ])
    elif variable == 'sex':
        df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
        df = df.set_index('patient id')
        dic = {'patient id':[],'sex':[]}
        for i in df.index.unique():
            dic['sex'].append(df.loc[i,'sex'].values[0])
            dic['patient id'].append(i)
        df =pd.DataFrame(dic)
        sex = pd.DataFrame(df.sex.value_counts()).reset_index()
        return  dcc.Graph(id='comparison',
                          figure={
                              "data": [
                {
                    "type": "bar",
                    "x": ['F','M'],
                    # Get the count, or zero if it isn't present.
                    "y": sex['sex']
                }
            ],
            "layout": {
                "title": "comparison of sex"
            }
        })
    elif variable=='number of records':
        df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
        count = df['patient id'].value_counts()
        return  dcc.Graph(id='comparison',
                          figure={
            "data": [
                {
                    "type": "histogram",
                    "x": count
                }
            ],
            "layout": {
                "title": "Number of Records"
            }
        })
    elif variable == 'total hours in ICU':
        df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
        total_hours = []
        patient_id = df['patient id'].unique()
        df = df.set_index('patient id')
        for i in patient_id:
            total_hours.append(sum(df.loc[i, 'Time Frequency']) / 60)
        return dcc.Graph(id='comparison',
            figure={
            "data": [
                {
                    "type": "histogram",
                    "x": total_hours
                }
            ],
            "layout": {
                "title": "Total Hours Spent In ICU"
            }
        })
    elif variable == 'age':
        df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
        df=df.set_index('patient id')
        dic = {'patient id': [], 'age': []}
        for i in df.index.unique():
            dic['age'].append(df.loc[i, 'age'].values[0])
            dic['patient id'].append(i)
        df = pd.DataFrame(dic)
        return dcc.Graph(id='comparison',
            figure={
            "data": [
                {
                    "type": "histogram",
                    "x": df['age']
                }
            ],
            "layout": {
                "title": "Age"
            }
        })
    elif variable == 'Dry Weight':

        df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
        df=df.set_index('patient id')
        dic = {'patient id': [], 'weight': []}
        for i in df.index.unique():
            dic['weight'].append(np.median(df.loc[i, 'Dry Weight']))
            dic['patient id'].append(i)
        df = pd.DataFrame(dic)
        return dcc.Graph(id='comparison',
            figure={
            "data": [
                {
                    "type": "histogram",
                    "x": df['weight']
                }
            ],
            "layout": {
                "title": "Weight"
            }
        })

@app.callback(
    dash.dependencies.Output('variable used','options'),
    [dash.dependencies.Input('khours', 'value')]
)
def update_dropdown(khours):
    options=0
    if(khours=='2 hours'):
        options = [{'label': i, 'value': i} for i in df_2.columns if
                   i not in ['time', 'comment', 'time of arrest', 'patient id', 'Time Frequency','flag','time_c']]
    elif khours == '3 hours':
        options = [{'label': i, 'value': i} for i in df_3.columns if
                   i not in ['time', 'comment', 'time of arrest', 'patient id', 'Time Frequency','flag','time_c']]
    elif khours == '4 hours':
        options = [{'label': i, 'value': i} for i in df_4.columns if
                   i not in ['time', 'comment', 'time of arrest', 'patient id', 'Time Frequency','flag','time_c']]
    return options
@app.callback(
    dash.dependencies.Output('variable used','value'),
    [dash.dependencies.Input('khours', 'value')]
)
def update_dropdown(khours):
    if khours=='2 hours':
        value = [i for i in df_2.columns if
                   i not in ['time', 'comment', 'time of arrest', 'patient id', 'Time Frequency','flag','time_c']]
    elif khours=='3 hours':
        value = [i for i in df_3.columns if
                   i not in ['time', 'comment', 'time of arrest', 'patient id', 'Time Frequency','flag','time_c']]
    elif khours == '4 hours':
        value = [i for i in df_4.columns if
                 i not in ['time', 'comment', 'time of arrest', 'patient id', 'Time Frequency', 'flag', 'time_c']]
    return value

# for descriptive analysis
@app.callback(
    Output('clickable-graph', 'figure'),
    [Input('chem_dropdown', 'value'),
    Input('charts_radio', 'value'),Input('variable','value')])
def highlight_molecule(chem_dropdown_values, plot_type,variable):
    return scatter_plot_3d( z=df[variable],zlabel=str(variable), markers = chem_dropdown_values, plot_type = plot_type)


def dfRowFromHover( hoverData ):
    ''' Returns row for hover point as a Pandas Series '''
    if hoverData is not None:
        if 'points' in hoverData:
            firstPoint = hoverData['points'][0]
            if 'pointNumber' in firstPoint:
                point_number = firstPoint['pointNumber']
                molecule_name = str(FIGURE['data'][0]['text'][point_number]).strip()
                return df.loc[df['NAME'] == molecule_name]
    return pd.Series()


@app.callback(
    Output('chem_name', 'children'),
    [Input('clickable-graph', 'hoverData')])
def return_molecule_name(hoverData):
    if hoverData is not None:
        if 'points' in hoverData:
            firstPoint = hoverData['points'][0]
            if 'pointNumber' in firstPoint:
                point_number = firstPoint['pointNumber']
                molecule_name = str(FIGURE['data'][0]['text'][point_number]).strip()
                return molecule_name


@app.callback(
    Output('chem_desc', 'children'),
    [Input('chem_name', 'children'),Input('variable','value')])
def display_molecule(id,value):
    print(id)
    temp = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
    temp = temp.set_index("patient id")
    text0=list((temp.loc[int(id), 'time'].values))
    text1 = list(zip([a[-5:] for a in text0], list(temp.loc[int(id), value].values)))
    text = [(a,b) for (a,b) in text1 if np.isnan(b) ==False ]
    return str(text)

@app.callback(
    Output('chem_img', 'src'),
    [Input('chem_name', 'children')])
def display_image(id):
    temp = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
    temp = temp.set_index('patient id')
    if temp.loc[int(id),'age'].values[0]<=5:
        img_src="http://static3.businessinsider.de/image/5910666a50ade324008b4600-100-100/der-verstrende-grund-warum-babys-immer-spter-sprechen-lernen.jpg"
    elif temp.loc[int(id),'sex'].values[0]=='F':
        img_src="https://3.bp.blogspot.com/-QcUKoqBHrZY/UfEsTcWgcBI/AAAAAAAAACY/PjdxtEIXY4g/w120-h120/Short-Hairstyles-for-Little-Girls.jpg"
    else:
        img_src="https://media.ldscdn.org/images/media-library/children/portraits/portrait-boy-argentina-1080903-thumbnail.jpg"
    return img_src

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css"]


for css in external_css:
    app.css.append_css({"external_url": css})

@app.callback(
        dash.dependencies.Output('plot', 'figure'),
        [dash.dependencies.Input('variable', 'value')]
    )
def update_plot(value):
    df = pd.read_csv("/home/shivank/Dash-App-master/data/210_add_increment_2.csv")
    if (value == 'sex'):
        sex = pd.DataFrame(df.sex.value_counts()).reset_index()
        return {
            "data": [
                {
                    "type": "bar",
                    "x": ['F', 'M'],
                    # Get the count, or zero if it isn't present.
                    "y": sex['sex'],
                    "opacity": 0.7
                }
            ],
            "layout": {
                "title": "comparison of sex"
            }
        }
    elif value == 'number of records':
        # plot number of records
        count = df['patient id'].value_counts()
        return {
            "data": [
                {
                    "type": "histogram",
                    "x": count,
                    "opacity": 0.7
                }
            ],
            "layout": {
                "title": "Number of Records"
            }
        }
    elif value == 'total hours in ICU':
        total_hours = []
        patient_id = df['patient id'].unique()
        df = df.set_index('patient id')
        for i in patient_id:
            total_hours.append(sum(df.loc[i, 'Time Frequency']) / 60)
        return {
            "data": [
                {
                    "type": "histogram",
                    "x": total_hours,
                    "opacity": 0.7
                }
            ],
            "layout": {
                "title": "Total Hours Spent In ICU"
            }
        }
    elif value == 'age':
        return {
            "data": [
                {
                    "type": "histogram",
                    "x": df['age'],
                    "opacity": 0.7
                }
            ],
            "layout": {
                "title": "Age"
            }
        }
    elif value == 'weight':
        return {
            "data": [
                {
                    "type": "histogram",
                    "x": df['weight'],
                    "opacity": 0.7
                }
            ],
            "layout": {
                "title": "Weight"
            }
        }
    else:
        patient_id = df['patient id'].unique()
        return {
            "data": [
                {
                    "type": "scatter",
                    "mode": 'markers',
                    "opacity": 0.7,
                    "marker": {
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    "x": df['patient id'],
                    "y": df[value]
                }
            ],
            "layout": {
                "title": "Scatter Plot of " + str(value)

            }
        }
@app.callback(
    dash.dependencies.Output('confusion matrix','figure'),
    [dash.dependencies.Input('button','n_clicks')],
    [dash.dependencies.State('model','value'),
    dash.dependencies.State('khours', 'value'),
     dash.dependencies.State('variable used','value')
     ]
)
def update_matrix(n_click,model,khours,variable_name):
    print("printing n_click, khour,model")
    print(n_click,khours,model,variable_name)
    dic = {'2 hours':df_2,'3 hours': df_3, '4 hours': df_4}

    if model=="Random Forest" :
        table,feature,importance = randomforest(dic[khours],variable_name)
        temp ={'feature':list(feature),'importance':list(importance)}
        temp = pd.DataFrame(temp)
        temp=temp.sort_values(by='importance',ascending=False)
        print(table)
        trace1= go.Heatmap(
                x= ['control', 'case'],
                y= ['case', 'control'],
                z=[[table[1][0], table[1][1]],
                      [table[0][0], table[0][1]]],
            showscale=False
        )

        trace2=go.Scatter(
            x=temp['feature'][:10],
            y=temp['importance'][:10],
        )

        fig = tools.make_subplots(rows=1, cols=2)

        fig.append_trace(trace1, 1, 1)
        fig.append_trace(trace2, 1, 2)

        #print(table[0][0]+" is 0,0 " +table[0][1]+" is 0,1 "+table[1][0]+" is 1,0 "+table[1][1]+"is 1,1"),

        tn = float(table[1][1])
        fn = float(table[0][1])
        tp = float(table[0][0])
        fp = float(table[1][0])
        pre = tp/(tp+tn)
        rec = tp/(tp+fp)
        acc = (tp+tn)/(tp+tn+fp+fn)
        print(table[1][1])
        print(table[0][1])
        print(table[0][0])
        print(table[1][0])
        f = ((2*pre*rec)/(pre+rec))
        # fig['layout'].update(title="Precision: %.10f, Recall: %.10f" % (
        #  table[1][1] / (table[0][1] + table[1][1]), table[1][1] / (table[1][0] + table[1][1])))
        fig['layout'].update(title="Accuracy: %.2f F score :  %.6f Precision :  %.6f, Recall: %.6f" % (acc, f, pre, rec))

        fig['layout']['xaxis1'].update(title="Predicted value")
        fig['layout']['yaxis1'].update(title="Real value")
        fig['layout']['xaxis2'].update(tickangle = 60)
        fig['layout'].update( annotations = annotate(table),font=dict(size=8))
        return fig

    if model=="SVM":
        table = SVM(dic[khours], variable_name)
        print(table)
        tn = float(table[1][1])
        fn = float(table[0][1])
        tp = float(table[0][0])
        fp = float(table[1][0])
        pre = tp/(tp+tn)
        rec = tp/(tp+fp)
        acc = (tp+tn)/(tp+tn+fp+fn)
        f = ((2*pre*rec)/(pre+rec))
        return {
            "data": [
                {
                    "type": "heatmap",
                    "x": ['control', 'case'],
                    "y": ['case', 'control'],
                    "z": [[table[1][0], table[1][1]],
                          [table[0][0], table[0][1]]]
                }
            ],
            "layout": {
                "title": "Accuracy: %.2f, F Score : %.2f, Precision: %.2f, Recall: %.2f" % (acc, f, pre, rec),
                "xaxis": {"title": "Predicted value"},
                "yaxis": {"title": "Real value"},
                "annotations": annotate(table)
            }
        }

    if model =="rfvsboost":
        table,feature,importance = randomforest(dic[khours],variable_name)
        # temp ={'feature':list(feature),'importance':list(importance)}
        # temp = pd.DataFrame(temp)
        # temp=temp.sort_values(by='importance',ascending=False)
        print(table)
        print("calling boosting")
        table1,feature1,importance1 = GradientBoosting(dic[khours], variable_name)
        #table1,feature1,importance1 = randomforest(dic[khours],variable_name)
        print("called gbm")
        print(table1)
        trace1 = go.Heatmap(
            
            x=['control', 'case'],
            y=['case', 'control'],
            z=[[table[1][0], table[1][1]],
               [table[0][0], table[0][1]]],
            showscale=False,
            
            text = [["TP", "FN"],
                ["FP", "TN"]],
            autocolorscale = False,
        )
        
        # z = [[table[0][0],table[0][1]],
        #     [table[1][0], table[1][1]]]
        # x = ['Predicted Values',' ']
        # y = ['Real Values',' ']

        # z_text = [['TP', 'FN'],  
        #       ['FP', 'TN']]

        # trace1 = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=z)

        trace2= go.Heatmap(
                #title = "this is form boosting",
            x= ['control', 'case'],
            y= ['case', 'control'],
            z=[[table1[1][0], table1[1][1]],
                [table1[0][0], table1[0][1]]],
            text = [["TP", "FN"],
                ["FP", "TN"]],
            showscale=True,
            autocolorscale=False,
            #layout=Layout()  
         )
        # trace2 = go.Layout(
        #     title = "this is from boosting"
        #     )              

   #     trace2 = ff.create_annotated_heatmap(table1, x=x, y=y, annotation_text=z)
        print("done with traces")
        fig = tools.make_subplots(rows=1, cols=2)
        fig.append_trace(trace1, 1, 1)
        fig.append_trace(trace2, 1, 2)

        print("done with boosting")
        tn = float(table[1][1])
        fn = float(table[0][1])
        tp = float(table[0][0])
        fp = float(table[1][0])
        pre = tp/(tp+tn)
        rec = tp/(tp+fp)
        acc = (tp+tn)/(tp+tn+fp+fn)
        print(table[1][1])
        print(table[0][1])
        print(table[0][0])
        print(table[1][0])
        f = ((2*pre*rec)/(pre+rec))
        
        tn1 = float(table1[1][1])
        fn1 = float(table1[0][1])
        tp1 = float(table1[0][0])
        fp1 = float(table1[1][0])
        pre1 = tp1/(tp1+tn1)
        rec1 = tp1/(tp1+fp1)
        f1 = ((2*pre1*rec1)/(pre1+rec1))
        acc1 = (tp1+tn1)/(tp1+tn1+fp1+fn1)


      ## fig['layout'].update(title="Precision: %.10f, Recall: %.10f" % (
      #  #  table[1][1] / (table[0][1] + table[1][1]), table[1][1] / (table[1][0] + table[1][1])))
        fig['layout'].update(title="Acc RF: %.2f F score RF:  %.2f Prec RF:  %.2f, Rec RF: %.2f Acc Boost: %.2f F score Boost:  %.2f Prec Boost:  %.2f, Rec Boost: %.2f" % (acc, f, pre, rec, acc1,f1,pre1,rec1))
        #fig['layout'].update(title="Accuracy Boosting: %.6f F score Boosting:  %.6f Precision Boosting:  %.6f, Recall Boosting: %.6f" % (acc1, f1, pre1, rec1))

        fig['layout']['xaxis1'].update(title="Predicted value Random Forest")
        fig['layout']['yaxis1'].update(title="Real value")
        # #print("done with predict value and real value update")
        fig['layout']['xaxis2'].update(title="Predicted value Boosting")
        fig['layout']['yaxis2'].update(title="Real value")
        fig['layout'].update( annotations = annotate(table),font=dict(size=12))
        #fig['trace2'].update( annotations = annotate(table1),font=dict(size=12))
        # print("done with annotations")
        #fig['layout'].update( annotations = annotate(table1),font=dict(size=8))
                
        return fig


    if model=="Boosting":
        table,feature,importance = GradientBoosting(dic[khours], variable_name)
        print(table)
        temp = {'feature': list(feature), 'importance': list(importance)}
        temp = pd.DataFrame(temp)
        temp = temp.sort_values(by='importance', ascending=False)
        trace1 = go.Heatmap(
            x=['control', 'case'],
            y=['case', 'control'],
            z=[[table[1][0], table[1][1]],
               [table[0][0], table[0][1]]],
            showscale=False
        )

        trace2 = go.Scatter(
            x=temp['feature'][:10],
            y=temp['importance'][:10]
        )

        fig = tools.make_subplots(rows=1, cols=2)

        fig.append_trace(trace1, 1, 1)
        fig.append_trace(trace2, 1, 2)
        tn = float(table[1][1])
        fn = float(table[0][1])
        tp = float(table[0][0])
        fp = float(table[1][0])
        pre = tp/(tp+tn)
        rec = tp/(tp+fp)
        f = ((2*pre*rec)/(pre+rec))
        acc = (tp+tn)/(tp+tn+fp+fn)
        fig['layout'].update(title="Accuracy: %.2f, F Score: %.2f Precision: %.2f, Recall: %.2f" % (
           acc, f, pre, rec))
        fig['layout']['xaxis1'].update(title="Predicted value")
        fig['layout']['yaxis1'].update(title="Real value")
        fig['layout']['xaxis2'].update(tickangle = 60)
        fig['layout'].update( annotations = annotate(table),font=dict(size=8))
        return fig
    if model=="Logistic Regression":
        table = logistic(dic[khours], variable_name)
        tn = float(table[1][1])
        fn = float(table[0][1])
        tp = float(table[0][0])
        fp = float(table[1][0])
        pre = tp/(tp+tn)
        rec = tp/(tp+fp)
        f = ((2*pre*rec)/(pre+rec))
        acc = (tp+tn)/(tp+tn+fp+fn)
        return {
            "data": [
                {
                    "type": "heatmap",
                    "x": ['control', 'case'],
                    "y": ['case', 'control'],
                    "z": [[table[1][0], table[1][1]],
                          [table[0][0], table[0][1]]]
                }
                  
            ],
            "layout": {
                "title": "Accuracy: %.2f F Score : %.2f, Precision: %.2f, Recall: %.2f" % (acc, f, pre,rec),
                "xaxis": {"title": "Predicted value"},
                "yaxis": {"title": "Real value"},
                "annotations": annotate(table),

                "title": "Accuracy: %.2f F Score : %.2f, Precision: %.2f, Recall: %.2f" % (acc, f, pre,rec),
                "xaxis": {"title": "Predicted value"},
                "yaxis": {"title": "Real value"},
                "annotations": annotate(table)
            }
        }



if __name__ == '__main__':
    app.run_server(port=3000)






