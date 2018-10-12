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
      .split(' ');
    str1 = type[0];
    str2 = type[1];
    if (str1.length > str2.length) {
      type = classObj[str1];
    } else {
      type = classObj[str2];
    }

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

  $('#dm-form').on('submit', function(evt) {
    evt.preventDefault();
    let text = $('#dm-input').val();
    if (text.length > 1) {
      let threadArr = document.URL.split('/');
      let threadId = parseInt(threadArr[threadArr.length - 1]);
      $('#dm-form').trigger('reset');
      addDM(text, threadId, function(resp) {
        generateDMs(resp);
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

function addDM(text, threadId, cb) {
  $.ajax({
    method: 'POST',
    url: `${BASE_URL}/threads/${threadId}/dm/add`,
    contentType: 'application/json',
    data: JSON.stringify({ text }),
    success: response => {
      cb(response);
    }
  });
}

function generateDMs(dmsArr, cb) {
  $('.dm-list').empty();
  for (let i = 0; i < dmsArr.length; i++) {
    $('.dm-list').append($(`<div class="dm row">${dmsArr[i]}</div><br>`));
  }
}
