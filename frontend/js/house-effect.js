const houseEffects = {
  gryffindor: {
    name: '格兰芬多',
    color: '#D3A625',
    bgColor: 'rgba(116, 0, 1, 0.3)',
    particles: ['🦁', '⚔️', '🔥', '✨', '💫'],
    message: '勇气与骑士精神！Gryffindor!',
    quote: '"真正的勇气，是在最黑暗的时刻依然坚持正义。"'
  },
  slytherin: {
    name: '斯莱特林',
    color: '#AAAAAA',
    bgColor: 'rgba(26, 71, 42, 0.3)',
    particles: ['🐍', '💎', '🌙', '✨', '💫'],
    message: '野心与精明！Slytherin!',
    quote: '"伟大的成就，往往源于坚定的野心与不懈的追求。"'
  },
  ravenclaw: {
    name: '拉文克劳',
    color: '#B08A68',
    bgColor: 'rgba(14, 26, 64, 0.3)',
    particles: ['🦅', '📚', '🔮', '✨', '💫'],
    message: '智慧与学识！Ravenclaw!',
    quote: '"智慧超越度量，是人类最宝贵的财富。"'
  },
  hufflepuff: {
    name: '赫奇帕奇',
    color: '#FFDB00',
    bgColor: 'rgba(55, 46, 41, 0.3)',
    particles: ['🦡', '🌻', '🍯', '✨', '💫'],
    message: '忠诚与勤奋！Hufflepuff!',
    quote: '"真正的力量，来自于坚定的忠诚与不懈的努力。"'
  }
};

let isEffectActive = false;

function createHouseEffectOverlay(house) {
  const effect = houseEffects[house];
  if (!effect) return;
  
  if (isEffectActive) return;
  isEffectActive = true;
  
  const overlay = document.createElement('div');
  overlay.className = 'house-effect-overlay';
  overlay.style.setProperty('--house-color', effect.color);
  overlay.style.setProperty('--house-bg', effect.bgColor);
  
  overlay.innerHTML = `
    <div class="house-effect-particles" id="effectParticles"></div>
    <div class="house-effect-content">
      <div class="house-effect-icon">${effect.particles[0]}</div>
      <div class="house-effect-title">${effect.name}</div>
      <div class="house-effect-message">${effect.message}</div>
      <div class="house-effect-quote">${effect.quote}</div>
    </div>
  `;
  
  document.body.appendChild(overlay);
  
  setTimeout(() => {
    overlay.classList.add('show');
  }, 50);
  
  createEffectParticles(effect.particles);
  
  setTimeout(() => {
    overlay.classList.remove('show');
    setTimeout(() => {
      if (overlay.parentNode) {
        overlay.parentNode.removeChild(overlay);
      }
      isEffectActive = false;
    }, 500);
  }, 3500);
}

function createEffectParticles(particleTypes) {
  const container = document.getElementById('effectParticles');
  if (!container) return;
  
  for (let i = 0; i < 40; i++) {
    setTimeout(() => {
      const particle = document.createElement('div');
      particle.className = 'effect-particle';
      particle.textContent = particleTypes[Math.floor(Math.random() * particleTypes.length)];
      
      particle.style.left = Math.random() * 100 + '%';
      particle.style.top = Math.random() * 100 + '%';
      particle.style.fontSize = (20 + Math.random() * 30) + 'px';
      particle.style.animationDelay = Math.random() * 0.5 + 's';
      particle.style.animationDuration = (2 + Math.random() * 2) + 's';
      
      container.appendChild(particle);
      
      setTimeout(() => {
        if (particle.parentNode) {
          particle.parentNode.removeChild(particle);
        }
      }, 4000);
    }, i * 50);
  }
}

function initCrestDoubleClick() {
  const crests = document.querySelectorAll('.crest');
  
  crests.forEach(crest => {
    crest.addEventListener('dblclick', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      const houseMap = {
        'gryffindor-crest': 'gryffindor',
        'slytherin-crest': 'slytherin',
        'ravenclaw-crest': 'ravenclaw',
        'hufflepuff-crest': 'hufflepuff'
      };
      
      for (const [className, house] of Object.entries(houseMap)) {
        if (crest.classList.contains(className)) {
          createHouseEffectOverlay(house);
          break;
        }
      }
    });
    
    crest.addEventListener('click', (e) => {
      if (e.detail === 1) {
        crest.style.transform = 'scale(1.3)';
        setTimeout(() => {
          crest.style.transform = '';
        }, 200);
      }
    });
  });
  
  const houseCards = document.querySelectorAll('.house-card');
  
  houseCards.forEach(card => {
    const houseMap = {
      'gryffindor': 'gryffindor',
      'slytherin': 'slytherin',
      'ravenclaw': 'ravenclaw',
      'hufflepuff': 'hufflepuff'
    };
    
    for (const [className, house] of Object.entries(houseMap)) {
      if (card.classList.contains(className)) {
        card.addEventListener('dblclick', (e) => {
          e.preventDefault();
          createHouseEffectOverlay(house);
        });
        break;
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initCrestDoubleClick();
});