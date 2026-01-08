from flask import Blueprint, render_template, request, redirect
from db import get_db_connection

flights_bp = Blueprint("flights", __name__)

# ------------------ VIEW + ADD FLIGHTS ------------------
@flights_bp.route("/flights", methods=["GET", "POST"])
def flights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute("""
            INSERT INTO flights
            (flight_no, departure, destination, departure_time, arrival_time, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["flight_no"],
            request.form["departure"],
            request.form["destination"],
            request.form["departure_time"],
            request.form["arrival_time"],
            request.form["status"]
        ))
        conn.commit()
        conn.close()
        return redirect("/flights")

    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    conn.close()

    return render_template("flights.html", flights=flights)

# ------------------ DELETE FLIGHT ------------------
@flights_bp.route("/delete_flight/<int:id>")
def delete_flight(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM flights WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/flights")

# ------------------ EDIT FLIGHT ------------------
@flights_bp.route("/edit_flight/<int:id>", methods=["GET", "POST"])
def edit_flight(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute("""
            UPDATE flights SET
            flight_no=%s,
            departure=%s,
            destination=%s,
            departure_time=%s,
            arrival_time=%s,
            status=%s
            WHERE id=%s
        """, (
            request.form["flight_no"],
            request.form["departure"],
            request.form["destination"],
            request.form["departure_time"],
            request.form["arrival_time"],
            request.form["status"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/flights")

    cursor.execute("SELECT * FROM flights WHERE id=%s", (id,))
    flight = cursor.fetchone()
    conn.close()

    return render_template("edit_flights.html", flight=flight)
