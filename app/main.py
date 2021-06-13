# -*- coding: utf-8 -*-
import json
import requests

from flask import Flask, render_template, jsonify, request
from jinja2 import Template

from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.iris import flowers

from app.functions import predict_credit

app = Flask(__name__)

METEO_API_KEY = "eca2a5529b4d4dc680113093041c5a8f"  # Remplacez cette ligne par votre clé OPENWEATHERMAP

if METEO_API_KEY is None:
    # URL de test :
    METEO_API_URL = "https://samples.openweathermap.org/data/2.5/forecast?lat=0&lon=0&appid=xxx"
else:
    # URL avec clé :
    METEO_API_URL = "https://api.openweathermap.org/data/2.5/forecast?lat=48.883587&lon=2.333779&appid=" + METEO_API_KEY

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


@app.route('/test_credit')
def form():
    return render_template('form.html')


@app.route('/result_credit', methods=['POST', 'GET'])
def result_credit():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/test_credit' to submit credit_ID"
    if request.method == 'POST':
        return predict_credit(request.form['credit_ID'])


def make_plot(x, y):
    p = figure(title="Iris Morphology", sizing_mode="fixed", plot_width=400, plot_height=400)
    p.xaxis.axis_label = x
    p.yaxis.axis_label = y
    p.circle(flowers[x], flowers[y], color=colors, fill_alpha=0.2, size=10)
    return p


@app.route('/api/meteo/')
def meteo():
    response = requests.get(METEO_API_URL)
    content = json.loads(response.content.decode('utf-8'))

    if response.status_code != 200:
        return jsonify({
            'status': 'error',
            'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(
                content['message'])
        }), 500

    data = []  # On initialise une liste vide
    for prev in content["list"]:
        datetime = prev['dt'] * 1000
        temperature = prev['main']['temp'] - 273.15  # Conversion de Kelvin en °c
        temperature = round(temperature, 2)
        data.append([datetime, temperature])

    return jsonify({
        'status': 'ok',
        'data': data
    })


@app.route("/hello")
def hello():
    return "Hello World!"


@app.route('/')
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
