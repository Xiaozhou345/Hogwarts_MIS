const WEEKDAY_MAP = {
  1: '周一', 2: '周二', 3: '周三', 4: '周四', 
  5: '周五', 6: '周六', 7: '周日'
};

const PERFORMANCE_TYPE_MAP = {
  1: '回答问题',
  2: '课堂作业',
  3: '小组合作'
};

document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');
  
  if (!token || role !== '0') {
    alert('请先以学生身份登录');
    window.location.href = 'login.html';
    return;
  }
  
  document.getElementById('welcomeText').textContent = `${username} 的课程中心`;
  
  initTabs();
  
  await loadAvailableCourses();
  
  document.getElementById('closeDetailModalBtn').addEventListener('click', closeDetailModal);
  
  document.getElementById('backToHallBtn').addEventListener('click', () => {
    window.location.href = 'index.html';
  });
  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
});

function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  
  tabBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const tab = btn.dataset.tab;
      
      document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
      });
      
      const targetTab = document.getElementById(`${tab}Tab`.replace(/-([a-z])/g, (g) => g[1].toUpperCase()));
      if (!targetTab) {
        document.getElementById(`${tab === 'my-courses' ? 'myCourses' : tab === 'schedule' ? 'schedule' : 'performances'}Tab`).classList.add('active');
      } else {
        targetTab.classList.add('active');
      }
      
      if (tab === 'available') {
        await loadAvailableCourses();
      } else if (tab === 'my-courses') {
        await loadMyCourses();
      } else if (tab === 'schedule') {
        await loadMySchedule();
      } else if (tab === 'performances') {
        await loadMyPerformances();
      }
    });
  });
}

async function loadAvailableCourses() {
  const container = document.getElementById('availableCoursesContainer');
  
  try {
    const res = await getAvailableCourses();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      container.innerHTML = '';
      res.data.forEach(course => {
        const card = createAvailableCourseCard(course);
        container.appendChild(card);
      });
    } else if (res.code === 200) {
      container.innerHTML = '<p class="no-data">暂无可选课程</p>';
    } else {
      container.innerHTML = '<p class="error-text">加载失败</p>';
    }
  } catch (err) {
    console.error('加载可选课程失败:', err);
    container.innerHTML = '<p class="error-text">网络错误</p>';
  }
}

function createAvailableCourseCard(course) {
  const card = document.createElement('div');
  card.className = 'course-item-card';
  
  const statusText = course.is_enrolled ? '已选课 ✓' : '选课';
  const statusClass = course.is_enrolled ? 'enrolled' : '';
  
  card.innerHTML = `
    <div class="course-header">
      <h3 class="course-title">📚 ${course.course_name}</h3>
      <button class="enroll-btn ${statusClass}" data-id="${course.course_id}" data-enrolled="${course.is_enrolled}">
        ${statusText}
      </button>
    </div>
    <div class="course-body">
      <p class="course-info"><strong>教授：</strong>${course.professor_name || '未分配'}</p>
      <p class="course-info"><strong>学分：</strong>${course.credits}</p>
      <p class="course-info"><strong>描述：</strong>${course.description || '暂无'}</p>
      <p class="course-info"><strong>已选人数：</strong>${course.enrollment_count || 0}人</p>
    </div>
  `;
  
  const enrollBtn = card.querySelector('.enroll-btn');
  enrollBtn.addEventListener('click', async () => {
    const courseId = enrollBtn.dataset.id;
    const isEnrolled = enrollBtn.dataset.enrolled === 'true';
    
    if (isEnrolled) {
      alert('您已经选了这门课');
      return;
    }
    
    await handleEnroll(courseId, course.course_name);
  });
  
  return card;
}

async function handleEnroll(courseId, courseName) {
  if (!confirm(`确定要选修《${courseName}》吗？`)) return;

  try {
    const res = await enrollCourse({ course_id: parseInt(courseId) });
    if (res.code === 200) {
      alert('选课成功！');
      await loadAvailableCourses();
      // 修复：如果课程详情弹窗打开，刷新详情以更新选课人数
      if (document.getElementById('courseDetailModal').style.display === 'flex') {
        await showCourseDetail(courseId);
      }
    } else {
      alert(res.msg || '选课失败');
    }
  } catch (err) {
    console.error('选课失败:', err);
    alert('网络错误');
  }
}

async function loadMyCourses() {
  const container = document.getElementById('myCoursesContainer');
  
  try {
    const res = await getMyCourses();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      container.innerHTML = '';
      res.data.forEach(course => {
        const card = createMyCourseCard(course);
        container.appendChild(card);
      });
    } else if (res.code === 200) {
      container.innerHTML = '<p class="no-data">还没有选课，快去"可选课程"看看吧！</p>';
    } else {
      container.innerHTML = '<p class="error-text">加载失败</p>';
    }
  } catch (err) {
    console.error('加载我的课程失败:', err);
    container.innerHTML = '<p class="error-text">网络错误</p>';
  }
}

function createMyCourseCard(course) {
  const card = document.createElement('div');
  card.className = 'course-item-card';
  
  card.innerHTML = `
    <div class="course-header">
      <h3 class="course-title">📚 ${course.course_name}</h3>
      <div class="course-actions-btn">
        <button class="course-action-btn detail-btn" data-id="${course.course_id}">详情</button>
        <button class="course-action-btn drop-btn" data-id="${course.enrollment_id}" data-name="${course.course_name}">退课</button>
      </div>
    </div>
    <div class="course-body">
      <p class="course-info"><strong>教授：</strong>${course.professor_name || '未分配'}</p>
      <p class="course-info"><strong>学分：</strong>${course.credits}</p>
      <p class="course-info"><strong>描述：</strong>${course.description || '暂无'}</p>
    </div>
  `;
  
  card.querySelector('.detail-btn').addEventListener('click', () => {
    showCourseDetail(course.course_id);
  });
  
  card.querySelector('.drop-btn').addEventListener('click', async () => {
    const enrollmentId = card.querySelector('.drop-btn').dataset.id;
    const name = card.querySelector('.drop-btn').dataset.name;
    await handleDropCourse(enrollmentId, name);
  });
  
  return card;
}

async function handleDropCourse(enrollmentId, courseName) {
  if (!confirm(`确定要退选《${courseName}》吗？`)) return;
  
  try {
    const res = await dropCourse(enrollmentId);
    if (res.code === 200) {
      alert('已退课');
      await loadMyCourses();
    } else {
      alert(res.msg || '退课失败');
    }
  } catch (err) {
    console.error('退课失败:', err);
    alert('网络错误');
  }
}

async function showCourseDetail(courseId) {
  try {
    const res = await getCourseDetail(courseId);
    
    if (res.code === 200 && res.data) {
      const course = res.data;
      const content = document.getElementById('courseDetailContent');
      
      let scheduleHTML = '';
      if (course.schedules && course.schedules.length > 0) {
        scheduleHTML = '<h4 style="margin-top: 15px;">课程安排：</h4>';
        course.schedules.forEach(s => {
          scheduleHTML += `<p>${WEEKDAY_MAP[s.weekday]} ${s.start_time}-${s.end_time} @ ${s.classroom}</p>`;
        });
      }
      
      content.innerHTML = `
        <div class="course-detail">
          <h3>📚 ${course.course_name}</h3>
          <p><strong>教授：</strong>${course.professor_name || '未分配'}</p>
          <p><strong>学分：</strong>${course.credits}</p>
          <p><strong>描述：</strong>${course.description || '暂无'}</p>
          <p><strong>选课人数：</strong>${course.enrollment_count || 0}人</p>
          ${scheduleHTML}
        </div>
      `;
      
      document.getElementById('detailModalTitle').textContent = '课程详情';
      document.getElementById('courseDetailModal').style.display = 'flex';
    } else {
      alert('加载课程详情失败');
    }
  } catch (err) {
    console.error('加载课程详情失败:', err);
    alert('网络错误');
  }
}

function closeDetailModal() {
  document.getElementById('courseDetailModal').style.display = 'none';
}

// 时间字符串转分钟数（用于数值比较）
function timeToMinutes(timeStr) {
  if (!timeStr) return 0;
  const parts = timeStr.split(':');
  const hours = parseInt(parts[0], 10);
  const minutes = parseInt(parts[1], 10);
  return hours * 60 + minutes;
}

async function loadMySchedule() {
  const container = document.getElementById('scheduleContainer');

  try {
    const res = await getMySchedule();

    if (res.code === 200 && res.data) {
      const weekData = res.data;
      const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

      let html = '<table class="schedule-table">';
      html += '<thead><tr><th>时间</th>';
      dayNames.forEach(day => {
        html += `<th>${day}</th>`;
      });
      html += '</tr></thead><tbody>';

      const timeSlots = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'];

      timeSlots.forEach(time => {
        html += `<tr><td class="time-cell">${time}</td>`;
        const slotMinutes = timeToMinutes(time);

        days.forEach(day => {
          const courses = weekData[day] || [];
          // 修复：使用数值比较而不是字符串比较
          const course = courses.find(c => {
            const startMinutes = timeToMinutes(c.start_time);
            const endMinutes = timeToMinutes(c.end_time);
            return slotMinutes >= startMinutes && slotMinutes < endMinutes;
          });

          if (course) {
            html += `
              <td class="course-cell">
                <div class="schedule-course">${course.course_name}</div>
                <div class="schedule-room">${course.classroom}</div>
                <div class="schedule-professor">${course.professor_name}</div>
              </td>
            `;
          } else {
            html += '<td class="empty-cell"></td>';
          }
        });
        html += '</tr>';
      });

      html += '</tbody></table>';
      container.innerHTML = html;
    } else if (res.code === 200) {
      container.innerHTML = '<p class="no-data">还没有选课，暂无课程表</p>';
    } else {
      container.innerHTML = '<p class="error-text">加载失败</p>';
    }
  } catch (err) {
    console.error('加载课程表失败:', err);
    container.innerHTML = '<p class="error-text">网络错误</p>';
  }
}

async function loadMyPerformances() {
  const container = document.getElementById('performancesContainer');

  try {
    const res = await getMyPerformances();

    // 修复：后端返回的是 {performances: [...], total, page, limit}，不是直接的数组
    if (res.code === 200 && res.data && res.data.performances && res.data.performances.length > 0) {
      container.innerHTML = '';

      res.data.performances.forEach(perf => {
        const item = document.createElement('div');
        item.className = 'performance-item';

        const scoreClass = perf.score > 0 ? 'score-positive' : 'score-negative';
        const scoreText = perf.score > 0 ? `+${perf.score}` : perf.score;
        const time = new Date(perf.create_time).toLocaleString('zh-CN');

        item.innerHTML = `
          <div class="performance-header">
            <span class="performance-course">📚 ${perf.course_name}</span>
            <span class="performance-type">${PERFORMANCE_TYPE_MAP[perf.performance_type]}</span>
          </div>
          <div class="performance-body">
            <p><strong>教授：</strong>${perf.professor_name}</p>
            <p><strong>积分：</strong><span class="${scoreClass}">${scoreText}</span></p>
            <p><strong>原因：</strong>${perf.reason}</p>
            <p><strong>时间：</strong>${time}</p>
          </div>
        `;

        container.appendChild(item);
      });
    } else if (res.code === 200) {
      container.innerHTML = '<p class="no-data">还没有课堂表现记录</p>';
    } else {
      container.innerHTML = '<p class="error-text">加载失败</p>';
    }
  } catch (err) {
    console.error('加载课堂表现失败:', err);
    container.innerHTML = '<p class="error-text">网络错误</p>';
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
    window.location.href = 'index.html';
  }
}