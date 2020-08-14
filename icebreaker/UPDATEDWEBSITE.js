const firstNames = ["What's your favorite color?", "What's your favorite movie?", "What came first: the chicken or the egg?", "If you could travel anywhere would would you go?", "What is a secret skill that you have?", "If you had one day off, what would you do?"];

const secondNames = ["", "", "", "", "", ""];

const getRandomNumber = (max) => Math.floor(Math.random() * max);

const getRandomName = () => 
  `${firstNames[getRandomNumber(firstNames.length)]} ${secondNames[getRandomNumber(secondNames.length)]}`;

const setRandomName = () => {
  document.getElementById('random-name').innerText = getRandomName();
}

document.getElementById('generate')
  .addEventListener('click', setRandomName);

setRandomName();

