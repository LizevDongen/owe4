# Functie: Bestandlezen van sequenties (excel bestand waar sequenties per 100
# verdeeld waren)


def main():
    bestandsnaam = 'sequenties_100.txt'
    bestandslezer(bestandsnaam)


def bestandslezer(bestandsnaam):
    """
    :param bestandsnaam: Dit is het excelbestand waarin de 100 sequenties
    stonden
    :return: een lijst met alle headers en een lijst met alle sequenties
    """
    bestand = open(bestandsnaam)
    headers = []
    sequenties = []
    for line in bestand:
        lines = line.split('\t')
        headers.append(lines[0])
        sequenties.append(lines[1])
        headers.append(lines[3])
        sequenties.append(lines[4])

    return headers, sequenties


main()