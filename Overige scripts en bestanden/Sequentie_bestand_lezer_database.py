# Naam: Robert Rijksen
# Functie: Het netjes schrijven van alle sequenties met daarbij de behorende
# sequenties ID in een csv bestand waarna dit bestand gebruikt kon worden
# om alles tegelijk te inserten in mysql


def main():
    bestandsnaam = 'sequenties_100B.xlsx.txt'
    # Dit is het excel bestand waarbij alle 100 sequenties (met read 1 en 2)
    # naast elkaar stonden
    bestandslezer(bestandsnaam)


def bestandslezer(bestandsnaam):
    """
    :param bestandsnaam: Het bestand waarin alle 100 sequenties stonden
    Dit werd netjes in een bestand gezet waardoor dit gelijk in de tabel
    Onderzoeks_sequenties gezet kon worden
    """
    bestand = open(bestandsnaam)
    count = 0
    read = 0
    nieuw_bestand = open('project_sequenties.csv', 'a+')
    for line in bestand:
        lines = line.split('\t')
        count += 1
        read += 1
        nieuw_bestand.write(str(count) + ',')
        nieuw_bestand.write('\'' + lines[1] + '\'' + ',')
        nieuw_bestand.write('\'' + lines[0] + '\'' + ',' + str(read))
        read += 1
        nieuw_bestand.write('\n')
        count += 1
        nieuw_bestand.write(str(count) + ',')
        nieuw_bestand.write('\'' + lines[4] + '\'' + ',')
        nieuw_bestand.write('\'' + lines[3] + '\'' + ',' + str(read))
        nieuw_bestand.write('\n')
        read = 0

    nieuw_bestand.close()

    # return headers, sequenties


main()
