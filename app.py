from flask import Flask, render_template, request
from model import find_schemes, get_scheme_by_id

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    schemes = []
    form_data = {}

    if request.method == "POST":
        language   = request.form.get("language", "English")
        age        = request.form.get("age", "")
        occupation = request.form.get("occupation", "")
        gender     = request.form.get("gender", "")
        state      = request.form.get("state", "")
        query      = request.form.get("query", "")

        form_data = {
            "language":   language,
            "age":        age,
            "occupation": occupation,
            "gender":     gender,
            "state":      state,
            "query":      query,
        }

        schemes = find_schemes(
            query=query,
            language=language,
            age=age,
            occupation=occupation,
            gender=gender,
            state=state,
        )

    return render_template("index.html", schemes=schemes, form_data=form_data)


@app.route("/scheme/<int:scheme_id>")
def scheme_detail(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if scheme is None:
        return "Scheme not found", 404
    return render_template("scheme_detail.html", scheme=scheme)


if __name__ == "__main__":
    app.run(debug=False)