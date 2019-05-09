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
    return "<html>

<title> KIPPEEEEEN </title>
<head>
    <center>
        <font size=300> <b> RELEASE THE CHICKENS </b> </font>
    </center>

</head>


<style>
    body {
        background-image: url("https://i.gifer.com/7Yw.gif")
    }
</style>

<script>
    var USure = prompt("Durf je dit echt aan?");
    if (USure == "Ja"); {
        alert("RELEASE THE CHICKEEEENS");
    }
    else {
        var num = prompt("Geef een nummer: ");
        if (num < 5) {
            for (num < 5, num++) {
                alert("Pech gehad")
            }
        else
            {
                alert("Oke cool")
            }
        }
        alert("Pech dan");
    }
</script>"


if __name__ == '__main__':
    app.run()
