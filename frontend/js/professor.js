document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');
  
  if (!token || role !== '1') {
    alert('请先以教授身份登录');
    window.location.href = 'login.html';
    return;
  }
  
  document.getElementById('welcomeText').textContent = `欢迎，${username} 教授`;
  
  await loadStudents();
  await loadLogs();
  
  document.getElementById('submitBtn').addEventListener('click', handleSubmit);
  document.getElementById('backToHallBtn').addEventListener('click', () => {
    window.location.href = 'index.html';
  });
  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
});

async function loadStudents() {
  const studentSelect = document.getElementById('studentSelect');
  
  try {
    const res = await getStudents();
    
    if (res.code === 200 && res.data) {
      studentSelect.innerHTML = '<option value="">-- 请选择学生 --</option>';
      res.data.forEach(student => {
        const option = document.createElement('option');
        option.value = student.user_id;
        option.textContent = `${student.username} (学院ID: ${student.house_id})`;
        studentSelect.appendChild(option);
      });
    } else {
      studentSelect.innerHTML = '<option value="">加载失败</option>';
    }
  } catch (err) {
    console.error('加载学生列表失败:', err);
    studentSelect.innerHTML = '<option value="">网络错误</option>';
  }
}

async function handleSubmit() {
  const studentId = document.getElementById('studentSelect').value;
  const scoreChange = document.getElementById('scoreChange').value;
  const reason = document.getElementById('reason').value.trim();
  
  const errorMsg = document.getElementById('errorMsg');
  const successMsg = document.getElementById('successMsg');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = document.getElementById('btnText');
  
  errorMsg.textContent = '';
  successMsg.style.display = 'none';
  
  if (!studentId) {
    errorMsg.textContent = '请选择学生';
    return;
  }
  
  if (!scoreChange || scoreChange === '0') {
    errorMsg.textContent = '请输入有效的分数变动';
    return;
  }
  
  if (!reason) {
    errorMsg.textContent = '请输入原因说明';
    return;
  }
  
  submitBtn.disabled = true;
  btnText.textContent = '提交中...';
  
  try {
    const res = await submitPoints({
      student_id: parseInt(studentId),
      score_change: parseInt(scoreChange),
      reason: reason
    });
    
    if (res.code === 200) {
      successMsg.textContent = '积分工单提交成功！';
      successMsg.style.display = 'block';
      
      document.getElementById('scoreChange').value = '';
      document.getElementById('reason').value = '';
      document.getElementById('studentSelect').value = '';
      
      await loadLogs();
    } else {
      errorMsg.textContent = res.msg || '提交失败';
    }
  } catch (err) {
    console.error('提交工单失败:', err);
    errorMsg.textContent = '网络错误，请重试';
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = '提交工单';
  }
}

async function loadLogs() {
  const logsContainer = document.getElementById('logsContainer');
  
  try {
    const res = await getProfessorLogs();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      let tableHTML = `
        <table class="logs-table">
          <thead>
            <tr>
              <th>学生姓名</th>
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
            <td>${log.student_name}</td>
            <td class="${scoreClass}">${scoreText}</td>
            <td>${log.reason}</td>
            <td>${time}</td>
          </tr>
        `;
      });
      
      tableHTML += '</tbody></table>';
      logsContainer.innerHTML = tableHTML;
    } else if (res.code === 200) {
      logsContainer.innerHTML = '<p class="no-logs">暂无操作记录</p>';
    } else {
      logsContainer.innerHTML = '<p class="no-logs">加载失败</p>';
    }
  } catch (err) {
    console.error('加载操作历史失败:', err);
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