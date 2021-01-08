from flask import Flask, render_template, jsonify
from query import Search

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<query>/<total>')
def search(query, total):
    result = Search().search(query, int(total))
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)