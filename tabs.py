from flask import Flask, render_template
app = Flask(__name__)

tabs = [
    {
        'name':'tab 1',
        'url':'https://google.com'
    },
    {
        'name':'tab 2',
        'url':'https://google.ru'
    }
]

@app.route('/')
@app.route('/home')
def hello():
    return render_template('layout.html', tabs=tabs)

if __name__ == '__main__':
    app.run(debug=True)