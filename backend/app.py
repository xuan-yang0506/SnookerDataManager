from flask import Flask
from flask import jsonify, request
import pandas
import requests

import sys
sys.path.append("..")
from src import main

app = Flask(__name__)

num_partition = 20
METADATA_ROOT_URL = main.METADATA_ROOT_URL

@app.route('/api/setup', methods=["GET"])
def put_data():
    write = request.args.get("write")

    data_dir = "../data/"
    filename_list = {'matches_r.csv', 
                    'players_r.csv',
                    'tournaments.csv', 
                    'World_Rankings.csv'}
    index_map = {}
    index_map['matches_r.csv'] = ["0", "1", "5", "7"]
    index_map['players_r.csv'] = ["2", "3", "4", "5"]
    index_map['tournaments.csv'] = ["0", "2", "4"]
    index_map['World_Rankings.csv'] = ["0", "1", "2", "3"]

    if write == "1":
        main.init_database()
        main.mkdir("/snooker")
        for filename in filename_list:
            main.put(data_dir + filename, "/snooker", num_partition)

    rules = {}
    rules["rules"] = {}
    rules["rules"][".read"] = "true"
    rules["rules"][".write"] = "true"

    for filename in filename_list:
        url = METADATA_ROOT_URL + '/snooker' + '.json'
        metadata = requests.get(url).json()
        filename_hash = main.get_hash(filename)
        cur_dur = metadata[filename_hash]
        block_locations = cur_dur['block_locations']
        node_to_block = {}
        for block in block_locations.keys():
            node_list = block_locations[block]
            for node in node_list:
                if node not in node_to_block.keys():
                    node_to_block[node] = []
                node_to_block[node].append("id_" + filename_hash + "_" + block)
        for node in node_to_block.keys():
            if node not in rules["rules"]:
                rules["rules"][node] = {}
            for block in node_to_block[node]:
                if block not in rules["rules"][node].keys():
                    rules["rules"][node][block] = {}    
                rules["rules"][node][block][".indexOn"] = index_map[filename]



    return jsonify(rules)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/api/searchPlayers', methods=['GET'])
def search_players():
    name = request.args.get("name")
    country = request.args.get("country")
    name = None if name == 'null' else name
    country = None if country == 'null' else country
    
    if not name and not country:
        return {}
    elif not name:
        def mapFunc(data_address):
            url = data_address + f'?orderBy="5"&equalTo="{country}"'
            data = requests.get(url).json()
            data = list(data.values())
            return data
    elif not country:
        def mapFunc(data_address):
            url = data_address + f'?orderBy="4"&equalTo="{name}"'
            data = requests.get(url).json()
            data = list(data.values())
            return data
    else:
        def mapFunc(data_address):
            url = data_address + f'?orderBy="4"&equalTo="{name}"'
            data = requests.get(url).json()
            data = list(data.values())
            output = []
            for item in data:
                if country.lower() in item[5].lower():
                    output.append(item)
            return output
    def combineFunc(value, element):
        return value + element
    result = main.map_reduce("/snooker/players_r.csv", mapFunc, combineFunc, num_partition)
    return jsonify(result)

@app.route('/api/searchGames', methods=['GET'])
def search_games():
    player1_name = request.args.get("player1")
    player2_name = request.args.get("player2")
    tournament = request.args.get("tournament")
    year = request.args.get("year")
    # format params
    player1_name = None if player1_name == '' else player1_name
    player2_name = None if player2_name == '' else player2_name
    tournament = None if tournament == '' else tournament
    year = None if year == '' else year

    if player1_name is None and player2_name is None and tournament is None and year is None:
        return {}
    else:
        def mapFuncPlayer(data):
            if data is None:
                return []
            output = []
            for item in data:
                if len(item) >= 8 and \
                    (player1_name is None or player1_name.lower() in item[5].lower()) and \
                    (player2_name is None or player2_name.lower() in item[7].lower()):
                    output.append(item)
            return output
        def combineFuncPlayer(value, element):
            return value + element
        playerFilterResult = main.map_reduce("/snooker/matches_r.csv", mapFuncPlayer, combineFuncPlayer, num_partition)

        def mapFuncTournament(data):
            if data is None:
                return []
            output = []
            for item in data:
                if len(item) >= 4 and \
                    (year is None or year == item[2]) and \
                    (tournament is None or tournament.lower() in item[3].lower()):
                    output.append(item)
            return output
        def combineFuncTournament(value, element):
            return value + element
        tournamentFilterResult = main.map_reduce("/snooker/tournaments.csv", mapFuncTournament, combineFuncTournament, num_partition)

        tournamentMap = {}
        output = []
        for item in tournamentFilterResult:
            tournamentId = item[0]
            tournamentMap[tournamentId] = item

        for item in playerFilterResult:
            tournamentId = item[0]
            if tournamentId in tournamentMap.keys():
                newItem = []
                newItem += item
                newItem += tournamentMap[tournamentId]
                output.append(newItem)
        return jsonify(output)

@app.route('/api/getCountriesList', methods=['GET'])
def get_countries():
    def mapFunc(data_address):
        url = data_address
        data = requests.get(url).json()
        countries = set(map(lambda x: x[5], data))
        return countries

    def combineFunc(value, element):
        return value.union(element)
    result = main.map_reduce("/snooker/players_r.csv", mapFunc, combineFunc, num_partition)
    result = sorted(list(result))
    return jsonify(result)

@app.route('/api/searchTournaments', methods=['GET'])
def gsearch_tournaments():
    tournament = request.args.get("tournament")
    year = request.args.get("year")
    def mapFunc(data):
        if data is None:
            return []
        output = []
        for item in data:
            if (tournament is None or tournament.lower() in item[3].lower()) and \
                (year is None or year.lower() in item[2]) and \
                item[2] != "year":
                output.append(item)
        return output
    def combineFunc(value, element):
        return value + element
    result = main.map_reduce("/snooker/tournaments.csv", mapFunc, combineFunc, num_partition)
    return jsonify(result)

@app.route('/api/getTournamentsList', methods=['GET'])
def get_tournaments():
    '''get a list of all unique tournaments' names'''
    def mapFunc(data_address):
        url = data_address + '?orderby="name"'
        data = requests.get(url).json()
        data = set(map(lambda x: x[3], data))
        return data
    
    def combineFunc(value, element):
        return value.union(element)
    
    result = main.map_reduce("/snooker/tournaments.csv", mapFunc, combineFunc, num_partition)
    result = sorted(list(result))
    return jsonify(result)

@app.route('/api/getPlayersList', methods=['GET'])
def get_players():
    '''get a list of all unique players' names'''
    def mapFunc(data_address):
        data = requests.get(data_address).json()
        data = list(map(lambda x: x[4], data))
        return data

    def combineFunc(value, element):
        return value + element
    
    result = main.map_reduce("/snooker/players_r.csv", mapFunc, combineFunc, num_partition)
    result = sorted(result)
    return jsonify(result)
    
if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
    