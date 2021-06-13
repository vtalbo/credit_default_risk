# -*- coding: utf-8 -*-
import pandas as pd
import pickle


def predict_credit(credit_id):
    """From credit_id, get the prediction of the credit failure or not
    If the credit_id does not exist, an error is shown"""
    try:
        test = pd.read_csv('m_test_10.csv', index_col='SK_ID_CURR')
        x = test.loc[int(credit_id), :]
        # load the model from disk
        loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
        return "OK ?"
        # Predict payment default
        result = loaded_model.predict(x.to_numpy().reshape(1, -1))
        if result[0]:
            return "CRÉDIT REFUSÉ"
        else:
            return "CRÉDIT ACCEPTÉ"
    except KeyError:
        return "Cet ID n'est pas présent dans notre base de données"
