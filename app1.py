from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def calculator():

    answer = None

    if request.method == "POST":

        a = float(request.form["a"])
        b = float(request.form["b"])
        operator = request.form["operator"]

        if operator == "+":
            answer = a + b

        elif operator == "-":
            answer = a - b

        elif operator == "*":
            answer = a * b

        elif operator == "%":
            answer = a % b

    return render_template("index1.html", answer=answer)


if __name__ == "__main__":
    app.run(debug=True)