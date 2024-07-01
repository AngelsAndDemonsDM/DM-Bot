var socket = io();
var popups = [];

socket.on('popup_notification', function(data) {
    var popup = document.createElement('div');
    popup.className = 'popup ' + data.type;
    popup.innerHTML = '<span>' + data.message + '</span>';
    popup.onclick = function() { closePopup(popup); };
    document.body.appendChild(popup);
    popups.push(popup);
    adjustPopupPositions();
    setTimeout(function() { closePopup(popup); }, 5000); // Закрыть через 5 секунд
});

function showPopup(type, message) {
    socket.emit('show_popup', {'type': type, 'message': message});
}

function closePopup(element) {
    element.style.display = 'none';
    popups = popups.filter(popup => popup !== element);
    element.remove();
    adjustPopupPositions();
}

function adjustPopupPositions() {
    var topOffset = 20;
    popups.forEach(function(popup) {
        popup.style.top = topOffset + 'px';
        topOffset += popup.offsetHeight + 10;
    });
}

window.showPopup = showPopup;
