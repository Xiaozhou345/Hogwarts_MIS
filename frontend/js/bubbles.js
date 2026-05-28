const schoolRules = [
  "禁止前往三楼走廊右侧的房间",
  "禁林严禁学生进入",
  "严禁在走廊施法",
  "禁止携带恶作剧道具",
  "图书馆严禁喧哗",
  "禁止私自调制魔药",
  "魁地奇训练需经霍琦夫人批准",
  "禁止夜游霍格沃茨",
  "不可辱骂幽灵",
  "严禁使用不可饶恕咒"
];

let currentRuleIndex = 0;
const maxVisibleBubbles = 4;

function createBubble(text) {
  const container = document.getElementById('bubbleContainer');
  if (!container) return;
  
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = `<div class="bubble-text">${text}</div>`;
  
  container.insertBefore(bubble, container.firstChild);
  
  setTimeout(() => {
    bubble.classList.add('show');
  }, 50);
  
  const bubbles = container.querySelectorAll('.bubble');
  if (bubbles.length > maxVisibleBubbles) {
    const oldBubble = bubbles[bubbles.length - 1];
    oldBubble.style.opacity = '0';
    oldBubble.style.transform = 'translateX(50px)';
    setTimeout(() => {
      oldBubble.remove();
    }, 300);
  }
}

function showNextRule() {
  createBubble(schoolRules[currentRuleIndex]);
  currentRuleIndex = (currentRuleIndex + 1) % schoolRules.length;
}

function initBubbles() {
  createBubble(schoolRules[0]);
  currentRuleIndex = 1;
  
  setInterval(showNextRule, 4000);
}

document.addEventListener('DOMContentLoaded', initBubbles);
