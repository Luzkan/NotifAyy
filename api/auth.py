import flask

app = flask.Flask(__name__)

users = [
    {
        'id': 1,
        'username': 'user1',
        'password': 'pass1'
    },
    {
        'id': 2,
        'username': 'user2',
        'password': 'pass2'
    },
    {
        'id': 3,
        'username': 'user3',
        'password': 'pass3'
    }
]

changes = [
    '''{
        'discordId': 367723606832316417,
        'change': 'change 1'
    },
    {
        'discordId': 702627599138029620,
        'change': 'change 2'
    }'''
]

@app.route('/', methods=['GET'])
def empty():
    return '<h1>Response</h1>'


@app.route('/login', methods=['GET'])
def login():
    req = flask.request
    if not req.json:
        flask.abort(400)
    for user in users:
        if user['username'] == req.json['username'] and user['password'] == req.json['password']:
            return flask.jsonify(user)
    return None, 400


@app.route('/users', methods=['GET'])
def getUsers():
    return flask.jsonify(users)


@app.route('/register', methods=['POST'])
def register():
    req = flask.request
    if not req.json:
        flask.abort(400)
    user = {
        'id': users[-1]['id'] + 1,
        'username': req.json['username'],
        'password': req.json['password']
    }
    users.append(user)
    return flask.jsonify(user), 201


@app.route('/changes', methods=['GET'])
def getChanges():
    return flask.jsonify(changes)


if __name__ == '__main__':
    app.run(debug=True)