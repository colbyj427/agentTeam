from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json()
    index = data['index']
    player = data['player']
    # Logic to handle moves and check game status would be added here
    return jsonify({'status': 'success', 'index': index, 'player': player})

if __name__ == '__main__':
    app.run(debug=True)