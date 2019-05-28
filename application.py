from flask import Flask, request, render_template
import mysql.connector
from Bio.Seq import Seq, transcribe, translate, back_transcribe
from Bio.Blast import NCBIXML, NCBIWWW
import re
from tabulate import tabulate
import matplotlib.pyplot as plt



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
    categorie = request.form.get('categorie')
    cursor.execute(
        """select Resultaten_Blast.Sequentie_ID, Naam_organisme, 
            Omschrijving_eiwit, Accessie_code, Query_cover_resultaat, E_value, 
            Percentage_Identity, Taxonomie_Tax_ID, Header from Resultaten_Blast 
            join Onderzoeks_sequenties on 
            (Resultaten_Blast.Sequentie_ID=Onderzoeks_sequenties.Sequentie_ID)
            where {} like '%{}%'order by E_value Asc;""".format(categorie, woord))
    rows = cursor.fetchall()
    for x in rows:
        if x != None:
            lijst_x = list(x)
            for n, i in enumerate(lijst_x):
                if i == x[0]:
                    lijst_x[n] = '<div class ="tooltip" > {} '.format(x[0]) \
                                 + '<span class ="tooltiptext" > Dit is header: <br>{} </span> </div>'.format(
                        x[8])
                    lijst_x[n].strip('\'')
                    del lijst_x[8]
                elif i == x[3]:
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
    resultaat = database_optie1()
    return render_template('database.html') + resultaat


@app.route('/grafieken')
def grafieken():
    """Deze functie haalt de grafieken op en plaatst ze in de template.
    :return: de HTML pagina
    """
    top_3_organismen_grafiek()
    top_3_hoogste_scores()
    return render_template('grafieken.html')


def top_3_organismen_grafiek():
    """Deze functie haalt de 3 meest voorkomende organismen op uit de db en
    maakt hier een grafiek van die het opslaat in static.
    :return: de grafiekgrafiek
    """
    cursor = conn.cursor()
    cursor.execute(
        'SELECT Naam_organisme, count(*) FROM Resultaten_Blast WHERE Naam_organisme <> "" GROUP BY Naam_organisme ORDER BY count(*) DESC LIMIT 3;')
    rows = cursor.fetchall()
    organisme = []
    aantal_organisme = []
    for x in rows:
        organisme.append(x[0])
        aantal_organisme.append(x[1])
    width = 0.5
    plt.bar(organisme, aantal_organisme, width, color=('g', 'r', 'blue'))
    plt.title('De meest voorkomende organismen')
    plt.xlabel('Organisme')
    plt.ylabel('Aantal organisme')
    plt.text(5, 5, "kip")
    plt.savefig("static/top_3_organisme.png")


def top_3_hoogste_scores():
    cursor = conn.cursor()
    cursor.execute(
        'select Naam_organisme, E_value, Percentage_Identity from Resultaten_Blast order by E_value, Percentage_Identity desc limit 10')
    rows = cursor.fetchall()
    organisme = []
    aantal_organisme = []
    for x in rows:
        organisme.append(x[0])
        aantal_organisme.append(x[2])
    explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    fig1, ax1 = plt.subplots()
    tot = sum(aantal_organisme) / 100.0
    autopct = lambda x: "%d" % round(x * tot)
    plt.rc('xtick', labelsize=7)

    ax1.pie(aantal_organisme, explode=explode, labels=organisme,
            autopct=autopct,
            shadow=True, startangle=90)

    plt.title('De hoogste E-values en Percentage Identities')
    ax1.axis('equal')

    plt.tight_layout()
    plt.savefig('templates/top_5_Evalue.png')
        
        
@app.route('/blast')
def blast():
    return render_template('blast.html')

def sequentie_id_ophaler():
    """ Deze functie haalt het hoogste sequentie ID op om deze vervolgens door te geven,
    zodat als er een resultaat wordt toegevoegd aan de database, deze een nieuw uniek nummer krijgt
    """
    conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        # maakt connectie met de database
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = conn.cursor()
    cursor.execute('select max(Sequentie_ID) from Onderzoeks_sequenties;')
    rows = cursor.fetchone()
    for x in rows:
        return x


def BLASTx():
    """ Deze functie BLASTx, blast met het programma blastx. Het heeft 2 global lijsten om
    vervolgens deze te vullen met de resultaten van de blast. De lijsten zijn global omdat deze
    door gegeven kunnen worden zonder de hele functie (met daarbij het blasten) opnieuw uit te voeren
    """
    global onderzoeks_sequentie
    global resultaten_blasten
    onderzoeks_sequentie = []
    resultaten_blasten = []
    seqID = sequentie_id_ophaler()
    sequentie = request.form.get("Sequentie")
    blastx = NCBIWWW.qblast(program='blastx', database='nr',
                            sequence=str(sequentie), format_type='XML',
                            hitlist_size=1)
    for record in NCBIXML.parse(blastx):
        if record.alignments:
            for align in record.alignments:
                for hsp in align.hsps:
                    resultaten_blasten.append(seqID+1)
                    resultaten_blasten.append(re.search("([A-Z][a-z]*) "
                                                        "([a-z]+)",align.title)
                                              .group())
                    resultaten_blasten.append(align.title)
                    resultaten_blasten.append(re.search('\|[A-Z]+.*?[0-9]\|',
                                                        align.title).group()
                                              .replace('|', ''))
                    resultaten_blasten.append(((hsp.align_length /
                                                len(sequentie)) * 100))
                    resultaten_blasten.append(hsp.expect)
                    resultaten_blasten.append(((hsp.identities /
                                                hsp.align_length) * 100))
                    onderzoeks_sequentie.append(seqID+1)
                    onderzoeks_sequentie.append(sequentie)


def blast_opslaan_database():
    """" Deze functie pakt de global lijsten en vult daarmee de database
    """
    conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        # maakt connectie met de database
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = conn.cursor()
    cursor.execute('insert into Onderzoeks_sequenties(Sequentie_ID, Sequentie, Header) values {};'.format(tuple(onderzoeks_sequentie)))
    conn.commit()
    cursor.execute('insert into Resultaten_Blast(Sequentie_ID, Naam_organisme, Omschrijving_eiwit, Accessie_code, Query_cover_resultaat, E_value, Percentage_Identity) values {};'.format(tuple(resultaten_blasten)))
    conn.commit()


@app.route('/blastresultaten', methods=['get', 'post'])
def blastresultaten():
    """Van hier uit wordt de blast geregeld.
    Het haalt de sequentie op uit de template en brengt het naar functie is_dna
    om te kijken wat voor functie het is. Vervolgens brengt het de sequentie
    naar de juiste BLAST en transcribeert het de sequentie als er RNA gegeven
    is.
    :return: de HTML pagina van BLAST.
    """
    seq = request.form['Sequentie'].upper()
    x = is_dna(seq)
    if x != "Fout":
        if request.form['BLAST'] == 'BLASTn':
            resultaten_blastn = Blast_overig('blastn', seq)
            return \
                render_template('BLAST_resultaten_zonder_opslaan.html') +\
                resultaten_blastn
        elif request.form['BLAST'] == 'BLASTx':
            BLASTx()
            return \
                render_template('BLAST_resultaten_zonder_opslaan.html') + \
                '<hr>' + '<b>Resultaten BLASTx </b> <br>' + '<br>' + \
                'Accessiecode: ' + str(resultaten_blasten[3]) + '<br>' + \
                'Beschrijving: ' + str(resultaten_blasten[2]) + '<br>' \
                + 'E-value: ' + str(resultaten_blasten[5]) + \
                '<br>' + 'Query cover: ' + str(resultaten_blasten[4]) + \
                '<br>' + 'Percentage identity: ' + \
                str(resultaten_blasten[6]) + '<br>' + \
                render_template('opslaan_database_knoppen.html')
        elif request.form['BLAST'] == 'BLASTp':
            resultaten_blastp = Blast_overig('blastp', seq)
            return \
                render_template('BLAST_resultaten_zonder_opslaan.html') + \
                resultaten_blastp
        elif request.form['BLAST'] == 'tBLASTx':
            resultaten_tblastx = Blast_overig('tblastx', seq)
            return \
                render_template('BLAST_resultaten_zonder_opslaan.html') + \
                resultaten_tblastx
    else:
        return render_template('blast.html') + \
               '&emsp;<b><br> Dit is geen geldige sequentie, ' \
               'probeer opnieuw!</b>'


@app.route('/opslaan_database', methods=['get', 'post'])
def opslaan_database():
    if request.form['checked'] == 'opslaan':
        onderzoeks_sequentie.append(request.form['Header'])
        blast_opslaan_database()
        return render_template('BLAST_resultaten_zonder_opslaan.html') + \
               '<article class="card"> <header> <h3>De resultaten zijn ' \
               'succesvol opgeslagen!</h3> </header> </article> '
    else:
        return render_template('BLAST_resultaten_zonder_opslaan.html') + \
               '<article class="card"> <header> <h3>Dan niet! bedankt voor ' \
               'het gebruikmaken van ons programma!</h3> </header> </article> '


def is_dna(sequentie):
    """Dit wordt aangeroepen door de BLAST functie er kijkt wat het type is
    van de sequentie.
    :param sequentie: de ingevoerde sequentie
    :return: een string met het type van de sequentie
    """
    sequentie = sequentie.upper()
    if len(re.findall(r"[ATCG]", sequentie)) == len(sequentie):
        return "DNA"
    elif len(re.findall(r"[AUCG]", sequentie)) == len(sequentie):
        return "RNA"
    elif len(
            re.findall(r"[ARNDBC EQZGHILKMFPSTWYV]",
                       sequentie)) == len(
        sequentie):
        return "eiwit"
    else:
        return "Fout"


def Blast_overig(blast, sequentie):
    """Dit is BLAST_overig. Het blast als gewoonlijk met als score matrix BLOSUM62
    en als database nr.
    :param sequentie: de sequentie die gegeven is 
    :param blast: het blast programma wat meegegeven is
    :return:
    """
    result_blast = ''
    result_handle = NCBIWWW.qblast(blast, "nr", sequentie,
                                   matrix_name="BLOSUM62",
                                   hitlist_size=1)
    blast_record = NCBIXML.read(result_handle)
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            result_blast += "<b>****Alignment****</b> <br>"
            result_blast += ("Beschrijving: " + alignment.title
                             + '<br>')
            result_blast += ('Accessiecode: ' +
                             (re.search('\|[A-Z]+.*?[0-9]\|',
                                        alignment.title).group()
                              .replace('|', '')) + '<br>')
            result_blast += ("Length: " + str(alignment.length)
                             + '<br>')
            result_blast += ("E-value: " + str(hsp.expect) + '<br>')
            result_blast += ('Query cover: ' + str((hsp.align_length /
                                                          len(sequentie))
                                                          * 100) + '<br>')
            result_blast += ('Identity: ' + str((hsp.identities /
                                                        hsp.align_length)
                                                       * 100) + '<br>')

    return result_blast


if __name__ == '__main__':
    app.run()
