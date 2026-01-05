# Fichier : web_app.py
# Serveur minimaliste pour l'analyse dynamique de sécurité (OWASP ZAP)(serveur de l'application web)

from flask import Flask, jsonify

app = Flask(__name__)

# Route d'accueil simple
@app.route('/', methods=['GET'])
def home():
    # Retourne une réponse pour prouver que le serveur est actif
    return jsonify({"status": "OK", "message": "Serveur ERP web actif pour les tests de sécurité."})

# Simule une route d'API courante dans votre application
@app.route('/products', methods=['GET', 'POST'])
def products():
    # ZAP utilisera cette route pour injecter des payloads
    return jsonify({"data": "Données de produits simulées"})

if __name__ == '__main__':
    # ESSENTIEL : Écoute sur toutes les interfaces (0.0.0.0) et le port 8080
    app.run(host='0.0.0.0', port=8080, debug=False)