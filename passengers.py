from flask import Blueprint, render_template
from db import get_db_connection

passengers_bp = Blueprint("passengers", __name__)

# ---------------- PASSENGER LIST ----------------
@passengers_bp.route("/passengers")
def passengers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
       SELECT 
            p.id,
            p.name AS passenger_name,
            p.email,
            p.phone,
            COUNT(b.id) AS total_bookings
        FROM passengers p
        LEFT JOIN bookings b ON b.passenger_id = p.id
        GROUP BY p.id, p.name, p.email, p.phone
        ORDER BY p.name
    """)
    passengers = cursor.fetchall()

    conn.close()
    return render_template("passengers.html", passengers=passengers)


# ---------------- PASSENGER DETAILS ----------------
@passengers_bp.route("/passenger/<int:passenger_id>")
def passenger_details(passenger_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # passenger profile
    cursor.execute("""
        SELECT name, email, phone, gender, age
        FROM passengers
        WHERE id = %s
    """, (passenger_id,))
    passenger = cursor.fetchone()

    # travel history
    cursor.execute("""
        SELECT b.booking_code,
               f.flight_no,
               s.seat_number,
               b.booking_status
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        JOIN seats s ON b.seat_id = s.id
        WHERE b.passenger_id = %s
    """, (passenger_id,))
    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "passenger_details.html",
        passenger=passenger,
        bookings=bookings
    )
from flask import request, redirect

@passengers_bp.route("/edit_passenger/<int:id>", methods=["GET", "POST"])
def edit_passenger(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute("""
            UPDATE passengers SET
            name = %s,
            email = %s,
            phone = %s,
            gender = %s,
            age = %s
            WHERE id = %s
        """, (
             request.form.get("name"),
             request.form.get("email"),
             request.form.get("phone"),
             request.form.get("gender"),
             request.form.get("age"),
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/passengers")

    cursor.execute("SELECT * FROM passengers WHERE id=%s", (id,))
    passenger = cursor.fetchone()
    conn.close()

    return render_template("edit_passenger.html", passenger=passenger)
