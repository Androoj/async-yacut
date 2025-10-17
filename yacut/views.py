from flask import render_template

from . import app
# from .models import URLMap


@app.route('/')
def index_view():
    return render_template('main.html')