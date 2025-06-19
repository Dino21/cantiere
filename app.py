import csv
from flask import Flask, render_template, request, redirect, Response
from database import get_lavoratore, aggiorna_lavoratore, aggiungi_lavoratore, lista_lavoratori, elimina_lavoratore
from database import get_cantiere, aggiorna_cantiere, aggiungi_cantiere, lista_cantieri, elimina_cantiere
from database import aggiungi_presenza, report_dettagliato_cantiere, report_dettagliato_lavoratore
from database import lista_presenze, elimina_presenza, get_presenza, aggiorna_presenza
RUOLI = ["Muratore","Elettricista","Idraulico","Lattoniere","Altro"]
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/lavoratori", methods=["GET", "POST"])
def idlavoratori():
    if request.method == "POST":
        nome = request.form.get("nome")
        ruolo = request.form.get("ruolo")
        if nome and ruolo:
            aggiungi_lavoratore(nome,ruolo)
        return redirect("/lavoratori")
    lavoratori = lista_lavoratori()
    return render_template("lavoratori.html", lavoratori=lavoratori, ruoli=RUOLI)

@app.route("/cantieri", methods=["GET", "POST"])
def idcantieri():
    if request.method == "POST":
        nome = request.form.get("nome")
        paese = request.form.get("paese")
        indirizzo = request.form.get("indirizzo")
        if nome and paese and indirizzo:
            aggiungi_cantiere(nome, paese, indirizzo)
        return redirect("/cantieri")
    cantieri = lista_cantieri()
    return render_template("cantieri.html", cantieri=cantieri)

@app.route("/lavoratori/elimina/<int:id_lavoratore>")
def elimina(id_lavoratore):
    elimina_lavoratore(id_lavoratore)
    return redirect("/lavoratori")

@app.route("/cantieri/elimina/<int:id_cantiere>")
def eliminaCantiere(id_cantiere):
    elimina_cantiere(id_cantiere)
    return redirect("/cantieri")

@app.route("/lavoratori/modifica/<int:id_lavoratore>", methods=["GET", "POST"])
def modifica(id_lavoratore):
    lavoratore = get_lavoratore(id_lavoratore)
    if not lavoratore:
        return "Lavoratore non trovato", 404
    if request.method == "POST":
        nome = request.form.get("nome")
        ruolo = request.form.get("ruolo")
        aggiorna_lavoratore(id_lavoratore, nome, ruolo)
        return redirect("/lavoratori")
    return render_template("modifica_lavoratore.html", lavoratore=lavoratore, ruoli=RUOLI)

@app.route("/cantieri/modifica/<int:id_cantiere>", methods=["GET", "POST"])
def modificaCantiere(id_cantiere):
    cantiere = get_cantiere(id_cantiere)
    if not cantiere:
        return "Cantiere non trovato", 404
    if request.method == "POST":
        nome = request.form.get("nome")
        paese = request.form.get("paese")
        indirizzo = request.form.get("indirizzo")
        aggiorna_cantiere(id_cantiere, nome, paese, indirizzo)
        return redirect("/cantieri")
    return render_template("modifica_cantiere.html", cantiere=cantiere)

@app.route("/presenze", methods=["GET", "POST"])
def presenze():
    if request.method == "POST":
        data = request.form.get("data")
        lavoratore_id = request.form.get("lavoratore_id")
        cantiere_id = request.form.get("cantiere_id")
        ore = request.form.get("ore")
        descrizione = request.form.get("descrizione")

        if data and lavoratore_id and cantiere_id and ore:
            aggiungi_presenza(data, lavoratore_id, cantiere_id, ore, descrizione)
        return redirect("/presenze")

    lavoratori = lista_lavoratori()
    cantieri = lista_cantieri()
    presenze = lista_presenze()

    return render_template("presenze.html", lavoratori=lavoratori, cantieri=cantieri, presenze=presenze)

@app.route("/report/lavoratore", methods=["GET", "POST"])
def report_lavoratore():
    lavoratori = lista_lavoratori()
    totale = 0
    dettaglio = []
    if request.method == "POST":
        lavoratore_id = request.form.get("lavoratore_id")
        data_inizio = request.form.get("data_inizio")
        data_fine = request.form.get("data_fine")
        if lavoratore_id and data_inizio and data_fine:
            totale, dettaglio = report_dettagliato_lavoratore(lavoratore_id, data_inizio, data_fine)
    return render_template("report_lavoratore.html", lavoratori=lavoratori, totale=totale, dettaglio=dettaglio)

@app.route("/report/cantiere", methods=["GET", "POST"])
def report_cantiere():
    cantieri = lista_cantieri()
    totale = 0
    dettaglio = []
    nome_cantiere = ""
    if request.method == "POST":
        cantiere_id = request.form.get("cantiere_id")
        data_inizio = request.form.get("data_inizio")
        data_fine = request.form.get("data_fine")
        if cantiere_id and data_inizio and data_fine:
            totale, dettaglio = report_dettagliato_cantiere(cantiere_id, data_inizio, data_fine)
            for c in cantieri:
                if c[0]==int(cantiere_id):
                    nome_cantiere=c[1]
                    break
    return render_template("report_cantiere.html", cantieri=cantieri, totale=totale, dettaglio=dettaglio, nome_cantiere=nome_cantiere)

@app.route("/report/lavoratore/export", methods=["POST"])
def export_report_lavoratore():
    lavoratore_id = request.form.get("lavoratore_id")
    data_inizio = request.form.get("data_inizio")
    data_fine = request.form.get("data_fine")
    nome_cantiere = ""
    if not (lavoratore_id and data_inizio and data_fine):
        return "Parametri mancanti", 400
    totale, dettaglio = report_dettagliato_lavoratore(lavoratore_id, data_inizio, data_fine)
    def generate():
        yield "Cantiere;Ore\n"
        for cantiere, ore in dettaglio:
            yield f"{cantiere};{ore}\n"
        yield f"\nTotale Ore;{totale}\n"
    filename = f"report_lavoratore_{lavoratore_id}_{data_inizio}_to_{data_fine}.csv"
    return Response(generate(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

@app.route("/report/cantiere/export", methods=["POST"])
def export_report_cantiere():
    cantiere_id = request.form.get("cantiere_id")
    data_inizio = request.form.get("data_inizio")
    data_fine = request.form.get("data_fine")
    if not (cantiere_id and data_inizio and data_fine):
        return "Parametri mancanti", 400
    totale, dettaglio = report_dettagliato_cantiere(cantiere_id, data_inizio, data_fine)
    cantieri = lista_cantieri()
    nome_cantiere = ""
    paese_cantiere = ""
    indirizzo_cantiere = ""
    for c in cantieri:
        if c[0] == int(cantiere_id):
            nome_cantiere=c[1]
            paese_cantiere=c[2]
            indirizzo_cantiere=c[3]
            break
    def generate():
        yield f"Cantiere:{nome_cantiere}\n"
        yield f"Città:{paese_cantiere}\n"
        yield f"Indirizzo:{indirizzo_cantiere}\n"
        yield "\nLavoratore;Ruolo;Ore\n"
        for lavoratore, ruolo, ore in dettaglio:
            yield f"{lavoratore};{ruolo};{ore}\n"
        yield f"\n;Totale Ore;{totale}\n"
    filename = f"report_cantiere_{nome_cantiere}_{data_inizio}_to_{data_fine}.csv"
    return Response(generate(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

@app.route("/presenze/elimina/<int:id_presenza>")
def elimina_presenza_route(id_presenza):
    elimina_presenza(id_presenza)
    return redirect("/presenze")

@app.route("/presenze/modifica/<int:id_presenza>", methods=["GET", "POST"])
def modifica_presenza(id_presenza):
    presenza = get_presenza(id_presenza)
    if not presenza:
        return "Presenza non trovata", 404
    if request.method == "POST":
        data = request.form.get("data")
        lavoratore_id = request.form.get("lavoratore_id")
        cantiere_id = request.form.get("cantiere_id")
        ore = request.form.get("ore")
        descrizione = request.form.get("descrizione")
        aggiorna_presenza(id_presenza, data, lavoratore_id, cantiere_id, ore, descrizione)
        return redirect("/presenze")
    lavoratori = lista_lavoratori()
    cantieri = lista_cantieri()
    return render_template("modifica_presenza.html", presenza=presenza, lavoratori=lavoratori, cantieri=cantieri)

if __name__ == "__main__":
    app.run(debug=True)
