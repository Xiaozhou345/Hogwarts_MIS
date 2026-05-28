const HOUSE_CONFIG = {
  1: { 
    name: 'Gryffindor', 
    chinese: '格兰芬多',
    icon: '🦁',
    color: 'gryffindor',
    values: '勇气、胆识、气魄'
  },
  2: { 
    name: 'Slytherin', 
    chinese: '斯莱特林',
    icon: '🐍',
    color: 'slytherin',
    values: '野心、精明、领导力'
  },
  3: { 
    name: 'Ravenclaw', 
    chinese: '拉文克劳',
    icon: '🦅',
    color: 'ravenclaw',
    values: '智慧、创造力、学习'
  },
  4: { 
    name: 'Hufflepuff', 
    chinese: '赫奇帕奇',
    icon: '🦡',
    color: 'hufflepuff',
    values: '忠诚、耐心、勤劳'
  }
};

const DUMBLEDORE_QUOTES = [
  "在霍格沃茨，我们相信每个学生都有展现自己才华的机会。",
  "幸福可以在最黑暗的时期找到，只要记得打开通往光明的门。",
  "一个人的出身并不重要，重要的是他成长为一个什么样的人。",
  "我们做出的选择，比我们的天赋更能说明我们是怎样的人。",
  "即使在最黑暗的时刻，幸福依然触手可及。",
  "勇气、友谊和忠诚——这是霍格沃茨最珍贵的财富。",
  "每个学生都有属于自己的学院，每个学院都有属于自己的荣耀。",
  "记住，被送进禁林的学生，一定是因为他们做了值得被送进去的事。"
];

document.addEventListener('DOMContentLoaded', async () => {
  checkLoginStatus();
  await loadRanking();
  await loadRecentActivity();
  showRandomQuote();
  
  document.getElementById('loginBtn').addEventListener('click', () => {
    window.location.href = 'login.html';
  });
  
  document.getElementById('userBtn').addEventListener('click', handleUserNavigation);
  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
});

function checkLoginStatus() {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');
  
  const loginBtn = document.getElementById('loginBtn');
  const userBtn = document.getElementById('userBtn');
  const logoutBtn = document.getElementById('logoutBtn');
  const userText = document.getElementById('userText');
  
  if (token) {
    loginBtn.style.display = 'none';
    userBtn.style.display = 'flex';
    logoutBtn.style.display = 'flex';
    
    const roleText = role === '1' ? '教授' : '学生';
    userText.textContent = `${username} (${roleText})`;
  } else {
    loginBtn.style.display = 'flex';
    userBtn.style.display = 'none';
    logoutBtn.style.display = 'none';
  }
}

function handleUserNavigation() {
  const role = localStorage.getItem('role');
  
  if (role === '1') {
    window.location.href = 'professor.html';
  } else {
    window.location.href = 'student.html';
  }
}

async function handleLogout() {
  try {
    await logout();
  } catch (err) {
    console.error('退出失败:', err);
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('house_id');
    window.location.reload();
  }
}

async function loadRanking() {
  const container = document.getElementById('rankingContainer');
  
  try {
    const res = await getHouseRanking();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      container.innerHTML = '';
      
      res.data.forEach((house, index) => {
        const config = HOUSE_CONFIG[house.house_id];
        const card = createHouseCard(house, config, index + 1);
        container.appendChild(card);
      });
    } else {
      container.innerHTML = '<p class="no-data">暂无学院数据</p>';
    }
  } catch (err) {
    console.error('加载排行榜失败:', err);
    container.innerHTML = '<p class="error-text">无法连接到魔法服务器</p>';
  }
}

function createHouseCard(house, config, rank) {
  const card = document.createElement('div');
  card.className = `house-card ${config.color}`;
  
  const rankBadge = rank === 1 ? '👑' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `#${rank}`;
  
  card.innerHTML = `
    <div class="house-rank">${rankBadge}</div>
    <div class="house-icon">${config.icon}</div>
    <h3 class="house-name">${config.chinese}</h3>
    <p class="house-name-en">${config.name}</p>
    <div class="house-points-container">
      <div class="house-points-label">学院积分</div>
      <div class="house-points-value">${house.total_points || 0}</div>
    </div>
    <div class="house-values">✦ ${config.values} ✦</div>
    <div class="house-glow"></div>
  `;
  
  return card;
}

async function loadRecentActivity() {
  const container = document.getElementById('activityContainer');
  
  try {
    const res = await getPublicLogs();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      container.innerHTML = '';
      
      res.data.slice(0, 5).forEach(log => {
        const item = createActivityItem(log);
        container.appendChild(item);
      });
    } else {
      container.innerHTML = '<p class="no-data">暂无最新动态</p>';
    }
  } catch (err) {
    console.error('加载动态失败:', err);
    container.innerHTML = '<p class="error-text">无法获取最新动态</p>';
  }
}

function createActivityItem(log) {
  const item = document.createElement('div');
  item.className = 'activity-item';
  
  const scoreClass = log.score_change > 0 ? 'score-positive' : 'score-negative';
  const scoreText = log.score_change > 0 ? `+${log.score_change}` : log.score_change;
  const time = formatTime(log.create_time);
  
  item.innerHTML = `
    <div class="activity-icon">${log.score_change > 0 ? '⬆️' : '⬇️'}</div>
    <div class="activity-content">
      <div class="activity-main">
        <span class="student-name">${log.student_name}</span>
        <span class="score-change ${scoreClass}">${scoreText}</span>
      </div>
      <div class="activity-detail">
        <span class="professor-name">by ${log.professor_name}</span>
        <span class="activity-divider">•</span>
        <span class="activity-reason">${log.reason}</span>
      </div>
    </div>
    <div class="activity-time">${time}</div>
  `;
  
  return item;
}

function formatTime(timeStr) {
  const date = new Date(timeStr);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  
  return date.toLocaleDateString('zh-CN');
}

function showRandomQuote() {
  const quoteElement = document.getElementById('dumbledoreMessage');
  const randomIndex = Math.floor(Math.random() * DUMBLEDORE_QUOTES.length);
  quoteElement.textContent = `"${DUMBLEDORE_QUOTES[randomIndex]}"`;
}