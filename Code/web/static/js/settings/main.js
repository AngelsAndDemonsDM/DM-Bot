var socket = io.connect('http://' + document.domain + ':' + location.port);

// Функции загрузки данных
document.addEventListener("DOMContentLoaded", function() {
    checkTokenStatus();
    checkAutoStartStatus();
    checkAutoUpdateStatus();
    getVersionInfo();
});

// Работа с токеном
function saveTokenSettings(event) {
    event.preventDefault();

    var botToken = document.getElementById("token").value;
    socket.emit('settingSetUpToken', botToken);
}

socket.on('settingTokenStatusPopup', function(data) {
    if (data) {
        showPopup('success', 'Настройка токена сохранена');
    } else {
        showPopup('error', 'Введён неверный токен бота');
    }
});

function checkTokenStatus() {
    socket.emit('settingCheckToken');
}

socket.on('settingTokenStatusUpdate', function(data) {
    if (data) {
        document.getElementById("tokenStatus").textContent = "Токен существует";
    } else {
        document.getElementById("tokenStatus").textContent = "Токен не существует";
    }
});

// Работа с автозапуском
function saveAutoStartSetting() {
    var autoStart = document.getElementById("autoStart").checked;
    socket.emit('settingSetUpAutoStart', autoStart);
}

socket.on('settingAutoStartStatusPopup', function(data) {
    if (data) {
        showPopup('success', 'Настройка автозапуска сохранена');
    } else {
        showPopup('error', 'Ошибка сохранения настройки автозапуска');
    }
});

function checkAutoStartStatus() {
    socket.emit('settingCheckAutoStart');
}

socket.on('settingAutoStartStatusUpdate', function(data) {
    document.getElementById("autoStart").checked = data;
});

// Функция для запуска бота
function startBot() {
    socket.emit('settingsStartBot');
}

socket.on('settingsBotStartStatus', function(data) {
    if (data.status === 'success') {
        showPopup('success', 'Бот успешно запущен!');
    } else {
        showPopup('error', 'Ошибка при запуске бота: ' + data.message);
    }
});

// Функция для сохранения настройки автоматического обновления
function saveAutoUpdateSetting() {
    var autoUpdate = document.getElementById("autoUpdateVersion").checked;
    socket.emit('settingSetUpAutoUpdate', autoUpdate);
}

// Обработка события для отображения сообщения о сохранении настройки
socket.on('settingAutoUpdateStatusPopup', function(data) {
    if (data) {
        showPopup('success', 'Настройка автоматического обновления сохранена');
    } else {
        showPopup('error', 'Ошибка сохранения настройки автоматического обновления');
    }
});

// Функция для проверки состояния автоматического обновления
function checkAutoUpdateStatus() {
    socket.emit('settingCheckAutoUpdate');
}

// Обработка события для обновления состояния чекбокса
socket.on('settingAutoUpdateStatusUpdate', function(data) {
    document.getElementById("autoUpdateVersion").checked = data;
});

// Функция для получения текущей и последней версии приложения
function getVersionInfo() {
    socket.emit('getVersionInfo');
}

// Обработка события для обновления информации о версиях
socket.on('versionInfo', function(data) {
    document.getElementById("appCurentVersion").textContent = data.currentVersion;
    document.getElementById("appLatestVersion").textContent = data.latestVersion;
});
