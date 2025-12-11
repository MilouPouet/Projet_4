from flask import Flask, jsonify, request
from src.data_manager import DataManager

app = Flask(__name__)
db = DataManager()

@app.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('search')
    res = db.search_products(search) if search else db.get_all_products()
    return jsonify(res), 200

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    try:
        float(data['prix']); int(data['quantite'])
        db.add_product(data)
        return jsonify({"message": "OK"}), 201
    except: return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
