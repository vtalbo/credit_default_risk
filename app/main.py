# -*- coding: utf-8 -*-
import json
# import requests

from flask import Flask, render_template, jsonify, request
from jinja2 import Template

from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.iris import flowers

from app.functions import predict_credit, predict_credit_page
from app.functions.bokeh_plot import bokeh_table, bokeh_plot, bokeh_dashboard, feature_importances

app = Flask(__name__)

page = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
  {{ resources }}
</head>
<body>
  <div id="myplot"></div>
  <div id="myplot2"></div>
  <script>
  fetch('/plot')
    .then(function(response) { return response.json(); })
    .then(function(item) { return Bokeh.embed.embed_item(item); })
  </script>
  <script>
  fetch('/plot2')
    .then(function(response) { return response.json(); })
    .then(function(item) { return Bokeh.embed.embed_item(item, "myplot2"); })
  </script>
</body>
""")

colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
colors = [colormap[x] for x in flowers['species']]


def make_plot(x, y):
    p = figure(title="Iris Morphology", sizing_mode="fixed", plot_width=400, plot_height=400)
    p.xaxis.axis_label = x
    p.yaxis.axis_label = y
    p.circle(flowers[x], flowers[y], color=colors, fill_alpha=0.2, size=10)
    return p


@app.route('/')
def bokeh():
    return bokeh_dashboard()


@app.route('/test_credit')
def form():
    return render_template('form.html')


@app.route('/result_credit', methods=['POST', 'GET'])
def result_credit():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/test_credit' to submit credit_ID"
    if request.method == 'POST':
        return predict_credit_page(request.form['credit_ID'])
        # return feature_importances(request.form['credit_ID'])


@app.route('/hello')
def root():
    return page.render(resources=CDN.render())


@app.route('/plot')
def plot():
    from bokeh.embed import json_item
    import json

    import pandas as pd

    # Load the table
    application_train = pd.read_csv('home-credit-default-risk/application_train.csv')
    # Work on data
    data = pd.DataFrame(application_train.TARGET.value_counts()).reset_index()
    data['percent'] = data['TARGET'] / sum(data['TARGET']) * 100
    print(max(data.percent))
    data['index'] = data['index'].astype(str)
    values = data['index'].unique()

    # from bokeh.io import output_file, show
    from bokeh.models import PrintfTickFormatter
    from bokeh.plotting import figure
    from bokeh.models.tools import HoverTool

    p = figure(sizing_mode="fixed", plot_width=400, plot_height=400, x_range=values,
               title="Target Counts",
               tools=[HoverTool()],
               tooltips="number of contracts : @TARGET (@percent{0.2f} %)",
               toolbar_location=None)

    p.vbar(x="index", top="TARGET", width=0.6, source=data)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    p.yaxis[0].formatter = PrintfTickFormatter(format="%6.0f")

    return json.dumps(json_item(p, 'myplot'))


@app.route('/plot2')
def plot2():
    p = make_plot('sepal_width', 'sepal_length')
    return json.dumps(json_item(p))


@app.route('/dashboard/')
def dashboard():
    return "Bienvenue sur le <i>dashboard</i>"
