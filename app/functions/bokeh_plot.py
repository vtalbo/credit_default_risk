from bokeh.resources import CDN
from bokeh.embed import file_html

import numpy as np
import pickle

from bokeh.layouts import column, grid
from bokeh.models import ColumnDataSource, CustomJS, PrintfTickFormatter, Select
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.palettes import Spectral10
import pandas as pd


def bokeh_plot():

    data_for_bokeh = pd.read_csv('app/data/data-for-bokeh.csv', index_col='SK_ID_CURR')
    data = pd.DataFrame(data_for_bokeh.TARGET.value_counts()).reset_index()
    data['percent'] = data['TARGET'] / sum(data['TARGET']) * 100
    data['index'] = data['index'].astype(str).replace({'True': 'Default', 'False': 'No Default'})

    values = data['index'].unique()

    p = figure(x_range=values, plot_height=200, title="Number of contracts", tools=[HoverTool()],
               tooltips="@index : @TARGET (@percent{0.2f} %)",
               toolbar_location=None)

    p.vbar(x="index", top="TARGET", width=0.6, source=data)
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.yaxis[0].formatter = PrintfTickFormatter(format="%6.0f")

    return file_html(p, CDN, "DASHBOARD")


def bokeh_table():
    data_for_bokeh = pd.read_csv('app/data/data-for-bokeh.csv', index_col='SK_ID_CURR')

    source = ColumnDataSource(data_for_bokeh.sort_values(by='previous_loan_counts', ascending=False).head(10))

    columns = [
        TableColumn(field="SK_ID_CURR", title="SK_ID_CURR"),
        TableColumn(field="previous_loan_counts", title="previous_loan_counts"),
    ]
    data_table = DataTable(source=source, columns=columns, width=400, height=280)

    return file_html(data_table, CDN, "DASHBOARD")


def bokeh_dashboard():
    # tools = 'pan'

    def number_of_credits():
        data_for_bokeh = pd.read_csv('app/data/data-for-bokeh.csv', index_col='SK_ID_CURR')
        data_for_bokeh['YEARS_EMPLOYED'] = data_for_bokeh['DAYS_EMPLOYED'] / -365.25
        data_for_bokeh['CLIENT_AGE'] = data_for_bokeh['DAYS_BIRTH'] / -365.25

        data = pd.DataFrame(data_for_bokeh.TARGET.value_counts()).reset_index()
        data['percent'] = data['TARGET'] / sum(data['TARGET']) * 100
        data['index'] = data['index'].astype(str).replace({'True': 'Default', 'False': 'No Default'})
        values = data['index'].unique()

        p = figure(x_range=values, plot_height=200, title="Number of contracts", tools=[HoverTool()],
                   tooltips="@index : @TARGET (@percent{0.2f} %)",
                   toolbar_location=None)

        p.vbar(x="index", top="TARGET", width=0.6, source=data)

        p.xgrid.grid_line_color = None
        p.y_range.start = 0

        p.yaxis[0].formatter = PrintfTickFormatter(format="%6.0f")

        return [p]

    def table_previous_loans():
        data_for_bokeh = pd.read_csv('app/data/data-for-bokeh.csv', index_col='SK_ID_CURR')
        source = ColumnDataSource(data_for_bokeh.sort_values(by='previous_loan_counts', ascending=False).head(10))

        columns = [
            TableColumn(field="SK_ID_CURR", title="SK_ID_CURR"),
            TableColumn(field="previous_loan_counts", title="previous_loan_counts"),
        ]
        data_table = DataTable(source=source, columns=columns, width=400, height=280)

        return [data_table]

    def histograms():
        data_for_bokeh = pd.read_csv('app/data/data-for-bokeh.csv', index_col='SK_ID_CURR')
        data_for_bokeh['YEARS_EMPLOYED'] = data_for_bokeh['DAYS_EMPLOYED'] / -365.25
        data_for_bokeh['CLIENT_AGE'] = data_for_bokeh['DAYS_BIRTH'] / -365.25

        def create_hist(df, column_name, target_name):
            data_hist = {}
            bins = [x * 5 for x in range(0, 14)]
            index_names = ['[{}-{}['.format(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]
            index_names[-1] = '[{}+'.format(bins[-1])
            data_hist['names'] = index_names

            for t in df[target_name].unique():
                series_temp = df.loc[df[target_name] == t, column_name]
                hist = np.histogram(series_temp, bins=bins)
                if t:
                    data_hist["Default"] = hist[0]
                else:
                    data_hist["No Default"] = hist[0]

            return data_hist

        data_hist_AGE = create_hist(data_for_bokeh, "CLIENT_AGE", "TARGET")
        data_hist_CREDIT = create_hist(data_for_bokeh, "CREDIT_TERM", "TARGET")
        data_hist_YEARS = create_hist(data_for_bokeh, "YEARS_EMPLOYED", "TARGET")

        xrange = data_hist_AGE["names"]
        colors = ["#c9d9d3", "#718dbf"]
        target = ["Default", "No Default"]

        # Creation des histogrammes
        hist_AGE_CDS = ColumnDataSource(data=data_hist_AGE)
        hist_CREDIT_CDS = ColumnDataSource(data=data_hist_CREDIT)
        hist_YEARS_CDS = ColumnDataSource(data=data_hist_YEARS)

        # Dummy pour remplir l'histogramme dans un premier temps
        source_dummy = ColumnDataSource(data=data_hist_AGE)

        source = source_dummy

        p = figure(x_range=xrange, plot_height=250, title="Number of clients by age",
                   toolbar_location=None, tools="hover",
                   tooltips=[("Range", "@{}".format('names')), ("Number", "@$name")],
                   x_axis_label="Age range (in years)",
                   y_axis_label="Count")

        # Histograms
        p.vbar_stack(target, x="names", width=0.9, color=colors, source=source,
                     legend_label=target)

        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_right"
        p.legend.orientation = "horizontal"

        # Menu de sélection
        # Actions lors du changement

        handler = CustomJS(args=dict(source=source,
                                     hist_AGE_CDS=hist_AGE_CDS, hist_CREDIT_CDS=hist_CREDIT_CDS,
                                     hist_YEARS_CDS=hist_YEARS_CDS), code="""

            if (cb_obj.value=="Clients age") {
              source.data = hist_AGE_CDS.data
            } else if (cb_obj.value=='Credit Term'){
              source.data = hist_CREDIT_CDS.data
            } else {
              source.data = hist_YEARS_CDS.data
            }
            """)

        handler_2 = CustomJS(args=dict(xaxis=p.xaxis[0]), code="""

            if (cb_obj.value=="Clients age") {
              xaxis.axis_label = 'Age range (in years)'
            } else if (cb_obj.value=='Credit Term'){
              xaxis.axis_label = 'Years of credit'
            } else {
              xaxis.axis_label = 'Years employed'
            }
            """)

        handler_3 = CustomJS(args=dict(p=p), code="""

            if (cb_obj.value=="Clients age") {
              p.title.text = 'Number of clients by age'
            } else if (cb_obj.value=='Credit Term'){
              p.title.text = 'Number of clients by credit term'
            } else {
              p.title.text = 'Number of clients by years employed'
            }
            """)

        # Selecteur
        select = Select(title="Value to show:", options=["Clients age", 'Credit Term', 'Years employed'])
        select.js_on_change('value', handler)
        select.js_on_change('value', handler_2)
        select.js_on_change('value', handler_3)

        return [column(select, p)]

    layout = grid([
        [number_of_credits(),
         table_previous_loans()],
        histograms(),
    ], sizing_mode='stretch_both')

    return file_html(layout, CDN, "DASHBOARD")


def feature_importances(credit_id):
    test = pd.read_csv('app/data/m_test.csv', index_col='SK_ID_CURR')
    loaded_model = pickle.load(open('app/models/finalized_model.sav', 'rb'))

    feature_importance = pd.DataFrame({'feature': list(test.columns),
                                       'importance': loaded_model.feature_importances_})
    feature_importance = feature_importance.merge(test.loc[int(credit_id), :].reset_index(),
                                                  left_on='feature', right_on='index').drop(
        columns='index').sort_values('importance',
                                     ascending=False).head(10)

    feature_importance = feature_importance.rename(columns={int(credit_id): 'value'})
    feature_importance['Name'] = ['Years of credit', 'Years employed', 'Days since last phone change', 'Age',
                                  'What the client actually paid on previous credit on this installment(sum of minimum)',
                                  'Annuity payment', 'Credit amount',
                                  'Installments left to pay on the previous credit (max of mean)',
                                  'How many days before current application did client apply for Credit Bureau credit '
                                  '(max)',
                                  'How many days before the application did client change the identity document with '
                                  'which he applied for the loan']

    # Convert columns to correct values
    feature_importance.loc[feature_importance.feature == 'DAYS_EMPLOYED', 'value'] = feature_importance.loc[
                                                                                         feature_importance.feature == 'DAYS_EMPLOYED', 'value'] / -365.25
    feature_importance.loc[feature_importance.feature == 'DAYS_EMPLOYED', 'feature'] = 'YEARS_EMPLOYED'
    feature_importance.loc[feature_importance.feature == 'DAYS_BIRTH', 'value'] = feature_importance.loc[
                                                                                      feature_importance.feature == 'DAYS_BIRTH', 'value'] / -365.25
    feature_importance.loc[feature_importance.feature == 'DAYS_BIRTH', 'feature'] = 'AGE'
    feature_importance.loc[feature_importance.feature == 'bureau_DAYS_CREDIT_max', 'value'] = - \
        feature_importance.loc[feature_importance.feature == 'bureau_DAYS_CREDIT_max', 'value']
    feature_importance.loc[feature_importance.feature == 'DAYS_ID_PUBLISH', 'value'] = -feature_importance.loc[
        feature_importance.feature == 'DAYS_ID_PUBLISH', 'value']
    feature_importance.loc[feature_importance.feature == 'DAYS_LAST_PHONE_CHANGE', 'value'] = - \
        feature_importance.loc[feature_importance.feature == 'DAYS_LAST_PHONE_CHANGE', 'value']

    # Bokeh Figure
    yrange = feature_importance.sort_values(by='importance').feature.to_list()
    source = ColumnDataSource(data=feature_importance)
    source.data['color'] = Spectral10
    p = figure(y_range=yrange, x_range=(300, 1700), plot_height=400, title="Features importance",
               tools=[HoverTool()], tooltips="@Name : @value{f}",
               toolbar_location=None)

    p.hbar(y='feature', right='importance', height=0.9, color='color', source=source)

    p.xgrid.grid_line_color = None

    return [p]


