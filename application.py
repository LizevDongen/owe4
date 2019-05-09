"""
Basis voor een te ontwikkelen Flask applicatie
Creation: may 9, 2019
(c) HAN University of Applied Science
Author: Martijn van der Bruggen

Voor deployment op Azure WebApps is het noodzakelijk het bestand
de naam application.py te geven.
"""
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def index_fun():
    return 'Dit is de routing naar de root! Aanpassing!'


if __name__ == '__main__':
    app.run()
