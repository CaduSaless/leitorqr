from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from PIL import Image
from io import BytesIO


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def home():
    if not request.json or 'image' not in request.json:
        return jsonify({'error': 'Dados de imagem ausentes no JSON'}), 400

    image_data_url = request.get_json()
    image_data_url = image_data_url['image']

    try:
        header, base64_data = image_data_url.split(',', 1)
    except ValueError:
        return jsonify({'error': 'Formato de URL de dados inválido'}), 400

    try:
        image_bytes = base64.b64decode(base64_data)
    except base64.binascii.Error:
        return jsonify({'error': 'Dados base64 inválidos'}), 400

    # 3. Abrir a imagem com Pillow
    try:
        image = Image.open(BytesIO(image_bytes))
    except IOError:
        return jsonify({'error': 'Não foi possível abrir a imagem. Dados corrompidos?'}), 400


    width, height = image.size
    print(f"Largura: {width}, Altura: {height}")

    gray_image = image.convert('L')
    resized_image = image.resize((1080, 720))
    output_path = "processed_image.png"
    try:
        resized_image.save(output_path)
        print(f"Imagem processada salva em: {output_path}")
    except Exception as e:
        print(f"Erro ao salvar a imagem: {e}")

    # Retornar uma resposta de sucesso
    return jsonify({'message': 'Imagem recebida e processada com sucesso!', 'width': width, 'height': height}), 200

if '__main__' == __name__:
    app.run(debug=True)