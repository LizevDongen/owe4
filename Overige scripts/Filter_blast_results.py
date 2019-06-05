# Naam: Robert Rijksen
# Functie: Het netjes schrijven van alle resultaten in een csv bestand waarna
# al dit bestand gebruikt kon worden om alles tegelijk te inserten in mysql
# in de tabel Resultaten_Blast


import mysql.connector
import pickle


def main():
    input_file = open('Volledige_blast', 'rb')
    # Het bestand is het pickle bestand waarin de resultaten van de BLAST
    # in een dictionary staat
    dicti = pickle.load(input_file)
    input_file.close()
    filter_dict(dicti)


def filter_dict(dictionary):
    """
    :param dictionary: De dictionary die hier als parameter mee wordt gegeven
    is dezelfde dictionary die in het BLAST script gepickeled wordt
    """
    verbinding = mysql.connector.connect(
        host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
        user="rohtv@hannl-hlo-bioinformatica-mysqlsrv",
        db="rohtv", password='pwd123')
    cursor = verbinding.cursor()  # de verbinding met de database
    bestand = open('__alle_blast_resultaten__versie2.csv', 'a+')
    for x in dictionary:
        cursor.execute("""select Sequentie_ID from Onderzoeks_sequenties 
                          where Header = '{}'""".format(x))
        # Met bovenstaandde query wordt de sequentie ID opgehaald, zodat deze
        # gekoppeld kan worden aan de header met de juiste BLAST-resultaten
        regel = cursor.fetchone()
        if dictionary[x] != "":
            for y in regel:
                if dictionary[x][0] != '':
                    for i in range(len(dictionary[x][0])):
                        bestand.write(str(y) + ',')
                        # Het is misschien niet zo efficient gedaan om zoveel
                        # if / elifs te gebruiken, maar het is puur om te weten
                        # dat er geen een overgeslagen word zodat elk resultaat
                        # meegenomen kan worden in de database
                        if len(dictionary[x][0][i]) == 0:
                            bestand.write('\'' + ' ' + '\'' + ',')
                            bestand.write('\'' + dictionary[x][1][i] + '\''
                                          + ',')
                            bestand.write('\'' + dictionary[x][2][i] + '\''
                                          + ',')
                            bestand.write(str(dictionary[x][3][i]) + ',')
                            bestand.write(str(dictionary[x][4][i]) + ',')
                            bestand.write(str(dictionary[x][5][i]) + '\n')
                        elif len(dictionary[x][1][i]) == 0:
                            bestand.write('\'' + dictionary[x][0][i] + '\''
                                          + ',')
                            bestand.write('\'' + ' ' + '\'' + ',')
                            bestand.write('\'' + dictionary[x][2][i] + '\''
                                          + ',')
                            bestand.write(str(dictionary[x][3][i]) + ',')
                            bestand.write(str(dictionary[x][4][i]) + ',')
                            bestand.write(str(dictionary[x][5][i]) + '\n')
                        elif len(dictionary[x][2][i]) == 0:
                            bestand.write('\'' + dictionary[x][0][i] + '\''
                                          + ',')
                            bestand.write('\'' + dictionary[x][1][i] + '\''
                                          + ',')
                            bestand.write('\'' + ' ' + '\'' + ',')
                            bestand.write(str(dictionary[x][3][i]) + ',')
                            bestand.write(str(dictionary[x][4][i]) + ',')
                            bestand.write(str(dictionary[x][5][i]) + '\n')
                        else:
                            bestand.write('\'' + dictionary[x][0][i] + '\''
                                          + ',')
                            bestand.write('\'' + dictionary[x][1][i] + '\''
                                          + ',')
                            bestand.write('\'' + dictionary[x][2][i] + '\''
                                          + ',')
                            bestand.write(str(dictionary[x][3][i]) + ',')
                            bestand.write(str(dictionary[x][4][i]) + ',')
                            bestand.write(str(dictionary[x][5][i]) + '\n')

    bestand.close()


main()
