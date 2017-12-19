from flask import Flask
from flask import current_app as app
from flask import Blueprint, request, g, url_for, render_template, redirect
from jinja2 import exceptions

import MySQLdb
import numpy
from utils import get_db 
# Vytvoří nový blueprint s názvem "TW_bp" a uloží ho to proměnné blueprint
blueprint = Blueprint('TW_bp', __name__)


