from flask import render_template, flash, jsonify, redirect, session, url_for, request, g
from app import app
from wtforms import TextAreaField, StringField
import checkvpn
# Python flask view handlers
@app.route('/')
@app.route('/index')
def index():
    #form = StoryForm()
    results = checkvpn.test_vpc_status()
    return render_template('index.html',
                           title='Calix AWS VPN Monitor',
                           results=results)
                           

