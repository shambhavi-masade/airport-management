from flask import Blueprint, render_template, request, redirect
from db import get_db_connection

flights_bp = Blueprint("flights", __name__)

# ------------------ VIEW + ADD FLIGHTS ------------------
@flights_bp.route("/flights", methods=["GET", "POST"])
def flights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # -------- ADD FLIGHT --------
    if request.method == "POST":
        cursor.execute("""
            INSERT INTO flights
            (flight_no, departure_airport_id, arrival_airport_id,
             departure_time, arrival_time, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["flight_no"],
            request.form["departure_airport_id"],
            request.form["arrival_airport_id"],
            request.form["departure_time"],
            request.form["arrival_time"],
            request.form["status"]
        ))

        # 🔥 GET NEW FLIGHT ID
        flight_id = cursor.lastrowid

        # 🔥 AUTO-GENERATE SEATS (DYNAMIC)
        rows = ["A", "B", "C", "D", "E"]   # 5 rows
        seats_per_row = 6                 # A1–A6 etc.

        for row in rows:
            for num in range(1, seats_per_row + 1):
                seat_no = f"{row}{num}"
                cursor.execute("""
                    INSERT INTO seats (flight_id, seat_number, is_booked)
                    VALUES (%s, %s, FALSE)
                """, (flight_id, seat_no))

        conn.commit()
        conn.close()
        return redirect("/flights")

    # -------- FETCH FLIGHTS (SHOW CITIES) --------
    cursor.execute("""
        SELECT 
            f.id,
            f.flight_no,
            dep.city AS departure_city,
            arr.city AS destination_city,
            f.departure_time,
            f.arrival_time,
            f.status
        FROM flights f
        JOIN airports dep ON f.departure_airport_id = dep.id
        JOIN airports arr ON f.arrival_airport_id = arr.id
    """)
    flights = cursor.fetchall()

    # -------- FETCH ACTIVE AIRPORTS --------
    cursor.execute("""
        SELECT id, code, city
        FROM airports
        WHERE status = 'Active'
    """)
    airports = cursor.fetchall()

    conn.close()

    return render_template(
        "flights.html",
        flights=flights,
        airports=airports
    )


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
            departure_airport_id=%s,
            arrival_airport_id=%s,
            departure_time=%s,
            arrival_time=%s,
            status=%s
            WHERE id=%s
        """, (
            request.form["flight_no"],
            request.form["departure_airport_id"],
            request.form["arrival_airport_id"],
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

    cursor.execute("SELECT id, code, city FROM airports WHERE status='Active'")
    airports = cursor.fetchall()

    conn.close()

    return render_template(
        "edit_flights.html",
        flight=flight,
        airports=airports
    )
