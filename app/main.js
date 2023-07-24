let roomCount = 0;

function addRoom() {
    const roomsDiv = document.getElementById('rooms');
    const newRoomDiv = document.createElement('div');
    newRoomDiv.id = `room${roomCount}`;
    
    const roomNameInput = document.createElement('input');
    roomNameInput.type = 'text';
    roomNameInput.name = `room-name`;
    roomNameInput.placeholder = `Room ${roomCount + 1} Name`;
    roomNameInput.required = true;
    
    const roomFileInput = document.createElement('input');
    roomFileInput.type = 'file';
    roomFileInput.name = `room-file`;
    roomFileInput.required = true;
    
    newRoomDiv.appendChild(roomNameInput);
    newRoomDiv.appendChild(roomFileInput);
    roomsDiv.appendChild(newRoomDiv);
    roomCount++;
}
