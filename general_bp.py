from flask import Flask
from flask import current_app as app
from flask import Blueprint, request, g, url_for, render_template, redirect
from jinja2 import exceptions
from io import BytesIO
import base64

import MySQLdb
import numpy 

import matplotlib.pyplot as plt


# Vytvoří nový blueprint s názvem "general_bp" a uloží ho to proměnné blueprint
blueprint = Blueprint('general_bp', __name__)
db = MySQLdb.connect("localhost", "root", "Bluepurse22", "Feedback_Discover", use_unicode = True)
db.set_character_set("utf8")
db.cursor().execute("SET CHARACTER SET utf8")

# Zaregistruje funkci show_general() jako funkci, kterou má Flask zavolat, když 
# uživatel otevře v prohlížeči stránku "/general"
@blueprint.route('/general')
def show_general():
    
    cur = db.cursor()
    cur.execute('SELECT count(Answer) FROM Feedback_Discover.Answer where question_id = 2')
    answerCount = cur.fetchone()[0]

    cur = db.cursor()
    cur.execute('SELECT count(idAgendaItemBlock) FROM Feedback_Discover.AgendaItemBlock')
    aibCount = cur.fetchone()[0]

    cur = db.cursor()
    cur.execute('SELECT count(Answer) FROM Feedback_Discover.Answer where question_id = 2 and answer = \'Ano\' ')
    impactCount = cur.fetchone()[0]

    #data pro graf známek
    listCourses = []
    scaleDataGraph = []

    cur = db.cursor()
    cur.execute('SELECT idAgendaItem, `name`, size FROM Feedback_Discover.AgendaItem where item_type = \'C\'')

    courses = cur.fetchall()

    gradesQuestionId = 49
    chartEntries = []

    for course in courses:
        cur.execute(("SELECT answer FROM Feedback_Discover.Answer "
                 "join AgendaItemBlock on Answer.agenda_item_block_id = AgendaItemBlock.idAgendaItemBlock "
                 "join AgendaItem on AgendaItem.idAgendaItem = AgendaItemBlock.agenda_item_AiB_id "
                 "where question_id = %s AND idAgendaItem = %s"), (gradesQuestionId, course[0]))
        rows = cur.fetchall()
        integerGrades = []

        for row in rows:
            try:
                integerGrades.append(float(row[0]))  
            except ValueError as e:
                print('number could not be converted: ' + row[0])

        averageGrade = numpy.mean(integerGrades)

        chartEntry = {"courseID": course[0], "courseName": course[1], "courseSize": course[2], "averageGrade": averageGrade}
        chartEntries.append(chartEntry)


    courseNames = []
    averageGrades = []
    #graf známky
    for chartEntry in chartEntries:
        courseNames.append(chartEntry["courseName"])
        averageGrades.append(chartEntry["averageGrade"])

    plt.rcdefaults()
    plt.rcParams["figure.figsize"] = (8, 3 * len(courseNames) / 10)
    plt.rcParams.update({'font.size': 8})
    plt.rcParams.update({'figure.autolayout': True})
    plt.tight_layout()
    fig, ax = plt.subplots()

    y_pos = numpy.arange(len(courseNames))

    ax.grid(color='gray', linestyle='-', linewidth=0.5)
   
    ax.barh(y_pos, averageGrades, height=0.4, align='center',
            color='#00a65a', ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(courseNames)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Kurzy')
    ax.set_title('Průměrné známky za kurzy')

    
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figdata_png = base64.b64encode(figfile.getvalue())
    
    try:
        return render_template('general.html', answerCount=answerCount, aibCount=aibCount, impactCount=impactCount, chartEntries=chartEntries, figdata_png = figdata_png.decode('utf8'))
    except exceptions.TemplateSyntaxError as ex:
        return "Template error: " + ex.filename + " on line " + str(ex.lineno)
