const seats = document.querySelectorAll('input[name="seat_id"]');
const bookBtn = document.getElementById('bookBtn');

seats.forEach(seat => {
    seat.addEventListener('change', () => {
        bookBtn.disabled = false;
    });
});
