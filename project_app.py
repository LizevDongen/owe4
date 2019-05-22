from flask import Flask, request, render_template
import mysql.connector
from tabulate import tabulate

app = Flask(__name__)

conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        # maakt connectie met de database
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
cursor = conn.cursor()


@app.route('/', methods=['get', 'post'])
def connectie():
    """
    maakt connectie met de database en run de app
    input: zoekwoord en categorie
    output: applicatie met resultaten uit de database
    """

    return render_template('Lize.html') #roept html pagina aan


def database_optie1():
    alle_resultaten = [['<b>Sequentie ID</b>', '<b>Naam organisme</b>',
                        '<b>Omschrijving eiwit</b>', '<b>Accessie code</b>',
                        '<b>Query cover resultaat</b>', '<b>E value</b>',
                        '<b>Percentage identity</b>',
                        '<b>Taxonomie tax ID</b>']]
    woord = request.form.get('woord')
    cursor.execute(
        "select * from Resultaten_Blast where Naam_organisme like '%{}%'".format(
            woord))
    rows = cursor.fetchall()
    for x in rows:
        if x != None:
            lijst_x = list(x)
            for n, i in enumerate(lijst_x):
                if i == x[3]:
                    lijst_x[
                        n] = '<a href="https://www.ncbi.nlm.nih.gov/protein/{}"</a>'.format(
                        x[3]) + x[3]
                    alle_resultaten.append(lijst_x)
                    return tabulate(alle_resultaten, tablefmt='html')


def database_optie2():
    alle_resultaten = [['<b>Sequentie ID</b>', '<b>Naam organisme</b>',
                        '<b>Omschrijving eiwit</b>', '<b>Accessie code</b>',
                        '<b>Query cover resultaat</b>', '<b>E value</b>',
                        '<b>Percentage identity</b>',
                        '<b>Taxonomie tax ID</b>']]
    woord = request.form.get('woord')
    cursor.execute(
        "select * from Resultaten_Blast where Omschrijving_eiwit like '%{}%'".format(
            woord))
    rows = cursor.fetchall()
    for x in rows:
        if x != None:
            lijst_x = list(x)
            for n, i in enumerate(lijst_x):
                if i == x[3]:
                    lijst_x[
                        n] = '<a href="https://www.ncbi.nlm.nih.gov/protein/{}"</a>'.format(
                        x[3]) + x[3]
                    alle_resultaten.append(lijst_x)
                    return tabulate(alle_resultaten, tablefmt='html')


def database_optie3():
    alle_resultaten = [['<b>Sequentie ID</b>', '<b>Naam organisme</b>',
                        '<b>Omschrijving eiwit</b>', '<b>Accessie code</b>',
                        '<b>Query cover resultaat</b>', '<b>E value</b>',
                        '<b>Percentage identity</b>',
                        '<b>Taxonomie tax ID</b>']]
    woord = request.form.get('woord')
    cursor.execute(
        "select * from Resultaten_Blast where Accessie_code like '%{}%'".format(
            woord))
    rows = cursor.fetchall()
    for x in rows:
        if x != None:
            lijst_x = list(x)
            for n, i in enumerate(lijst_x):
                if i == x[3]:
                    lijst_x[
                        n] = '<a href="https://www.ncbi.nlm.nih.gov/protein/{}"</a>'.format(
                        x[3]) + x[3]
                    alle_resultaten.append(lijst_x)
                    return tabulate(alle_resultaten, tablefmt='html')


@app.route('/database')
def database():
    return render_template('database.html')


@app.route('/resultaat', methods=['get', 'post'])
def resultaat_database():
    categorie = request.form.get('categorie')
    if categorie == 'Naam_organisme':
        resultaat = database_optie1()
        return render_template('database.html') + resultaat
    elif categorie == 'Omschrijving_eiwit':
        resultaat = database_optie2()
        return render_template('database.html') + resultaat
    elif categorie == 'Accessie_code':
        resultaat = database_optie3()
        return render_template('database.html') + resultaat

@app.route('/grafieken')
def grafieken():
    return render_template('grafieken.html')

@app.route('/blast')
def blast():
    return render_template('blast.html')


if __name__ == '__main__':
    app.run()
