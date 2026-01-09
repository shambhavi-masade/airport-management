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

        # ❗ SAFETY CHECK
        if not seat_id:
            conn.close()
            return redirect("/bookings")

        # generate booking code
        cursor.execute("SELECT COUNT(*) AS total FROM bookings")
        count = cursor.fetchone()["total"] + 1
        booking_code = f"BK-{1000 + count}"

        cursor.execute("""
            INSERT INTO bookings
            (booking_code, passenger_name, flight_id, seat_id, booking_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            booking_code,
            request.form["passenger_name"],
            request.form["flight_id"],
            seat_id,
            "Confirmed"
        ))

        # mark seat as booked
        cursor.execute(
            "UPDATE seats SET is_booked = TRUE WHERE id = %s",
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

    # ---------------- FETCH AVAILABLE SEATS ----------------
    flight_id = request.args.get("flight_id")
    seats = []

    if flight_id:
        cursor.execute("""
            SELECT id, seat_number
            FROM seats
            WHERE flight_id = %s AND is_booked = FALSE
        """, (flight_id,))
        seats = cursor.fetchall()

    # ---------------- FETCH BOOKINGS ----------------
    cursor.execute("""
        SELECT b.id, b.booking_code, b.passenger_name,
               f.flight_no, s.seat_number, b.booking_status
        FROM bookings b
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

# ---------------- CANCEL BOOKING ----------------
@bookings_bp.route("/delete_booking/<int:id>")
def delete_booking(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT seat_id FROM bookings WHERE id=%s", (id,))
    booking = cursor.fetchone()

    if booking:
        cursor.execute("DELETE FROM bookings WHERE id=%s", (id,))
        cursor.execute(
            "UPDATE seats SET is_booked = FALSE WHERE id = %s",
            (booking["seat_id"],)
        )

    conn.commit()
    conn.close()
    return redirect("/bookings")
