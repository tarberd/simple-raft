from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        value = request.json['value']
        return 'value: ' + str(value)
    else:
        return 'value: ' + str(value)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)
