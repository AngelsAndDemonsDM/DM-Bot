var socket = io.connect('http://' + document.domain + ':' + location.port);

// Отправка запроса на получение списка игроков
socket.emit('getAllPlayers');

// Обработка ответа и отображение списка игроков
socket.on('allPlayers', function(players) {
    const playerButtons = document.getElementById('playerButtons');
    playerButtons.innerHTML = ''; // Очищаем кнопки

    players.forEach(function(player) {
        const button = document.createElement('button');
        button.textContent = player.name;
        button.setAttribute('data-id', player.id);
        button.classList.add('player-button'); // Добавляем класс для стилизации

        // Добавляем обработчик клика для каждой кнопки
        button.addEventListener('click', function() {
            showPlayerInfo(player);
        });

        playerButtons.appendChild(button);
    });
});

// Функция для отображения информации о выбранном игроке
function showPlayerInfo(player) {
    const playerInfoDiv = document.getElementById('playerInfo');
    let playerBaseData = '';

    // Базовая информация об игроке
    playerBaseData = `
    <table>
    <tr><th>Discord параметры</th><th>Значение</th></tr>
    <tr><td>Discord name</td><td>${player.name}</td></tr>
    <tr><td>Discord ID</td><td>${player.id}</td></tr>
    </table>
    `
    
    // Формируем HTML код информации об игроке
    playerInfoDiv.innerHTML = `
    ${playerBaseData}
    `;
}

// Поиск игроков по ID или имени
document.getElementById('searchInput').addEventListener('input', function() {
    const searchText = this.value.toLowerCase();

    const playerButtons = document.getElementById('playerButtons');
    const buttons = playerButtons.getElementsByTagName('button');

    Array.from(buttons).forEach(function(button) {
        const text = button.textContent.toLowerCase();
        const id = button.getAttribute('data-id').toLowerCase();

        if (text.includes(searchText) || id.includes(searchText)) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });
});
