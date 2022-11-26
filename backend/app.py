from flask import Flask
from flask import jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/api/searchPlayers', methods=['POST'])
def searchPlayers():
    print(request.json)
    return jsonify('Hello World')


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
    