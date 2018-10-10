<<<<<<< HEAD
const BASE_URL = 'http://localhost:5000';

$(document).ready(function() {
  $('.far, .fas').on('click', function(evt) {
    let classObj = {
      'fa-smile': 'smile',
      'fa-sad-cry': 'sad',
      'fa-laugh-squint': 'laugh',
      'fa-angry': 'angry'
    };
    let type = $(evt.target)
      .attr('class')
      .split(' ')[1];
    type = classObj[type];
    let msgId = $(evt.target)
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .attr('id');
    $(evt.target).toggleClass('far fas');
    if ($(evt.target).hasClass('fas')) {
      addReaction(type, msgId, function(resp) {
        console.log(resp);
      });
    } else {
      deleteReaction(type, msgId, function(resp) {
        console.log(resp);
      });
    }
  });
});

// function getUserId(cb) {
//   $.ajax({
//     method: 'GET',
//     url: `${BASE_URL}/getcurrentuser`,
//     contentType: 'application/json',
//     success: response => {
//       userId = response.user;
//       return cb(userId);
//     }
//   });
// }

function addReaction(type, msgId, cb) {
  $.ajax({
    method: 'POST',
    url: `${BASE_URL}/addreaction`,
    contentType: 'application/json',
    data: JSON.stringify({ type, msgId }),
    success: response => {
      cb(response);
    }
  });
}

function deleteReaction(type, msgId, cb) {
  $.ajax({
    method: 'DELETE',
    url: `${BASE_URL}/deletereaction`,
    contentType: 'application/json',
    data: JSON.stringify({ type, msgId }),
    success: response => {
      cb(response);
    }
  });
}
=======
// $(document).ready(function() {
//   console.log('page loaded');
//   $('.reactions').on('mouseover', function(evt) {
//     console.log('hovered');
//     $(evt.target).attr('style', 'font-size: 40px');
//   });
// });
>>>>>>> edfb58e0e2ff6e28e4623a9e8297122a1d4398de
