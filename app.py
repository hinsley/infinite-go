from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/play", methods=["GET"])
def play():
    return render_template("play.html")
