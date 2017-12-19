
from flask import Flask
from flask import current_app as app
import MySQLdb
import numpy 

# Z flasku naimportuje spoustu různých funkcí, které budeme potřebovat
from flask import Blueprint, request, g, url_for, render_template, redirect
from jinja2 import exceptions

# Vytvoří nový blueprint s názvem "names_bp" a uloží ho to proměnné blueprint
blueprint = Blueprint('names_bp', __name__)
db = MySQLdb.connect("localhost", "root", "Bluepurse22", "Feedback_Discover", use_unicode = True)
db.set_character_set("utf8")
db.cursor().execute("SET CHARACTER SET utf8")
# Pomocná funkce, která se připojí k databázi, pokud je potřeba a vrátí nám
# jako výsledek objekt, který obsahuje ono spojení, nad kterém potom můžeme
# spouštět SQL dotazy
# Zaregistruje funkci show() jako funkci, kterou má Flask zavolat, když uživatel
# otevře v prohlížeči stránku "/" (tedy úvodní stránku)
@blueprint.route('/')
def show():
    # Získá připojení na databázi
    # Pošle databázi "SELECT ..." SQL dotaz a výsledek uloží do proměnné cur
    cur = db.cursor()
    cur.execute('SELECT idAgendaItem, name FROM Feedback_Discover.AgendaItem where item_type = \'C\' ORDER BY name')
    # Načte všechny řádky z výsledku toho SQL dotazu a uloží je do proměnné entries
    entries = cur.fetchall()
    cur.execute('SELECT idAgendaItem, name FROM Feedback_Discover.AgendaItem WHERE item_type = \'TW\' ORDER BY name')
    workshops = cur.fetchall()

    # Pro každý řádek z výsledku udělej...
    for row in entries:
        # ... tenhle print(). V proměnné row je uložený seznam, který odpovídá
        # jednotlivým sloupečkům z SQL tabulky "mytable", na které jsme spustili
        # ten SQL dotaz - když se podíváš nahoru na ten SELECT dotaz, tak vidíš,
        # že jsme chtěli 3 sloupečky: id, name a date. Tady v chceme vypsat do
        # konzole jenom jméno a datum, takže vypíěeme row[1] a row[2] - v row[0]
        # je to id
        print(row[1])

    # Zavolá funkci render_template(), která vezme template names.html, nahradí 
    # v něm "names" za to, co je v proměnné "entries" a vygeneruje výsledné HTML,
    # které vrátí jako výsledek z téhle funkce zpátky do Fasku, a ten ji pošle
    # k uživateli do prohlížeče.
    try:
        return render_template('names.html', names=entries, workshops=workshops)
    except exceptions.TemplateSyntaxError as e:
        return "Template error: " + e.filename + " on line " + str(e.lineno)

@blueprint.route('/course_fdbk/<id>')
def course_fdbk(id):
    # Prumerna znamka za kurz
    cur = db.cursor()
    gradesQuestionId = 49
    cur.execute(("SELECT Answer FROM Feedback_Discover.Answer "
                 "join AgendaItemBlock on Answer.agenda_item_block_id = AgendaItemBlock.idAgendaItemBlock "
                 "join AgendaItem on AgendaItem.idAgendaItem = AgendaItemBlock.agenda_item_AiB_id "
                 "where question_id = %s AND idAgendaItem = %s"), (gradesQuestionId, id))
    rows = cur.fetchall()
    integerGrades = []
    for row in rows:
        try:
            integerGrades.append(float(row[0]))
        except ValueError as e:
                print('number could not be converted: ' + row[0])

    # Impact ANO/NE
    impactQuestionId = 50
    cur.execute(("SELECT count(Answer) FROM Feedback_Discover.Answer join AgendaItemBlock on Answer.agenda_item_block_id = AgendaItemBlock.idAgendaItemBlock join AgendaItem on AgendaItem.idAgendaItem = AgendaItemBlock.agenda_item_AiB_id where question_id = %s AND idAgendaItem = %s AND answer = 'Ano'"), (impactQuestionId, id))
    impactAnoCount = cur.fetchone()[0]

    cur.execute(("SELECT count(Answer) FROM Feedback_Discover.Answer join AgendaItemBlock on Answer.agenda_item_block_id = AgendaItemBlock.idAgendaItemBlock join AgendaItem on AgendaItem.idAgendaItem = AgendaItemBlock.agenda_item_AiB_id where question_id = %s AND idAgendaItem = %s AND answer = 'Ne'"), (impactQuestionId, id))
    impactNeCount = cur.fetchone()[0]

    #Otazky se skalama

    questionIDs = [55, 56, 57, 58, 59, 60]
    scaleData = []

    for i in questionIDs:
        cur.execute("SELECT idQuestion, question_cz, question_en FROM Question where idQuestion = %s", (i,))
        questionText = cur.fetchone()

        cur.execute("SELECT Answer, count(Answer) from Feedback_Discover.Answer join AgendaItemBlock on Answer.agenda_item_block_id = AgendaItemBlock.idAgendaItemBlock join AgendaItem on AgendaItem.idAgendaItem = AgendaItemBlock.agenda_item_AiB_id where question_id = %s and idAgendaItem = %s group by Answer order by Answer" , (i,id))
        answers = []
        maxAnswersPerQuestion = 6

        for i in range(maxAnswersPerQuestion):
            answers.append({"answer": int(i), "value": 0})
        for a in cur.fetchall():
            answers[int(a[0])]["value"] = int(a[1])
                

        data = {"id": i,'question_id':questionText[0], 'question_cz': questionText[1], 'question_en': questionText[2],'answers': answers}
        scaleData.append(data)

    # komentáře
    commentQuestionIDs = [61, 54]
    questionData = []
    for i in commentQuestionIDs:
        cur.execute("SELECT question_cz, question_en FROM Question where idQuestion = %s", (i,))
        questionText = cur.fetchone() 

        cur.execute(("SELECT Answer from Feedback_Discover.Answer join AgendaItemBlock on Answer.agenda_item_block_id = AgendaItemBlock.idAgendaItemBlock join AgendaItem on AgendaItem.idAgendaItem = AgendaItemBlock.agenda_item_AiB_id where question_id = %s AND idAgendaItem = %s;"), (i, id))
        commentsPrint = cur.fetchall()
        answers = []

        for comment in commentsPrint:
            answers.append({"answer": comment[0]})

        questionData.append({"id": i, "question_cz": questionText[0], "question_en": questionText[1], "answers": answers})
       

    cur.execute("SELECT * FROM Feedback_discover.AgendaItem WHERE idAgendaItem = %s",(id,))
    courseName = cur.fetchone()[1]

    # 

    try:
        return render_template('course_fdbk.html', courseName=courseName, grade=numpy.mean(integerGrades), impactAnoCount=impactAnoCount, impactNeCount=impactNeCount, scaleData=scaleData, questionData=questionData)
    except exceptions.TemplateSyntaxError as e:
        return "Template error: " + e.filename + " on line " + str(e.lineno)

