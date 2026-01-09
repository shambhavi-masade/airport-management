from flask import Flask, render_template
from flights import flights_bp
from bookings import bookings_bp

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

app.register_blueprint(flights_bp)
app.register_blueprint(bookings_bp)

if __name__ == "__main__":
    app.run(debug=True)