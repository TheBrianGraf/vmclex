from flask import Flask, render_template
from flask_assets import Bundle, Environment
import os

app = Flask(__name__)

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)

VMTENV = os.environ.copy()

@app.route('/')
def homepage():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)