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


def grafiek_maker():
    cursor = conn.cursor()
    cursor.execute(
        'SELECT Naam_organisme, count(*) FROM Resultaten_Blast GROUP BY Naam_organisme ORDER BY count(*) DESC LIMIT 3;')
    rows = cursor.fetchall()
    organisme = []
    aantal_organisme = []
    for x in rows:
        organisme.append(x[0])
        aantal_organisme.append(x[1])
    width = 0.5
    plt.bar(organisme, aantal_organisme, width, color=('g', 'r', 'blue'))
    plt.title('Hoeveelheid organisme')
    plt.xlabel('Organisme')
    plt.ylabel('Aantal organisme')
    file = open("static/top_3_organisme.png", "w")
    fig = plt.savefig(file)


@app.route('/database')
def database():
    return render_template('database.html')


@app.route('/resultaat', methods=['get', 'post'])
def resultaat_database():
    resultaat = database_optie1()
    return render_template('database.html') + resultaat


@app.route('/grafieken')
def grafieken():
    grafiek_maker()
    return render_template('grafieken.html')

@app.route('/blast', methods=['get', 'post'])
def blast():
    """Van hier uit wordt de blast geregeld.
    Het haalt de sequentie op uit de template en brengt het naar functie is_dna
    om te kijken wat voor functie het is. Vervolgens brengt het de sequentie
    naar de juiste BLAST en transcribeert het de sequentie als er RNA gegeven
    is.
    :return: de HTML pagina van BLAST.
    """
    blastlijst = request.form.getlist('blast')
    if blastlijst == []:
        output = "vink een optie aan"
    elif len(blastlijst) > 1:
        output = "vink maar 1 optie aan!"
    elif len(blastlijst) == 1:
        for item in blastlijst:
            output = "de aangevinkte optie is" + str(item)

    sequentie = request.form.get("Sequentie")  # Dit haalt de sequentie op
    #print(sequentie)
    blastdictionary = sequentiedoorstuurder(
        sequentie)  # Dit maakt output van de input

    return render_template('blast.html',
                           data=blastdictionary, aangevinkt=output)  # Dit is de site


def sequentiedoorstuurder(sequentie):
    """Deze functie zorgt dat de sequentie goed wordt verwerkt en naar de BLAST
    wordt gestuurd.
    :param sequentie: de opgegeven sequentie
    :return: een dictionary met de resultaten van BLAST
    """
    blastdictionary = None
    if not sequentie == None:
        sequentie = sequentie.strip()
        type = is_dna(sequentie)  # Deze functie kijkt wat voor type het is
        print(type)
        if type == "DNA":
            blastdictionary = BlastN(sequentie)  # Dit is BLASTn
        elif type == "RNA":
            sequentie == back_transcribe(sequentie)  # Dit transcribeert het
            blastdictionary = BlastN(sequentie)  # Dit is ook BLASTn
        elif type == "eiwit":
            blastdictionary = BlastX(sequentie)  # Dit is BLASTx
        elif type == "Fout":
            blastdictionary = None
            print("Dit is geen goede sequentie")
    return blastdictionary


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


def BlastN(sequentie):
    """Dit is BLASTn. Het blast als gewoonlijk met als score matrix BLOSUM62
    en als database nr.
    :param sequentie: de sequentie die gegeven is
    :return: 
    """
    dictionaryn = {}  # Deze dictionary wordt gevuld met de lijsten met info
    descriptionlist_blastn = []
    scientific_name_list_blastn = []
    score_list = []
    e_value_list = []
    pid_list = []
    query_cover_list = []
    accession_code_list = []

    result_handle = NCBIWWW.qblast("blastn", "nr", sequentie,
                                   matrix_name="BLOSUM62",
                                   hitlist_size=10)
    blast_record = NCBIXML.read(result_handle)
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            print("****Alignment****")
            print("sequence:", alignment.title)
            print("length:", alignment.length)
            print("e value:", hsp.expect)
            print('query cover', (hsp.align_length / len(sequentie)) * 100)
            print('identity', (hsp.identities / hsp.align_length) * 100)
            print('score', hsp.score)
            print(hsp.query[0:75] + "...")
            print(hsp.match[0:75] + "...")
            print(hsp.sbjct[0:75] + "...")

            descriptionlist_blastn.append(alignment.title)
            scientific_name_list_blastn.append(
                re.search("([A-Z][a-z]*) ([a-z]+)", alignment.title).group())
            score_list.append(hsp.score)
            e_value_list.append(hsp.expect)
            pid_list.append((hsp.identities / hsp.align_length) * 100)
            query_cover_list.append(hsp.align_length / len(sequentie) * 100)
            accession_code_list.append((
                re.search('[A-Z].*\|',
                          alignment.title).group()).replace(
                '|', ''))

    key = sequentie
    print(key)
    if not key in dictionaryn:
        dictionaryn[key] = descriptionlist_blastn, scientific_name_list_blastn, \
                           accession_code_list, query_cover_list, e_value_list, score_list, pid_list
    else:
        print("Deze sequentie is al geblast")

    return dictionaryn


def BlastX(sequentie):
    """Dit is blastx. Het wordt als gewoonlijk gebruikt en maakt gebruik van
    matrix BLOSUM62 en database nr.
    :param sequentie: de meegegeven sequentie
    :return: 
    """
    dictionaryn = {}  # Deze dictionary wordt gevuld met de lijsten met info
    descriptionlist_blastn = []
    scientific_name_list_blastn = []
    score_list = []
    e_value_list = []
    pid_list = []
    query_cover_list = []
    accession_code_list = []

    result_handle = NCBIWWW.qblast("blastp", "nr", sequentie,
                                   matrix_name="BLOSUM62",
                                   hitlist_size=10)
    blast_record = NCBIXML.read(result_handle)
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            print("****Alignment****")
            print("sequence:", alignment.title)
            print("length:", alignment.length)
            print("e value:", hsp.expect)
            print('query cover', (hsp.align_length / len(sequentie)) * 100)
            print('identity', (hsp.identities / hsp.align_length) * 100)
            print('score', hsp.score)
            print(hsp.query[0:75] + "...")
            print(hsp.match[0:75] + "...")
            print(hsp.sbjct[0:75] + "...")

            descriptionlist_blastn.append(alignment.title)
            scientific_name_list_blastn.append(
                re.search("([A-Z][a-z]*) ([a-z]+)", alignment.title).group())
            score_list.append(hsp.score)
            e_value_list.append(hsp.expect)
            pid_list.append((hsp.identities / hsp.align_length) * 100)
            query_cover_list.append(hsp.align_length / len(sequentie) * 100)
            accession_code_list.append((
                re.search('[A-Z].*\|',
                          alignment.title).group()).replace(
                '|', ''))

    key = sequentie
    print(key)
    if not key in dictionaryn:
        dictionaryn[key] = descriptionlist_blastn, scientific_name_list_blastn, \
                           accession_code_list, query_cover_list, e_value_list, score_list, pid_list
    else:
        print("Deze sequentie is al geblast")

    return dictionaryn


if __name__ == '__main__':
    app.run()
