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
let bubbleInterval = null;
let isDragging = false;

function createBubble(text) {
  if (isDragging) return;
  
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
  
  bubbleInterval = setInterval(showNextRule, 4000);
}

function initDraggableDumbledore() {
  const panel = document.querySelector('.dumbledore-panel');
  const avatar = document.querySelector('.dumbledore-avatar');
  
  if (!panel || !avatar) return;
  
  let isDraggingLocal = false;
  let startX, startY, initialX, initialY;
  
  avatar.style.cursor = 'grab';
  
  function onMouseDown(e) {
    isDraggingLocal = true;
    isDragging = true;
    avatar.style.cursor = 'grabbing';
    
    startX = e.clientX;
    startY = e.clientY;
    
    const rect = panel.getBoundingClientRect();
    initialX = rect.left;
    initialY = rect.top;
    
    panel.style.transition = 'none';
    
    const bubbleContainer = document.getElementById('bubbleContainer');
    if (bubbleContainer) {
      bubbleContainer.style.opacity = '0';
    }
    
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    
    e.preventDefault();
  }
  
  function onMouseMove(e) {
    if (!isDraggingLocal) return;
    
    const deltaX = e.clientX - startX;
    const deltaY = e.clientY - startY;
    
    let newX = initialX + deltaX;
    let newY = initialY + deltaY;
    
    const panelRect = panel.getBoundingClientRect();
    const maxX = window.innerWidth - panelRect.width;
    const maxY = window.innerHeight - panelRect.height;
    
    newX = Math.max(0, Math.min(newX, maxX));
    newY = Math.max(0, Math.min(newY, maxY));
    
    panel.style.left = newX + 'px';
    panel.style.top = newY + 'px';
    panel.style.right = 'auto';
    panel.style.transform = 'none';
  }
  
  function onMouseUp(e) {
    if (!isDraggingLocal) return;
    
    isDraggingLocal = false;
    isDragging = false;
    avatar.style.cursor = 'grab';
    
    panel.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
      const bubbleContainer = document.getElementById('bubbleContainer');
      if (bubbleContainer) {
        bubbleContainer.style.opacity = '1';
      }
    }, 300);
    
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }
  
  avatar.addEventListener('mousedown', onMouseDown);
  
  avatar.addEventListener('dragstart', (e) => {
    e.preventDefault();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initBubbles();
  initDraggableDumbledore();
});
