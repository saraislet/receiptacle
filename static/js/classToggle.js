function classToggle() {
  var contents = document.querySelectorAll('td.contents');
  // contents[0].classList.toggle('censor');
  // for (content in contents) {
  //   content.classList.toggle('censor');
  // }

  for (var i = contents.length - 1; i >= 0; i--) {
    contents[i].classList.toggle('censor');
  }
}

function onLoad() {
  document.querySelector('#censorCheckBox').addEventListener('click', classToggle);
}