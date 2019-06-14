# Naam: Robert Rijksen
# Functie: Bestandlezen van sequenties (met dat bestand van onderwijsonline)


def main():
    bestandsnaam = '-at-HWI-M02942_file1.txt'
    bestandslezer(bestandsnaam)


def bestandslezer(bestandsnaam):
    """
    :param bestandsnaam: Dit is het bestand waarin alle sequenties stonden
    + alle scores etc.
    :return: een lijst met alle headers en een lijst met alle sequenties
    """
    bestand = open(bestandsnaam)
    headers = []
    sequenties = []
    teller = 0
    for line in bestand:
        teller += 1
        if teller == 1:
            headers.append(line.replace('\n', ''))
        elif teller == 2:
            sequenties.append(line.replace('\n', ''))
        elif teller == 4:
            teller = 0

    return headers, sequenties


main()