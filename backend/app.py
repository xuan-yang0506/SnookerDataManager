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

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

@app.route('/api/setup', methods=["GET"])
def put_data():
    write = request.args.get("write")

    data_dir = "../data/snooker/"
    filename_list = {'matches_r.csv', 
                    'players_r.csv',
                    'tournaments.csv', 
                    'World_Rankings.csv'}
    index_map = {}
    index_map['matches_r.csv'] = ["0", "1", "5", "7"]
    index_map['players_r.csv'] = ["2", "3", "4", "5"]
    index_map['tournaments.csv'] = ["0", "2", "3", "4"]
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
    player1_name = None if player1_name == 'null' else player1_name
    player2_name = None if player2_name == 'null' else player2_name
    tournament = None if tournament == 'null' else tournament
    year = None if year == 'null' else year

    if player1_name is None and player2_name is None and tournament is None and year is None:
        return {}

    def mapFuncP1(data_address):
        url = data_address + '?orderBy="5"'
        if player1_name is not None:
            url += '&equalTo"' + player1_name + '"'
        data = requests.get(url).json()
        output = []
        if type(data) is dict:
            for key in data.keys():
                output.append(data[key])
            return output
        else:
            return data

    def combineFunc(value, element):
        return value + element

    def mapFuncP2(data_address):
        url = data_address + '?orderBy="7"'
        if player2_name is not None:
            url += '&equalTo"' + player2_name + '"'
        data = requests.get(url).json()
        output = []
        if player2_name is not None:
            for key in data.keys():
                output.append(data[key])
            return output
        else:
            return data

    def mapFuncTournament(data_address):
        url = data_address + '?orderBy="3"'
        if tournament is not None:
            url += '&equalTo="' + tournament + '"'
        data = requests.get(url).json()
        output = []
        if tournament is not None:
            for key in data.keys():
                output.append(data[key])
            return output
        else:
            return data

    def mapFuncYear(data_address):
        url = data_address + '?orderBy="2"'
        if year is not None:
            url += '&equalTo="' + year + '"'
        data = requests.get(url).json()
        output = []
        if year is not None:
            for key in data.keys():
                output.append(data[key])
            return output
        else:
            return data

    playerFilter = None
    if player1_name is not None:
        playerFilter = main.map_reduce("/snooker/matches_r.csv", mapFuncP1, combineFunc, num_partition)
    elif player2_name is not None:
        playerFilter = main.map_reduce("/snooker/matches_r.csv", mapFuncP2, combineFunc, num_partition)

    if playerFilter is None:
        playerFilter = main.map_reduce("/snooker/matches_r.csv", mapFuncP1, combineFunc, num_partition)

    playerFilterResult = []
    for item in playerFilter:
        if len(item) >= 7 and (player1_name is None or player1_name == item[5]) and \
            (player2_name is None or player2_name == item[7]):
            playerFilterResult.append(item)

    if tournament is not None:
        tournamentFilter = main.map_reduce("/snooker/tournaments.csv", mapFuncTournament, combineFunc, num_partition)
    else:
        tournamentFilter = main.map_reduce("/snooker/tournaments.csv", mapFuncYear, combineFunc, num_partition)

    tournamentFilterResult = []
    for item in tournamentFilter:
        if (tournament is None or tournament == item[3]) and \
            (year is None or year == item[2]):
            tournamentFilterResult.append(item)

    if playerFilterResult is None and tournamentFilterResult is None:
        return {}
    elif playerFilterResult is None:
        return tournamentFilterResult
    elif tournamentFilterResult is None:
        return playerFilterResult
    else:
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
        print(output)
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
def search_tournaments():
    tournament = request.args.get("tournament")
    year = request.args.get("year")
    tournament = None if tournament == 'null' else tournament
    year = None if year == 'null' else year

    def mapFuncTournament(data_address):
        url = data_address + '?orderBy="3"'
        if tournament is not None:
            url += '&equalTo="' + tournament + '"'
        data = requests.get(url).json()
        output = []
        if tournament is not None:
            return list(data.values())
        else:
            return data
    def combineFunc(value, element):
        return value + element
    tournamentResult = main.map_reduce("/snooker/tournaments.csv", mapFuncTournament, combineFunc, num_partition)

    def mapFuncYear(data_address):
        url = data_address + '?orderBy="2"'
        if year is not None:
            url += '&equalTo="' + year + '"'
        data = requests.get(url).json()
        output = []
        if year is not None:
            for key in data.keys():
                output.append(data[key])
            return output
        else:
            return data
    yearResult = main.map_reduce("/snooker/tournaments.csv", mapFuncYear, combineFunc, num_partition)
        
    result = intersection(tournamentResult, yearResult)
    return jsonify(result)

@app.route('/api/getTournamentsList', methods=['GET'])
def get_tournaments():
    '''get a list of all unique tournaments' names'''
    def mapFunc(data_address):
        data = requests.get(data_address).json()
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

@app.route('/api/terminal', methods=['GET'])
def terminal():
    command = request.args.get("command")
    if command == 'null':
        return {}
    else:
        command = command.split(' ')
        result = main.terminal(command)
        return jsonify(result)
    
@app.route('/api/searchRank', methods=['GET'])
def search_rank():
    year = request.args.get("year")
    name = request.args.get("name")
    
    year = None if year == 'null' else year
    name = None if name == 'null' else name
    
    if year is not None:
        def mapFunc(data_address):
            url = data_address + '?orderBy="0"&equalTo="' + year + '"'
            output = []
            data = requests.get(url).json()
            for item in data.values():
                row = []
                if len(item) >= 4 and item[0] != 'Year' and item[3].isnumeric() and item[3] != "0":
                    if name and name != item[1] + ' ' + item[2]:
                        continue
                    row.append(item[0])
                    row.append(item[1])
                    row.append(item[2])
                    row.append(item[3])
                    output.append(row)
            return output
    elif name is not None:
        first_name, last_name = name.split(' ')
        def mapFunc(data_address):
            url = data_address + '?orderBy="2"&equalTo="' + last_name + '"'
            output = []
            data = requests.get(url).json()
            for item in data.values():
                row = []
                if len(item) >= 4 and item[0] != 'Year' and item[3].isnumeric() and item[3] != "0":
                    if first_name != item[1]:
                        continue
                    row.append(item[0])
                    row.append(item[1])
                    row.append(item[2])
                    row.append(item[3])
                    output.append(row)
            return output
    
    def combineFunc(element, value):
        return element + value
    
    result = main.map_reduce("/snooker/World_Rankings.csv", mapFunc, combineFunc, num_partition)
    result.sort(key = lambda x: int(x[3]))
    return jsonify(result)
    
def create_tree(json, curdir):
    if curdir != "/":
        split = main.split_path(curdir)
        filename = split[-1]
    else:
        filename = "root"
    subdir = main.ls(curdir)
    json["id"] = filename
    json["name"] = filename
    json["children"] = []
    for sub in subdir:
        if curdir != "/":
            json["children"].append(create_tree({}, curdir + "/" + sub))
        else:
            json["children"].append(create_tree({}, curdir + sub))
    return json

@app.route('/api/getNaviData', methods=['GET'])
def get_navi_data():
    root = "/"
    return jsonify(create_tree({}, root))

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
    