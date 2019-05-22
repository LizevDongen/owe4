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
@app.route('/blast', methods=['get', 'post'])
def blast():
    """Van hier uit wordt de blast geregeld.
    Het haalt de sequentie op uit de template en brengt het naar functie is_dna
    om te kijken wat voor functie het is. Vervolgens brengt het de sequentie 
    naar de juiste BLAST en transcribeert het de sequentie als er RNA gegeven
    is.
    :return: de HTML pagina van BLAST.
    """
    sequentie = request.form.get("Sequentie")
    print(sequentie)
    blastdictionary = None
    if not sequentie == None:
        sequentie = sequentie.strip()
        type = is_dna(sequentie)  # Deze functie kijkt wat voor type het is
        print(type)
        if type == "DNA":
            print("Ik ben in DNA, moet niet")
            blastdictionary = BlastN(sequentie)  # Dit is BLASTn
        elif type == "RNA":
            print("Ik ben in RNA, gaat fout")
            sequentie == back_transcribe(sequentie)  # Dit transcribeert het 
            blastdictionary = BlastN(sequentie)  # Dit is ook BLASTn
        elif type == "eiwit":
            blastdictionary = BlastX(sequentie)  # Dit is BLASTx
        elif type == "Fout":
            blastdictionary = None
            print("Dit is geen goede sequentie")
    return render_template('blast.html',
                           data=blastdictionary)  # Dit is de site


def is_dna(sequentie):
    """Dit wordt aangeroepen door de BLAST functie er kijkt wat het type is
    van de sequentie.
    :param sequentie: de ingevoerde sequentie
    :return: een string met het type van de sequentie
    """
    print(sequentie.upper())
    if len(re.findall(r"[ATCG]", sequentie)) == len(sequentie):
        return "DNA"
    elif not back_transcribe(sequentie) == sequentie:
        return "RNA"
    elif len(
            re.findall(r"[ARNDBC EQZGHILKMFPSTWYV]", sequentie.upper())) == len(
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
