import uuid
import importlib
from flask import Flask, request, jsonify, Response
from parse_key_info import parse
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={"*": {"origins": "*"}})

@app.route('/uploadPOFile', methods=['POST', 'GET']) 
def uploadPOFile():
    if 'file' not in request.files:
        return 'No file part in the request', 400
    
    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        print(file.filename)
        local_filename = '/tmp/' + str(uuid.uuid4()) + '.pdf'
        # 在这里可以处理文件，例如保存到服务器或者进行其他操作
        file.save(local_filename)  # 保存文件到指定路径
        key_info = parse(local_filename, request.form.get('templateName'))
        module = importlib.import_module('SchemaParser.' + request.form.get('templateName'))
        po_main, po_details, raw_info = module.parse_to_u8_schema(key_info)
        resp = jsonify({
            "po_main": po_main,
            "po_details": po_details,
            "raw_info": raw_info
        })
        return resp, 200

    return 'Error in file upload', 500

if __name__ == '__main__':
    app.run(debug=True)
