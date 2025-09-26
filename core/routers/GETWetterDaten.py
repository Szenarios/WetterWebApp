from flask import request, jsonify
from main import app


@app.route('/get_coords')
def get_coords():
    x = request.args.get('x')
    y = request.args.get('y')
    print(f"Geklickt bei: x={x}, y={y}")
    return jsonify({'message': 'Koordinaten empfangen', 'x': x, 'y': y})
