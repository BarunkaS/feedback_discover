from flask import Flask
from flask import current_app as app
from flask import Blueprint, request, g, url_for, render_template, redirect
from jinja2 import exceptions

import MySQLdb
import numpy

# Vytvoří nový blueprint s názvem "TW_bp" a uloží ho to proměnné blueprint
blueprint = Blueprint('TW_bp', __name__)
db = MySQLdb.connect("localhost", "root", "Bluepurse22", "Feedback_Discover", use_unicode = True)
db.set_character_set("utf8")
db.cursor().execute("SET CHARACTER SET utf8")

@blueprint.route('/TW_fdbk')
