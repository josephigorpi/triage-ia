from flask import Flask, jsonify, request

app = Flask(__name__)

# Datos de ejemplo
antecedentes = {
    1: ["Hipertensión", "Diabetes tipo 2"],
    2: ["Asma"],
}

@app.route('/pacientes/<int:id_paciente>/antecedentes', methods=['GET'])
def get_antecedentes(id_paciente):
    return jsonify({"antecedentes": antecedentes.get(id_paciente, [])})

@app.route('/triaje', methods=['POST'])
def recibir_triaje():
    data = request.json
    print(f"Triaje recibido en HCE: {data}")
    return jsonify({"status": "ok"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)