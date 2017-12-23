function classToggle() {
  var contents = document.querySelectorAll('td.contents');

  for (var i = contents.length - 1; i >= 0; i--) {
    contents[i].classList.toggle('censor');
  }
}

function onLoad() {
  document.querySelector('#censorCheckBox').addEventListener('click', classToggle);
}