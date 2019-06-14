# Namen: Robert Rijksen, Lize van Dongen en Annemieke Schönthaler
# Functie: Het visualiseren van een MySQL database via verschillende
# functies en HTML5 pagina's, waardoor er een werkende webapplicatie onstaat
# Datum: 13-06-2019
# Versie 1.2


from flask import Flask, request, render_template
import mysql.connector
from Bio.Blast import NCBIXML, NCBIWWW
import re
from tabulate import tabulate
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def connectie():
    """Deze functie runt de app
    :return: homepagina met informatie over de website
    """

    return render_template('Home.html')  # roept home html pagina aan


def database_optie1():
    """Deze functie haalt met een query alle resultaten op uit de zelf gekozen
    column om vervolgens de accessiecode doormiddel van een for loop te
    veranderen in een hyperlink naar de NCBI website
    :return: de resultaten uit de mysql database, hierbij is de module
    tabulate gebruikt
    """
    alle_resultaten = [['<b>Sequentie ID</b>', '<b>Naam organisme</b>',
                        '<b>Omschrijving eiwit</b>', '<b>Accessie code</b>',
                        '<b>Query cover resultaat</b>', '<b>E value</b>',
                        '<b>Percentage identity</b>']]
    woord = request.form.get('woord')
    categorie = request.form.get('categorie')
    conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = conn.cursor()
    if len(woord) + len(categorie) == 0:
        cursor.execute("""select Resultaten_Blast.Sequentie_ID, Naam_organisme, 
            Omschrijving_eiwit, Accessie_code, Query_cover_resultaat, E_value, 
            Percentage_Identity, Taxonomie_Tax_ID, Header from Resultaten_Blast 
            join Onderzoeks_sequenties on 
            (Resultaten_Blast.Sequentie_ID=Onderzoeks_sequenties.Sequentie_ID)
            order by E_value Asc;""")
    else:
        cursor.execute("""select Resultaten_Blast.Sequentie_ID, Naam_organisme, 
            Omschrijving_eiwit, Accessie_code, Query_cover_resultaat, E_value, 
            Percentage_Identity, Taxonomie_Tax_ID, Header from Resultaten_Blast 
            join Onderzoeks_sequenties on 
            (Resultaten_Blast.Sequentie_ID=Onderzoeks_sequenties.Sequentie_ID)
            where {} like '%{}%'order by E_value Asc;""".format(categorie,
                                                                woord))

    rows = cursor.fetchall()
    for x in rows:
        print(x)
        if x is not None:
            lijst_x = list(x)
            for n, i in enumerate(lijst_x):
                if i == x[0]:
                    lijst_x[n] = '<div class ="tooltip" > {} '.format(x[0]) \
                                 + '<span class ="tooltiptext" > Dit is ' \
                                   'header: <br>{} </span> </div>'.format(
                        x[8])
                    lijst_x[n].strip('\'')
                elif i == x[3]:
                    lijst_x[n] = '<a href="https://' \
                                 'www.ncbi.nlm.nih.gov/protein/{}"</a>' \
                                     .format(x[3]) + x[3]
                    alle_resultaten.append(lijst_x)
            del lijst_x[7]
            del lijst_x[7]
    return tabulate(alle_resultaten, tablefmt='html')


@app.route('/database')
def database():
    """Dit roept de HTML pagina van database aan als /database in wordt gegeven
    :return:
    """
    return render_template('database.html')  # Dit is de database HTML pagina


@app.route('/resultaat', methods=['get', 'post'])
def resultaat_database():
    resultaat = database_optie1()
    return render_template('database.html') + resultaat


@app.route('/grafieken')
def grafieken():
    """Deze functie maakt grafieken en plaatst ze in de template.
    :return: de HTML pagina
    """
    top_3_organismen_grafiek()  # Functie die grafiek aanmaakt over de database
    top_10_hoogste_scores()  # Functie die grafiek aanmaakt over de database
    return render_template('grafieken.html')  # Dit is de grafieken HTML pagina


def top_3_organismen_grafiek():
    """Deze functie haalt de 3 meest voorkomende organismen op uit de db en
    maakt hier een grafiek van die het opslaat in static.
    :return: de grafiekgrafiek
    """
    # Connectie is constant opnieuw aangeroepen omdat de
    # connectie met de database anders verbroken was.
    conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = conn.cursor()
    cursor.execute(
        """SELECT Naam_organisme, count(*) FROM Resultaten_Blast 
           WHERE Naam_organisme <> "" GROUP BY Naam_organisme 
           ORDER BY count(*) DESC LIMIT 3;""")
    # Query die de 3 meest voorkomende organisme zoekt
    rows = cursor.fetchall()
    organisme = []
    aantal_organisme = []
    for x in rows:
        organisme.append(x[0])
        aantal_organisme.append(x[1])
    width = 0.5
    plt.bar(organisme, aantal_organisme, width, color=('g', 'r', 'blue'))
    # Maken van de grafiek
    plt.title('De meest voorkomende organismen')
    plt.xlabel('Organisme')
    plt.ylabel('Aantal organisme')
    plt.xticks(rotation=8)
    plt.savefig("static/top_3_organisme.png")


def top_10_hoogste_scores():
    # Connectie is constant opnieuw aangeroepen omdat de
    # connectie met de database anders verbroken was.
    conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = conn.cursor()
    cursor.execute(
        """select Naam_organisme, E_value, Percentage_Identity 
           from Resultaten_Blast order by E_value, Percentage_Identity desc 
           limit 10""")
    # Query die de laagste E-value vind en hoogste Percentage idenity
    rows = cursor.fetchall()
    organisme = []
    e_value = []
    for x in rows:
        organisme.append(x[0])
        e_value.append(x[2])
    explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    fig1, ax1 = plt.subplots()
    tot = sum(e_value) / 100.0
    autopct = lambda x: "%d" % round(x * tot)  # maken grafiek
    plt.rc('xtick', labelsize=7)

    ax1.pie(e_value, explode=explode, labels=organisme,
            autopct=autopct,
            shadow=True, startangle=90)

    plt.title('De laagste E-values en hoogste Percentage Identities')
    ax1.axis('equal')

    plt.tight_layout()
    plt.savefig('static/top_5_Evalue.png')


@app.route('/blast')
def blast():
    """Deze functie haalt de template van de blast pagina op
    :return: BLAST pagina
    """
    return render_template('blast.html')  # roept BLAST pagina aan


def sequentie_id_ophaler():
    """ Deze functie haalt het hoogste sequentie ID op om deze vervolgens
    door te geven,
    zodat als er een resultaat wordt toegevoegd aan de database, deze een
    nieuw uniek nummer krijgt
    :return: ID bij toegevoegde sequentie
    """
    # Connectie is constant opnieuw aangeroepen omdat de
    # connectie met de database anders verbroken was.
    conn = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = conn.cursor()
    cursor.execute('select max(Sequentie_ID) from Onderzoeks_sequenties;')
    # query die max sequenties ID zoekt
    rows = cursor.fetchone()
    for x in rows:
        return x


def blastx():
    """
    Deze functie BLASTx, blast met het programma blastx. Het heeft 2 global
     lijsten om
    vervolgens deze te vullen met de resultaten van de blast. De lijsten zijn
     global omdat deze
    doorgegeven kunnen worden zonder de hele functie (met daarbij het blasten)
     opnieuw uit te voeren
     :return: uitgevoerde BLAST met BLASTx
    """
    global onderzoeks_sequentie
    global resultaten_blasten
    # Om ervoor te zorgen dat je constant bij de resultaten van de BLAST kon,
    # kon ik niet anders (denk ik) dan de lijsten global te maken.
    # Sorry Teuntje
    onderzoeks_sequentie = []
    resultaten_blasten = []
    seqid = sequentie_id_ophaler()
    sequentie = request.form.get("Sequentie")
    # instellingen BLAST
    blastx_type = NCBIWWW.qblast(program='blastx', database='nr',
                                 sequence=str(sequentie), format_type='XML',
                                 hitlist_size=1)
    # Hieronder worden de resultaten opgeslagen in de globale lijsten om deze
    # later te kunnen inserten in de database
    for record in NCBIXML.parse(blastx_type):
        if record.alignments:
            for align in record.alignments:
                for hsp in align.hsps:
                    resultaten_blasten.append(seqid + 1)
                    resultaten_blasten.append(re.search("([A-Z][a-z]*) "
                                                        "([a-z]+)",
                                                        align.title)
                                              .group())
                    resultaten_blasten.append(align.title)
                    resultaten_blasten.append(re.search(r'\|[A-Z]+.*?[0-9]\|',
                                                        align.title).group()
                                              .replace('|', ''))
                    resultaten_blasten.append(((hsp.align_length /
                                                len(sequentie)) * 100))
                    resultaten_blasten.append(hsp.expect)
                    resultaten_blasten.append(((hsp.identities /
                                                hsp.align_length) * 100))
                    onderzoeks_sequentie.append(seqid + 1)
                    onderzoeks_sequentie.append(sequentie)


def blast_opslaan_database():
    """" Deze functie Slaat alles op de database
    """
    # Connectie is constant opnieuw aangeroepen omdat de
    # connectie met de database anders verbroken was.
    try:
        conn = mysql.connector.connect(
            host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
            # maakt connectie met de database
            user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
            db="rohtv", password='pwd123')
        cursor = conn.cursor()
        cursor.execute(  # Query die de sequentie opslaat in de database
            """insert into Onderzoeks_sequenties(Sequentie_ID, Sequentie, 
               Header) values {};""".format(tuple(onderzoeks_sequentie)))
        conn.commit()
        cursor.execute(  # Query die de resulaten opslaat in de database
            """insert into Resultaten_Blast(Sequentie_ID, Naam_organisme,
               Omschrijving_eiwit, Accessie_code, Query_cover_resultaat, 
               E_value, Percentage_Identity) values {};""".format(
                tuple(resultaten_blasten)))
        conn.commit()
        return 0

    except mysql.connector.errors.IntegrityError:
        # Als er deze error verschijnt, is de sequentie niet te gebruiken bij
        # de BLAST
        return 1

    except mysql.connector.errors.DataError:
        # Als er deze error verschijnt, is het resultaat te onvolledige bij
        # om op te slaan in de database, of de resultaten staan als in de
        # database
        return 2


@app.route('/blastresultaten', methods=['get', 'post'])
def blastresultaten():
    """Van hier uit wordt de blast geregeld.
    Het haalt de sequentie op uit de template en brengt het naar functie is_dna
    om te kijken wat voor functie het is. Vervolgens brengt het de sequentie
    naar de juiste BLAST en transcribeert het de sequentie als er RNA gegeven
    is.
    :return: de HTML pagina van BLAST.
    """
    try:
        seq = request.form['Sequentie'].upper()
        x = is_dna(seq)
        if x != "Fout":
            if request.form['BLAST'] == 'BLASTn':  # BLAST met BLASTn
                resultaten_blastn = blast_overig('blastn', seq)
                return \
                    render_template('BLAST_resultaten_zonder_opslaan.html') + \
                    resultaten_blastn
            elif request.form['BLAST'] == 'BLASTx':  # BLAST met BLASTx
                blastx()
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
            elif request.form['BLAST'] == 'BLASTp':  # BLAST met BLASTp
                resultaten_blastp = blast_overig('blastp', seq)
                return \
                    render_template('BLAST_resultaten_zonder_opslaan.html') + \
                    resultaten_blastp
            elif request.form['BLAST'] == 'tBLASTx':  # BLAST met tBLASTx
                resultaten_tblastx = blast_overig('tblastx', seq)
                return \
                    render_template('BLAST_resultaten_zonder_opslaan.html') + \
                    resultaten_tblastx
        else:
            # wanneer er een niet geldige sequentie wordt ingevoerd
            return render_template('blast.html') + \
                   '&emsp;<b><br> Dit is geen geldige sequentie, ' \
                   'probeer opnieuw!</b>'
    except ValueError:
        # Wanneer men een value Error krijgt, krijgt de BLAST geen geldige
        # sequentie door, hierdoor wordt deze error afgevangen
        return render_template('blast.html') + '&emsp;<b><br> Dit is ' \
                                               'waarschijnlijk geen geldige ' \
                                               'sequentie voor deze blast, ' \
                                               'probeer opnieuw!</b>'


@app.route('/opslaan_database', methods=['get', 'post'])
def opslaan_database():
    """ BLAST resultaten wel of niet opslaan in de database
    :return: resultaten opgeslagen in de database
    """
    if request.form['checked'] == 'opslaan':
        header = request.form['Header']
        if len(header) != 0:
            onderzoeks_sequentie.append(header)
        else:
            niks = ' '
            onderzoeks_sequentie.append(niks)
        blast_opslaan_database()  # Roept functie aan met de queries die de
        # resultaten / sequenties opslaat
        # hieronder worden het bericht gegeven dat de resultaten opgeslagen
        # zijn
        x = blast_opslaan_database()
        if x == 0:
            return render_template('BLAST_resultaten_zonder_opslaan.html') + \
                   '<article class="card"> <header> <h3>De resultaten zijn ' \
                   'succesvol opgeslagen!</h3> </header> </article> '
        elif x == 1:
            return render_template('BLAST_resultaten_zonder_opslaan.html') + \
                   '<article class="card"> <header> <h3>Deze accessiecode ' \
                   'is al succesvol opgeslagen!</h3> </header> </article> '
        elif x == 2:
            return render_template('BLAST_resultaten_zonder_opslaan.html') + \
                   '<article class="card"> <header> <h3>Deze resultaten zijn' \
                   ' te onvolledig om op te slaan in de database!</h3> ' \
                   '</header> </article> '
    else:
        # hieronder worden het bericht gegeven dat de resultaten niet
        # opgeslagen zijn
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
    # kijken of het DNA is
    if len(re.findall(r"[ATCG]", sequentie)) == len(sequentie):
        return "DNA"
    # kijken of het RNA is
    elif len(re.findall(r"[AUCG]", sequentie)) == len(sequentie):
        return "RNA"
    elif len(
            re.findall(r"[ARNDBC EQZGHILKMFPSTWYV]",  # kijken of het eiwit is
                       sequentie)) == len(sequentie):
        return "eiwit"
    else:
        return "Fout"


def blast_overig(blast_type, sequentie):
    """Dit is BLAST_overig. Het blast als gewoonlijk met als score matrix
    BLOSUM62
    en als database nr.
    :param sequentie: de sequentie die gegeven is
    :param blast_type: het blast programma wat meegegeven is
    :return: de string met de resultaten van de BLAST
    """
    result_blast = ''
    # instellingen BLAST
    result_handle = NCBIWWW.qblast(blast_type, "nr", sequentie,
                                   matrix_name="BLOSUM62",
                                   hitlist_size=1)
    blast_record = NCBIXML.read(result_handle)
    # Hieronder worden de BLAST resultaten opgeeslagen in een string
    # + een HTML enter teken, zodat deze gereturned word om netjes onder elkaar
    # op de HTML pagina zichtbaar te worden
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            result_blast += "<b>****Alignment****</b> <br>"
            result_blast += ("Beschrijving: " + alignment.title
                             + '<br>')
            result_blast += ('Accessiecode: ' +
                             (re.search(r"\|[A-Z]+.*?[0-9]\|",
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
    app.run(debug=True)

