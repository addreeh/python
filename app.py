from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ejecutar_comando_1')
def ejecutar_comando_1():
    result = subprocess.run(['python', 'HSNfuncional.py'], capture_output=True, text=True)
    return result.stdout

@app.route('/ejecutar_comando_2')
def ejecutar_comando_2():
    result = subprocess.run(['python', 'MPfuncional.py'], capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    app.run(debug=True)
