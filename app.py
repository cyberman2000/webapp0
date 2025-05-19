from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    user_id = request.args.get("user_id", default=953532644, type=int)
    return render_template("index.html", user_id=user_id)

@app.route("/spin", methods=["POST"])
def spin():
    data = request.json
    user_id = data["user_id"]
    prize = data["prize"]

    return jsonify({
        "redirect_url": f"https://t.me/Ton_Rewarde_Bot?start=/prize+ {user_id}+{prize}"
    })

if __name__ == "__main__":
    app.run(debug=True)