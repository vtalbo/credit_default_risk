# -*- coding: utf-8 -*-
import pandas as pd
import pickle
import lightgbm
from app.functions.bokeh_plot import feature_importances
from bokeh.models.widgets import Div
from bokeh.layouts import layout
from bokeh.resources import CDN
from bokeh.embed import file_html


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
        if result[0]:
            name = 'DENIED.png'
        else:
            name = 'ACCEPTED.png'
        div_image = Div(text='<img src="/static/' + name + '">', height=200)
        p = feature_importances(credit_id)
        layouts = layout([[div_image], [p], ], sizing_mode="scale_height")

        return file_html(layouts, CDN, "Loan Acceptance")

    except KeyError:
        return "Cet ID n'est pas présent dans notre base de données"
