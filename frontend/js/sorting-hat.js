const sortingHatQuestions = [
  {
    question: "布莱克家族（The House of Black）世代属于哪个学院？",
    correctAnswer: "Slytherin",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Hmm... quite right! You have a keen understanding of the old families. The Blacks have indeed graced Slytherin for generations... though there was one notable exception, wasn't there?",
    wrongResponses: {
      Gryffindor: "Ah, I see your confusion! While one famous Black did break the tradition, the family's legacy lies elsewhere. A noble guess, though!",
      Ravenclaw: "Hmm... an interesting thought, but the Blacks value ambition over wit. Do not be discouraged - wisdom comes in many forms!",
      Hufflepuff: "Oh dear, no. The Blacks would hardly appreciate such... humble surroundings. But there is no shame in loyalty and hard work!",
      Azkaban: "My, my! While some Blacks certainly earned a place there, Azkaban is not a Hogwarts house! Though your... creative thinking is noted!"
    }
  },
  {
    question: "卢娜·洛夫古德（Luna Lovegood）在哪个学院？",
    correctAnswer: "Ravenclaw",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Excellent! You see beyond the ordinary, just like dear Luna herself. Wit beyond measure is man's greatest treasure, indeed!",
    wrongResponses: {
      Gryffindor: "A brave guess, but Luna's strength lies not in sword and shield, but in her unique perspective. Curious minds belong elsewhere...",
      Slytherin: "Oh no, no. Luna lacks the... conventional ambition of Slytherin. But her unconventional wisdom is a treasure in its own right!",
      Hufflepuff: "While Luna is certainly loyal and kind, her true home celebrates wit and wisdom. A thoughtful guess, nonetheless!",
      Azkaban: "Heavens no! Luna may be... eccentric, but she is no criminal! Though I admire your imagination - Ravenclaws do appreciate creativity!"
    }
  },
  {
    question: "塞德里克·迪戈里（Cedric Diggory）来自哪个学院？",
    correctAnswer: "Hufflepuff",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Indeed! You remember him well - a true Hufflepuff, loyal, hardworking, and just. His memory honors us all.",
    wrongResponses: {
      Gryffindor: "A natural assumption, given his bravery in the Triwizard Tournament. But Cedric's true strength was his fairness and dedication - Hufflepuff virtues!",
      Slytherin: "Oh, I think not. Cedric lacked the... cunning nature of Slytherin. His nobility shone through honest effort, not ambition!",
      Ravenclaw: "Cedric was clever, yes, but his heart belonged to Hufflepuff. He showed that hard work can match wit - remember that!",
      Azkaban: "What a terrible thought! Cedric was a model student - kind, fair, and true. Hufflepuff was his home, not that dreadful place!"
    }
  },
  {
    question: "韦斯莱家族（The Weasleys）世代属于哪个学院？",
    correctAnswer: "Gryffindor",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Precisely! The Weasleys are Gryffindor through and through - brave, daring, and fiercely loyal. Blood traitors, perhaps, but noble ones!",
    wrongResponses: {
      Slytherin: "Oh my, no! The Weasleys and Slytherin have been... at odds for quite some time. Pure-blood pride is not their way!",
      Ravenclaw: "While some Weasleys are certainly clever - Fred and George come to mind - their courage defines them more than their wit!",
      Hufflepuff: "A reasonable guess - the Weasleys are indeed hardworking and loyal. But their bravery and daring place them firmly in Gryffindor!",
      Azkaban: "Goodness! The Weasleys may bend rules, but they're hardly Azkaban material! Though Arthur's collection of plugs might raise eyebrows..."
    }
  },
  {
    question: "小天狼星布莱克（Sirius Black）是家族中唯一进入哪个学院的人？",
    correctAnswer: "Gryffindor",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Ah, you know your history well! Sirius broke the Black family tradition, choosing courage over cunning. A true Gryffindor to the very end!",
    wrongResponses: {
      Slytherin: "Oh, quite the opposite! Sirius was the Black who got away - the rebel who rejected his family's Slytherin legacy!",
      Ravenclaw: "An interesting theory, but Sirius's defining trait was his bravery, not his book-learning. He followed his heart, not his head!",
      Hufflepuff: "While Sirius was loyal to his friends, his nature was far too... rebellious for gentle Hufflepuff. He blazed with Gryffindor fire!",
      Azkaban: "Ha! Sirius did spend time there, but against his will! His heart always belonged to Gryffindor - and to his friends, the true Marauders!"
    }
  },
  {
    question: "哪个学院以智慧（Wit）和学习（Learning）著称？",
    correctAnswer: "Ravenclaw",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Correct! 'Wit beyond measure is man's greatest treasure.' Rowena Ravenclaw valued wisdom above all, and her house reflects that noble pursuit!",
    wrongResponses: {
      Gryffindor: "Close, but Gryffindor prizes bravery and chivalry, not scholarly pursuits. Though some Gryffindors are quite clever - Hermione, for instance!",
      Slytherin: "Slytherin values ambition and cunning - different from pure wisdom. Though a sharp mind serves their ambitions well!",
      Hufflepuff: "Hufflepuff values hard work and dedication. While not unintelligent, their strength lies in persistence, not pure wit!",
      Azkaban: "My dear student, Azkaban has no house values - only despair! But your... unconventional thinking shows a certain Ravenclaw creativity!"
    }
  },
  {
    question: "哪个学院以忠诚（Loyalty）和耐心（Patience）著称？",
    correctAnswer: "Hufflepuff",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Indeed! Helga Hufflepuff took 'the rest' and taught them all she knew. Her house values fair play, hard work, and true friendship!",
    wrongResponses: {
      Gryffindor: "Gryffindors are loyal, yes, but their defining trait is courage. Hufflepuff's loyalty runs deeper - steady and unwavering!",
      Slytherin: "Oh, Slytherin values loyalty to one's own, perhaps, but their focus is ambition and self-advancement. Hufflepuff's loyalty is more... inclusive!",
      Ravenclaw: "Ravenclaws pursue knowledge, which requires patience, yes. But their primary value is wisdom, not the steadfast loyalty of Hufflepuff!",
      Azkaban: "Loyalty in Azkaban? A rare thing indeed! But Hufflepuff's loyalty is a virtue, not a prison sentence. Do try again!"
    }
  },
  {
    question: "哪个学院以野心（Ambition）和精明（Cunning）著称？",
    correctAnswer: "Slytherin",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Precisely! Salazar Slytherin sought those with great ambition and pure-blood heritage. His house produces leaders - for better or worse!",
    wrongResponses: {
      Gryffindor: "Gryffindors can be ambitious, yes, but they achieve through bravery, not cunning. Slytherin's methods are... more subtle!",
      Ravenclaw: "Ravenclaws seek knowledge for its own sake. Slytherins seek it as a means to power - a crucial distinction!",
      Hufflepuff: "Oh dear, no. Hufflepuff values fair play and hard work. Slytherin's ambition and cunning would be quite... out of place there!",
      Azkaban: "Ambition can indeed lead one to Azkaban, if misdirected! But Slytherin is a house of greatness, not a prison. Use your ambition wisely!"
    }
  },
  {
    question: "哪个学院以勇气（Bravery）和骑士精神（Chivalry）著称？",
    correctAnswer: "Gryffindor",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Correct! Godric Gryffindor sought the brave at heart. His house has produced some of the finest witches and wizards - Dumbledore himself was one!",
    wrongResponses: {
      Slytherin: "Slytherins can be brave, certainly, but their courage serves their ambitions. Gryffindor's bravery is selfless - that's the difference!",
      Ravenclaw: "Ravenclaws may be brave in pursuing knowledge, but their defining trait is wisdom. Gryffindor's courage is more... immediate!",
      Hufflepuff: "Hufflepuffs show quiet courage in their steadfastness, but Gryffindor's bravery is bold and daring - quite different!",
      Azkaban: "Bravery in Azkaban? Only in surviving it! But Gryffindor courage is about standing up for what's right, not enduring what's wrong!"
    }
  },
  {
    question: "汤姆·里德尔（Tom Riddle）在哪个学院？",
    correctAnswer: "Slytherin",
    options: ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Azkaban"],
    correctResponse: "Indeed... the last heir of Salazar Slytherin himself. Tom Riddle's ambition and cunning led him down a dark path, but his house placement was inevitable.",
    wrongResponses: {
      Gryffindor: "Oh, quite impossible! Riddle's nature was the very opposite of Gryffindor - no chivalry, no selfless bravery. Only ambition and cruelty.",
      Ravenclaw: "Riddle was clever, yes, but his pursuit of knowledge was twisted by ambition. He sought power, not wisdom - Slytherin was his true home.",
      Hufflepuff: "No, no. Riddle lacked every Hufflepuff virtue - no loyalty, no fairness, no honest hard work. His path was one of cunning and ambition.",
      Azkaban: "A fitting destination for his later self, perhaps! But as a student, he walked Slytherin's halls, learning dark secrets... and creating them."
    }
  }
];

let currentQuestion = null;
let isHatActive = false;

function createSortingHatModal() {
  const modal = document.createElement('div');
  modal.className = 'sorting-hat-modal';
  modal.id = 'sortingHatModal';
  modal.innerHTML = `
    <div class="sorting-hat-content">
      <div class="sorting-hat-icon">🎩</div>
      <div class="sorting-hat-title">分院帽</div>
      <div class="sorting-hat-subtitle">The Sorting Hat</div>
      <div class="sorting-hat-divider"></div>
      <div class="sorting-hat-message" id="sortingHatMessage">
        "Hmm... 让我看看你有多了解霍格沃茨..."
      </div>
      <div class="sorting-hat-options" id="sortingHatOptions"></div>
      <div class="sorting-hat-buttons">
        <button class="sorting-hat-btn close-btn" id="closeSortingHat">关闭</button>
        <button class="sorting-hat-btn next-btn" id="nextQuestion" style="display: none;">再来一题</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  
  document.getElementById('closeSortingHat').addEventListener('click', closeSortingHat);
  document.getElementById('nextQuestion').addEventListener('click', showNextQuestion);
  
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeSortingHat();
    }
  });
  
  return modal;
}

function openSortingHat() {
  if (isHatActive) return;
  isHatActive = true;
  
  let modal = document.getElementById('sortingHatModal');
  if (!modal) {
    modal = createSortingHatModal();
  }
  
  modal.classList.add('show');
  showNextQuestion();
}

function closeSortingHat() {
  const modal = document.getElementById('sortingHatModal');
  if (modal) {
    modal.classList.remove('show');
    isHatActive = false;
  }
}

function showNextQuestion() {
  const messageEl = document.getElementById('sortingHatMessage');
  const optionsEl = document.getElementById('sortingHatOptions');
  const nextBtn = document.getElementById('nextQuestion');
  
  nextBtn.style.display = 'none';
  optionsEl.innerHTML = '';
  
  currentQuestion = sortingHatQuestions[Math.floor(Math.random() * sortingHatQuestions.length)];
  
  typeWriterEffect(messageEl, `"${currentQuestion.question}"`, 30);
  
  setTimeout(() => {
    showOptions(optionsEl, currentQuestion);
  }, currentQuestion.question.length * 30 + 500);
}

function typeWriterEffect(element, text, speed = 30) {
  element.textContent = '';
  let i = 0;
  
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  
  type();
}

function showOptions(container, question) {
  const shuffledOptions = [...question.options].sort(() => Math.random() - 0.5);
  
  shuffledOptions.forEach((option, index) => {
    const optionBtn = document.createElement('button');
    optionBtn.className = 'sorting-hat-option';
    optionBtn.textContent = option;
    optionBtn.style.opacity = '0';
    optionBtn.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      optionBtn.style.opacity = '1';
      optionBtn.style.transform = 'translateY(0)';
    }, index * 150);
    
    optionBtn.addEventListener('click', () => handleAnswer(option, question));
    container.appendChild(optionBtn);
  });
}

function handleAnswer(selectedAnswer, question) {
  const messageEl = document.getElementById('sortingHatMessage');
  const optionsEl = document.getElementById('sortingHatOptions');
  const nextBtn = document.getElementById('nextQuestion');
  
  const buttons = optionsEl.querySelectorAll('.sorting-hat-option');
  buttons.forEach(btn => {
    btn.disabled = true;
    if (btn.textContent === question.correctAnswer) {
      btn.classList.add('correct');
    } else if (btn.textContent === selectedAnswer && selectedAnswer !== question.correctAnswer) {
      btn.classList.add('wrong');
    }
  });
  
  let response;
  if (selectedAnswer === question.correctAnswer) {
    response = question.correctResponse;
  } else {
    response = question.wrongResponses[selectedAnswer];
  }
  
  setTimeout(() => {
    typeWriterEffect(messageEl, response, 25);
    nextBtn.style.display = 'inline-block';
  }, 500);
}

function createSortingHatTrigger() {
  const trigger = document.createElement('div');
  trigger.className = 'sorting-hat-trigger';
  trigger.innerHTML = '🎩';
  trigger.title = '点击试试分院帽小游戏';
  
  trigger.addEventListener('click', openSortingHat);
  
  document.body.appendChild(trigger);
}

document.addEventListener('DOMContentLoaded', () => {
  createSortingHatTrigger();
});