from flask import Blueprint, render_template, request, redirect
from db import get_db_connection

bookings_bp = Blueprint("bookings", __name__)

@bookings_bp.route("/bookings", methods=["GET", "POST"])
def manage_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ---------------- CREATE BOOKING ----------------
    if request.method == "POST":
        seat_id = request.form.get("seat_id")

        if not seat_id:
            conn.close()
            return redirect("/bookings")

        # -------- FIND OR CREATE PASSENGER --------
        cursor.execute(
            "SELECT id FROM passengers WHERE email=%s",
            (request.form.get("email"),)
        )
        passenger = cursor.fetchone()

        if passenger:
            passenger_id = passenger["id"]
        else:
            cursor.execute("""
                INSERT INTO passengers (name, email, phone, gender, age)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                request.form.get("passenger_name"),
                request.form.get("email"),
                request.form.get("phone"),
                request.form.get("gender"),
                request.form.get("age")
            ))
            passenger_id = cursor.lastrowid

        # -------- GENERATE BOOKING CODE --------
        cursor.execute("SELECT COUNT(*) AS total FROM bookings")
        count = cursor.fetchone()["total"] + 1
        booking_code = f"BK-{1000 + count}"

        # -------- CREATE BOOKING --------
        cursor.execute("""
            INSERT INTO bookings
            (booking_code, passenger_id, flight_id, seat_id, booking_status)
            VALUES (%s, %s, %s, %s, 'Confirmed')
        """, (
            booking_code,
            passenger_id,
            request.form["flight_id"],
            seat_id
        ))

        # -------- MARK SEAT BOOKED --------
        cursor.execute(
            "UPDATE seats SET is_booked = TRUE WHERE id=%s",
            (seat_id,)
        )

        conn.commit()
        conn.close()
        return redirect("/bookings")

    # ---------------- FETCH FLIGHTS ----------------
    cursor.execute("""
        SELECT id, flight_no
        FROM flights
        WHERE status IN ('On Time', 'Delayed')
    """)
    flights = cursor.fetchall()

    # ---------------- FETCH SEATS ----------------
    flight_id = request.args.get("flight_id")
    seats = []

    if flight_id:
        cursor.execute("""
            SELECT id, seat_number, is_booked
            FROM seats
            WHERE flight_id = %s
        """, (flight_id,))
        seats = cursor.fetchall()

    # ---------------- FETCH BOOKINGS ----------------
    cursor.execute("""
        SELECT 
            b.id, b.booking_code,
            p.name AS passenger_name,
            f.flight_no,
            s.seat_number,
            b.booking_status
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.id
        JOIN flights f ON b.flight_id = f.id
        JOIN seats s ON b.seat_id = s.id
    """)
    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "bookings.html",
        flights=flights,
        seats=seats,
        bookings=bookings
    )


@bookings_bp.route("/delete_booking/<int:id>")
def delete_booking(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT seat_id FROM bookings WHERE id=%s", (id,))
    booking = cursor.fetchone()

    if booking:
        cursor.execute("DELETE FROM bookings WHERE id=%s", (id,))
        cursor.execute(
            "UPDATE seats SET is_booked = FALSE WHERE id=%s",
            (booking["seat_id"],)
        )

    conn.commit()
    conn.close()
    return redirect("/bookings")
