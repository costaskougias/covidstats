from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd
import requests
import os
import re

app = Flask(__name__)


def covid():
    # Create DataFrame from html table
    tables = pd.read_html('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data', header=0)
    df = pd.DataFrame(tables[0])

    # Reformating the table
    del df['Ref.']
    df.drop(df.columns[0], axis=1, inplace=True)
    df.drop(df.tail(2).index, inplace=True)
    df.rename(
        columns={'Location[a].1': 'Location', 'Cases[b]': 'Cases', 'Deaths[c]': 'Deaths', 'Recov.[d]': 'Recovered'},
        inplace=True)

    l = []
    for x in df['Location'].values.tolist():
        l.append(re.sub(r'(\[.*?\])', "", x))

    n = df.columns[0]
    df.drop(n, axis=1, inplace=True)
    df[n] = l

    df = df[['Location', 'Cases', 'Deaths', 'Recovered']]
    df = df.loc[1:]

    # Connect to MongoDB
    client = MongoClient('mongodb', 27017)
    db = client['covid-data']
    collection = db['covid']
    collection.insert_many(df.to_dict('records'))


@app.route('/')
def index():
    tables = pd.read_html('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data', header=0)
    df = pd.DataFrame(tables[0])
    cases = df['Cases[b]'].values.tolist()[0]
    deaths = df['Deaths[c]'].values.tolist()[0]
    recovered = df['Recov.[d]'].values.tolist()[0]
    return render_template('index.html', cases=cases, deaths=deaths, recovered=recovered)


# Run the app
if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    covid()
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)
