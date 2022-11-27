from flask import Flask
from flask import jsonify, request
import pandas

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/api/searchPlayers', methods=['POST'])
def searchPlayers():
    print(request.json)
    return jsonify('Hello World')

@app.route('/api/getCountries', methods=['GET'])
def getCountries():
    df = pandas.read_csv('data/snooker/players_r.csv')
    countries = df['country'].unique()
    return jsonify(countries.tolist())


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
    