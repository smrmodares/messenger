
document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit vote" event
        document.querySelector('#send').onclick = () => {
                let message = document.getElementById('message-box')
                socket.emit('send message', {'message': message.value});
        };

        document.getElementsByName('delete').forEach(button => {
                button.onclick = delete_click;
        });


    });

    function delete_click(butt) {
        const id = this.id;
        // const li = document.querySelector(`${id.split(1)}`)
        // li.innerHTML = ''
        socket.emit('delete message', {'id': id.slice(1)});
    };



    socket.on('update message', data => {
        const li = document.getElementById(data.id)
        console.log(li);

        if (data.action == 'delete') {
          let ul = document.querySelector('#messages');
          ul.removeChild(li)
        }
        else if (data.action == 'edit') {
          li.innerHTML = data.newvalue
        }
    });



    // When a new vote is announced, add to the unordered list
    socket.on('new message', data => {
        // get the list of messages
        let ul = document.querySelector('#messages');

        // create a new item
        let li = document.createElement("li");

        let message_id = `${data.message_id}`
        // create edit and delete buttons
        let editButton = document.createElement("button");
        let deleteButton = document.createElement("button");

        editButton.setAttribute("id", `e${data.message_id}`);
        deleteButton.setAttribute("id", `d${data.message_id}`);
        editButton.setAttribute("name", 'edit');
        deleteButton.setAttribute("name", 'delete');

        editButton.appendChild(document.createTextNode('edit'));
        deleteButton.appendChild(document.createTextNode('delete'));
        deleteButton.onclick = delete_click;

        //append buttons to li
        li.appendChild(document.createTextNode(`${data.username}: ${data.message}`));
        li.appendChild(editButton);
        li.appendChild(deleteButton);

        //append li to ul
        li.setAttribute("id", message_id);
        ul.appendChild(li);
    });

    document.querySelector('#form').onsubmit = () => {


        return false;
    };


    // socket.on('delete message', () => {
    //
    //   document.getElementByName('delete').forEach(button => {
    //           button.onclick = () => {
    //               const id = this.id;
    //               console.log(id);
    //               // const li = document.querySelector(`${id.split(1)}`)
    //               // li.innerHTML = ''
    //               socket.emit('delete message', {'id': id});
    //           };
    //     });
    // });

    // var selectedValue = selectElement.value;
});

// function get_id() {
//   // Initialize new request
//   const request = new XMLHttpRequest();
//   request.open('POST', '/get_id');
//
//   // Callback function for when request completes
//   request.onload = () => {
//
//       // Extract JSON data from request
//       const data = JSON.parse(request.responseText);
//
//       // Update the result div
//       if (data.user_id) {
//           localStorage.setItem('user_id', data.user_id);
//
//       }
//   }
//
//   // Add data to send with request
//   const data = new FormData();
//
//   // Send request
//   request.send(data);
//
// }
