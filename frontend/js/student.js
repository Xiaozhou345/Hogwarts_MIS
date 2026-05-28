const HOUSE_MAP = {
  1: { name: 'Gryffindor', chinese: '格兰芬多', class: 'gryffindor' },
  2: { name: 'Slytherin', chinese: '斯莱特林', class: 'slytherin' },
  3: { name: 'Ravenclaw', chinese: '拉文克劳', class: 'ravenclaw' },
  4: { name: 'Hufflepuff', chinese: '赫奇帕奇', class: 'hufflepuff' }
};

document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  
  if (!token || role !== '0') {
    alert('请先以学生身份登录');
    window.location.href = 'login.html';
    return;
  }
  
  await loadStudentInfo();
  await loadStudentLogs();
  
  document.getElementById('backToHallBtn').addEventListener('click', () => {
    window.location.href = 'index.html';
  });
  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
});

async function loadStudentInfo() {
  const infoContainer = document.getElementById('infoContainer');
  
  try {
    const res = await getStudentInfo();
    
    if (res.code === 200 && res.data) {
      const { username, house_name, total_points } = res.data;
      const houseId = localStorage.getItem('house_id');
      const houseInfo = HOUSE_MAP[houseId] || { chinese: house_name, class: '' };
      
      infoContainer.innerHTML = `
        <div class="info-item">
          <span class="info-label">学生姓名</span>
          <span class="info-value">${username}</span>
        </div>
        <div class="info-item">
          <span class="info-label">所属学院</span>
          <span class="info-value">
            <span class="house-badge ${houseInfo.class}">${houseInfo.chinese}</span>
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">学院总分</span>
          <span class="info-value">${total_points} 分</span>
        </div>
      `;
    } else {
      infoContainer.innerHTML = '<p class="no-logs">加载个人信息失败</p>';
    }
  } catch (err) {
    console.error('加载个人信息失败:', err);
    infoContainer.innerHTML = '<p class="no-logs">网络错误</p>';
  }
}

async function loadStudentLogs() {
  const logsContainer = document.getElementById('logsContainer');
  
  try {
    const res = await getStudentLogs();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      let tableHTML = `
        <table class="logs-table">
          <thead>
            <tr>
              <th>教授姓名</th>
              <th>分数变动</th>
              <th>原因</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
      `;
      
      res.data.forEach(log => {
        const scoreClass = log.score_change > 0 ? 'score-positive' : 'score-negative';
        const scoreText = log.score_change > 0 ? `+${log.score_change}` : log.score_change;
        const time = new Date(log.create_time).toLocaleString('zh-CN');
        
        tableHTML += `
          <tr>
            <td>${log.professor_name}</td>
            <td class="${scoreClass}">${scoreText}</td>
            <td>${log.reason}</td>
            <td>${time}</td>
          </tr>
        `;
      });
      
      tableHTML += '</tbody></table>';
      logsContainer.innerHTML = tableHTML;
    } else if (res.code === 200) {
      logsContainer.innerHTML = '<p class="no-logs">暂无积分变动记录</p>';
    } else {
      logsContainer.innerHTML = '<p class="no-logs">加载失败</p>';
    }
  } catch (err) {
    console.error('加载积分流水失败:', err);
    logsContainer.innerHTML = '<p class="no-logs">网络错误</p>';
  }
}

async function handleLogout() {
  try {
    await logout();
  } catch (err) {
    console.error('退出登录失败:', err);
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('house_id');
    window.location.href = 'login.html';
  }
}