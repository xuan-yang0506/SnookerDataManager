from flask import Flask
from flask import jsonify, request
import pandas

import sys
sys.path.append("..")
from src import main

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/api/searchPlayers', methods=['GET'])
def search_players():
    # print(request.json)
    # return jsonify('Hello World')
    name = request.args.get("name")
    country = request.args.get("country")
    if name is not None:
        name_split = name.split(" ")
        first_name = name_split[0].lower()
        last_name = name_split[1].lower()
        if country is not None:
            def mapFunc(data):
                output = []
                for item in data:
                    if item[2].lower() == first_name and item[3].lower() == last_name and item[5] == country:
                        output.append(item)
                return output
        else:
            def mapFunc(data):
                output = []
                for item in data:
                    if item[2].lower() == first_name and item[3].lower() == last_name:
                        output.append(item)
    elif country is not None:
        def mapFunc(data):
            output = []
            for item in data:
                if item[5] == country:
                    output.append(item)
            return output
    def combineFunc(value, element):
        return value + element
    result = main.map_reduce("/user/players_r.csv", mapFunc, combineFunc, 3)
    return jsonify(result)



@app.route('/api/getCountries', methods=['GET'])
def get_countries():
    df = pandas.read_csv('data/snooker/players_r.csv')
    countries = df['country'].unique()
    return jsonify(countries.tolist())


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
    