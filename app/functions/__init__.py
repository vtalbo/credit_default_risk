# -*- coding: utf-8 -*-
import pandas as pd
import pickle
import lightgbm
from app.functions.bokeh_plot import feature_importances
from bokeh.layouts import column, row, layout
from bokeh.resources import CDN
from bokeh.embed import file_html

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.widgets import DataTable, TableColumn, Div

import numpy as np

Names = {'CREDIT_TERM': 'Years of credit',
         'client_installments_AMT_PAYMENT_min_sum': 'Sum of the minimum amount the client paid on previous credits',
         'YEARS_EMPLOYED': 'Years employed',
         'YEARS_LAST_PHONE_CHANGE': 'Years since last phone change',
         'AGE': 'Client age',
         'AMT_ANNUITY': 'Annuity payment',
         'AMT_CREDIT': 'Credit amount',
         'bureau_DAYS_CREDIT_max': 'Maximum of years days before the client applied for Credit Bureau credit',
         'YEARS_ID_PUBLISH': 'Years since the client applied'}


def create_hist_column(df, column_name, target, bins, client_value):
    """ Create histogram for bokeh object after"""

    colors = ["#718dbf", '#e84d60']  # Default color, Client color
    data_hist = {}
    index_names = ['[{}-{}['.format(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]
    index_names.append('[{}+'.format(bins[-1]))
    data_hist['names'] = index_names
    data_hist['Default_percentage'] = np.zeros((len(bins), 1))

    data_hist['colors'] = [colors[0] for x in range(len(bins))]

    for i in range(len(bins)):
        if i != len(bins) - 1:
            data_hist['colors'][i] = colors[1] if (
                    (client_value >= bins[i]) & (client_value < bins[i + 1])) else colors[0]
            if df.loc[(df[column_name] >= bins[i]) & (df[column_name] < bins[i + 1]), target].count() != 0:
                data_hist['Default_percentage'][i] = \
                    100 * sum(df.loc[(df[column_name] >= bins[i]) & (df[column_name] < bins[i + 1]), target]) / df.loc[
                        (df[column_name] >= bins[i]) & (df[column_name] < bins[i + 1]), target].count()
        elif df.loc[(df[column_name] >= bins[i]), target].count() != 0:
            data_hist['colors'][i] = colors[1] if (client_value >= bins[i]) else colors[0]
            data_hist['Default_percentage'][i] = \
                100 * sum(df.loc[(df[column_name] >= bins[i]), target]) / df.loc[
                    (df[column_name] >= bins[i]), target].count()

    return data_hist


def histograms_column(df, column_name, target, bins, client_value, title='Probability of default', xlabel='Range'):
    data_hist = create_hist_column(df, column_name, target, bins, client_value)

    xrange = data_hist["names"]

    # Creation des ColumnDataSource
    hist_CDS = ColumnDataSource(data=data_hist)

    # Info de la figure
    p = figure(x_range=xrange, plot_height=125, title=title,
               toolbar_location=None, tools="hover",
               tooltips=[("Range", "@{}".format('names')),
                         ("Default Probability", "@{} %".format('Default_percentage'))],
               x_axis_label=xlabel,
               y_axis_label="Risk of default (in %)")

    # Histograms
    vbar = p.vbar(top='Default_percentage', x="names", width=0.9, source=hist_CDS, color="colors")

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None

    return p


def convert_cols(df):
    name_change = {'DAYS_EMPLOYED': 'YEARS_EMPLOYED', 'DAYS_BIRTH': 'AGE',
                   'DAYS_LAST_PHONE_CHANGE': 'YEARS_LAST_PHONE_CHANGE', 'AMT_ANNUITY': 'AMT_ANNUITY_x1000',
                   'AMT_CREDIT': 'AMT_CREDIT_x10000'}
    if isinstance(df, pd.DataFrame):
        df = df.rename(columns=name_change)
    else:
        df = df.rename(name_change)
    df['YEARS_EMPLOYED'] = -df['YEARS_EMPLOYED'] / 365.25
    df['AGE'] = -df['AGE'] / 365.25
    df['YEARS_LAST_PHONE_CHANGE'] = -df['YEARS_LAST_PHONE_CHANGE'] / 365.25
    df['AMT_ANNUITY_x1000'] = df['AMT_ANNUITY_x1000'] / 1000
    df['AMT_CREDIT_x10000'] = df['AMT_CREDIT_x10000'] / 10000

    return df


def get_client_values(credit_id):
    try:
        test = pd.read_csv('app/data/m_test.csv', index_col='SK_ID_CURR')
        x = test.loc[int(credit_id), :]
        return x
    except KeyError:
        return False


def predict_proba_lgbm(series):
    """ Predict the probability of default from a series of values, from lgbm model"""
    # load the model from disk
    with open('app/models/finalized_model_lgbm.sav', 'rb') as file:
        loaded_model = pickle.load(file)
    proba = loaded_model.predict_proba(series.to_numpy().reshape(1, -1))
    # Return probability of default
    return proba[:, 1][0]


def create_table_client(x):
    """ Create the table of Client's Data"""
    # create a Python dict as the basis of your ColumnDataSource
    data = {'Feature': ['Years of credit', 'Years employed', 'Client age (years)', 'Annuity payment (x1.000 $)',
                        'Credit amount (x100.000 $)'],
            "Value": np.around([x["CREDIT_TERM"], x['YEARS_EMPLOYED'], x['AGE'], x['AMT_ANNUITY_x1000'],
                                x['AMT_CREDIT_x10000']])}

    # create a ColumnDataSource by passing the dict
    source = ColumnDataSource(data)

    columns = [
        TableColumn(field="Feature", title="Feature Name"),
        TableColumn(field="Value", title="Clients Value"),
    ]
    data_table = DataTable(source=source, columns=columns, width=300, height=300)
    return data_table


def predict_credit_page(credit_id):
    """ Display of the page """

    x = get_client_values(credit_id)

    if isinstance(x, pd.Series):
        proba = predict_proba_lgbm(x)
        if proba <= 0.5:
            name = 'ACCEPTED.png'
        else:
            name = 'DENIED.png'

        x_mod = convert_cols(x)

        # bokeh table
        table_client = create_table_client(x_mod)

        # Bokeh histograms
        data_for_bokeh = pd.read_csv('app/data/data-for-bokeh.csv', index_col='SK_ID_CURR')
        # CREDIT TERM
        bins = [x * 5 for x in range(0, 10)]
        column_name = 'CREDIT_TERM'
        p_credit_term = histograms_column(data_for_bokeh, column_name, 'TARGET', bins, x_mod[column_name],
                                          title='Probability of default : Credit term',
                                          xlabel='Years of credit')
        # YEARS EMPLOYED
        bins = [x * 5 for x in range(0, 10)]
        column_name = 'YEARS_EMPLOYED'
        p_employed = histograms_column(data_for_bokeh, column_name, 'TARGET', bins, x_mod[column_name],
                                       title='Years employed',
                                       xlabel='Years employed')
        # AGE
        bins = [21 + x * 5 for x in range(0, 10)]
        column_name = 'AGE'
        p_age = histograms_column(data_for_bokeh, column_name, 'TARGET', bins, x_mod[column_name],
                                  title='Clients age',
                                  xlabel='Clients age')

        # AMT ANNUITY
        bins = [x * 10 for x in range(0, 10)]
        column_name = 'AMT_ANNUITY_x1000'
        p_annuity = histograms_column(data_for_bokeh, column_name, 'TARGET', bins, x_mod[column_name],
                                      title='Amount of annuities',
                                      xlabel='Amount of annuities (x 1000 $)')

        # AMT CREDIT
        bins = [x * 30 for x in range(0, 10)]
        column_name = 'AMT_CREDIT_x10000'
        p_amt_credit = histograms_column(data_for_bokeh, column_name, 'TARGET', bins, x_mod[column_name],
                                         title='Amount of credit',
                                         xlabel='Amount of credit (x 10.000 $)')

        # bokeh Div objects
        title_div = Div(text="<b>Prediction of default for client {:d} </b>".format(int(credit_id)),
                        style={'font-size': '100%', 'color': 'blue'})
        div_image = Div(text='<img src="/static/' + name + '" height=200>', height=200)
        div_proba_text = Div(text='<p> Probability of default : {:d} % </p>'.format(int(proba * 100)),
                             style={'text-align': 'center', 'font-size': '250%', 'color': 'black'})
        div_disclaimer_text = Div(text='(loan denied if probability more than 50 %).'
                                       'Probabilitities are actually calculated from more than 350 features. Even '
                                       'though the most important ones are shown here, they may not reflect the final'
                                       ' decision',
                                  style={'font-size': '100%', 'color': 'black'})
        proba_div = Div(text='<b> Probability of default according to clients database </b>',
                        style={'text-align': 'center', 'font-size': '100%', 'color': 'black'})
        column_left = column(title_div, div_image, div_proba_text, div_disclaimer_text, table_client,
                             sizing_mode='scale_width')
        column_right = column(proba_div, p_credit_term, p_employed, p_age, p_annuity, p_amt_credit,
                              sizing_mode='scale_width')
        layouts = row(column_left, column_right, sizing_mode="scale_height")
        return file_html(layouts, CDN, "Loan Acceptance")
    else:
        return "Cet ID n'est pas présent dans notre base de données"


def predict_credit(credit_id):
    """From credit_id, get the prediction of the credit failure or not
    If the credit_id does not exist, an error is shown"""
    try:
        test = pd.read_csv('app/data/m_test.csv', index_col='SK_ID_CURR')
        x = test.loc[int(credit_id), :]
        # load the model from disk
        with open('app/models/finalized_model.sav', 'rb') as file:
            loaded_model = pickle.load(file)
        # Predict payment default
        result = loaded_model.predict(x.to_numpy().reshape(1, -1))
        proba = loaded_model.predict_proba(x.to_numpy().reshape(1, -1))
        if result[0]:
            name = 'DENIED.png'
        else:
            name = 'ACCEPTED.png'
        div_image = Div(text='<img src="/static/' + name + '">', height=200)
        # div_image = Div(text='<img src="/static/DENIED.png"> </img>', height=200)
        div_proba = Div(text='<p>Probability of default : {:d} % (loan denied for more than 50 %)</p>'.format(5))

        p = feature_importances(credit_id)
        layouts = layout([[div_image], [p], ], sizing_mode="scale_height")
        # return name, proba
        return file_html(layouts, CDN, "Loan Acceptance")

    except KeyError:
        return "Cet ID n'est pas présent dans notre base de données"
