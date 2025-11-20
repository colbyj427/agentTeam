let currentPlayer = 'X';
const cells = document.querySelectorAll('.cell');

function makeMove(index) {
    if (cells[index].textContent === '') {
        cells[index].textContent = currentPlayer;
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    }
}

cells.forEach((cell, index) => {
    cell.addEventListener('click', () => makeMove(index));
});