from flask import Flask, render_template, request
from model import find_schemes

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    schemes = []

    if request.method == "POST":
        query = request.form["query"]
        schemes = find_schemes(query)

    return render_template("index.html", schemes=schemes)


if __name__ == "__main__":
    app.run(debug=False)