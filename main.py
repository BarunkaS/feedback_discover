# Z modulu flask naimportuje "Flask" a "g" tak, abychom je mohli
# používat v tomto programu
from flask import Flask, g
# Naimportuje náš modul names_bp (names_bp.py), tak abychom z tohoto souboru
# používat proměnné a funkce, které jsou definované v names_bp.py
import names_bp
# Stejně tak pro general_bp modul
import general_bp
from flask_mysqldb import MySQL

# Vytvoří novou Flask aplikaci a uloží ji do proměnné "DiscoverApp"
DiscoverApp = Flask(__name__)
DiscoverApp.config['MYSQL_HOST'] = 'localhost'
DiscoverApp.config['MYSQL_USER'] = 'root'
DiscoverApp.config['MYSQL_PASSWORD'] = 'Bluepurse22'
DiscoverApp.config['MYSQL_DB'] = 'Feedback_Discover'
DiscoverApp.config['MYSQL_CHARSET'] = 'Utf-8'
# Zaregistruje blueprint z names_bp do naší Flask aplikace - names_bp.blueprint
# odkazuje na proměnnou "blueprint", kterou jsme vytvořili v names_bp.py
DiscoverApp.register_blueprint(names_bp.blueprint)
# Stejně tak zaregistrujeme general_bp blueprint
DiscoverApp.register_blueprint(general_bp.blueprint)
