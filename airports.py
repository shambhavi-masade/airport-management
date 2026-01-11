from flask import Blueprint, render_template, request, redirect
from db import get_db_connection

airports_bp = Blueprint("airports", __name__)

# ---------------- VIEW + ADD AIRPORT ----------------
@airports_bp.route("/airports", methods=["GET", "POST"])
def airports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute("""
            INSERT INTO airports (code, name, city, country, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form["code"],
            request.form["name"],
            request.form["city"],
            request.form["country"],
            request.form["status"]
        ))
        conn.commit()
        conn.close()
        return redirect("/airports")

    cursor.execute("SELECT * FROM airports")
    airports = cursor.fetchall()
    conn.close()

    return render_template("airports.html", airports=airports)


# ---------------- EDIT AIRPORT ----------------
@airports_bp.route("/edit_airport/<int:id>", methods=["GET", "POST"])
def edit_airport(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute("""
            UPDATE airports SET
            code=%s, name=%s, city=%s, country=%s, status=%s
            WHERE id=%s
        """, (
            request.form["code"],
            request.form["name"],
            request.form["city"],
            request.form["country"],
            request.form["status"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/airports")

    cursor.execute("SELECT * FROM airports WHERE id=%s", (id,))
    airport = cursor.fetchone()
    conn.close()

    return render_template("edit_airport.html", airport=airport)


# ---------------- DELETE AIRPORT (SAFE) ----------------
@airports_bp.route("/delete_airport/<int:id>")
def delete_airport(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM flights
        WHERE departure_airport_id=%s OR arrival_airport_id=%s
    """, (id, id))

    if cursor.fetchone()[0] == 0:
        cursor.execute("DELETE FROM airports WHERE id=%s", (id,))
        conn.commit()

    conn.close()
    return redirect("/airports")
