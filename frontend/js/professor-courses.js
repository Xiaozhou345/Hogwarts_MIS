const WEEKDAY_MAP = {
  1: '周一', 2: '周二', 3: '周三', 4: '周四', 
  5: '周五', 6: '周六', 7: '周日'
};

let currentEditCourseId = null;
let allStudents = [];

document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');
  
  if (!token || role !== '1') {
    alert('请先以教授身份登录');
    window.location.href = 'login.html';
    return;
  }
  
  document.getElementById('welcomeText').textContent = `${username} 教授的课程管理`;
  
  await loadCourses();
  await loadAllStudents();
  
  document.getElementById('createCourseBtn').addEventListener('click', () => {
    currentEditCourseId = null;
    openCourseModal();
  });
  
  document.getElementById('closeModalBtn').addEventListener('click', closeCourseModal);
  document.getElementById('closeScheduleModalBtn').addEventListener('click', closeScheduleModal);
  document.getElementById('closePerformanceModalBtn').addEventListener('click', closePerformanceModal);
  
  document.getElementById('courseForm').addEventListener('submit', handleCourseSubmit);
  document.getElementById('scheduleForm').addEventListener('submit', handleScheduleSubmit);
  document.getElementById('performanceForm').addEventListener('submit', handlePerformanceSubmit);
  
  document.getElementById('backToHallBtn').addEventListener('click', () => {
    window.location.href = 'index.html';
  });
  document.getElementById('logoutBtn').addEventListener('click', handleLogout);
});

async function loadAllStudents() {
  try {
    const res = await getStudents();
    if (res.code === 200 && res.data) {
      allStudents = res.data;
    }
  } catch (err) {
    console.error('加载学生列表失败:', err);
  }
}

async function loadCourses() {
  const container = document.getElementById('coursesContainer');
  
  try {
    const res = await getProfessorCourses();
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      container.innerHTML = '';
      res.data.forEach(course => {
        const card = createCourseCard(course);
        container.appendChild(card);
      });
    } else if (res.code === 200) {
      container.innerHTML = '<p class="no-data">还没有创建课程，点击上方按钮创建第一门课程</p>';
    } else {
      container.innerHTML = '<p class="error-text">加载失败</p>';
    }
  } catch (err) {
    console.error('加载课程失败:', err);
    container.innerHTML = '<p class="error-text">网络错误</p>';
  }
}

function createCourseCard(course) {
  const card = document.createElement('div');
  card.className = 'course-item-card';
  
  card.innerHTML = `
    <div class="course-header">
      <h3 class="course-title">📚 ${course.course_name}</h3>
      <div class="course-actions-btn">
        <button class="course-action-btn edit-btn" data-id="${course.course_id}">编辑</button>
        <button class="course-action-btn schedule-btn" data-id="${course.course_id}">安排</button>
        <button class="course-action-btn students-btn" data-id="${course.course_id}">名单</button>
        <button class="course-action-btn performance-btn" data-id="${course.course_id}">记录</button>
        <button class="course-action-btn delete-btn" data-id="${course.course_id}">删除</button>
      </div>
    </div>
    <div class="course-body">
      <p class="course-info"><strong>学分：</strong>${course.credits}</p>
      <p class="course-info"><strong>描述：</strong>${course.description || '暂无'}</p>
      <p class="course-info"><strong>选课人数：</strong>${course.enrollment_count || 0}人</p>
    </div>
  `;
  
  card.querySelector('.edit-btn').addEventListener('click', () => {
    currentEditCourseId = course.course_id;
    openCourseModal(course);
  });
  
  card.querySelector('.schedule-btn').addEventListener('click', () => {
    openScheduleModal(course.course_id);
  });
  
  card.querySelector('.students-btn').addEventListener('click', () => {
    showEnrolledStudents(course.course_id, course.course_name);
  });
  
  card.querySelector('.performance-btn').addEventListener('click', () => {
    openPerformanceModal(course.course_id);
  });
  
  card.querySelector('.delete-btn').addEventListener('click', () => {
    handleDeleteCourse(course.course_id, course.course_name);
  });
  
  return card;
}

function openCourseModal(course = null) {
  const modal = document.getElementById('courseModal');
  const title = document.getElementById('modalTitle');
  const btnText = document.getElementById('courseBtnText');
  
  if (course) {
    title.textContent = '编辑课程';
    btnText.textContent = '更新';
    document.getElementById('courseName').value = course.course_name;
    document.getElementById('courseCredits').value = course.credits;
    document.getElementById('courseDescription').value = course.description || '';
  } else {
    title.textContent = '创建课程';
    btnText.textContent = '创建';
    document.getElementById('courseForm').reset();
  }
  
  modal.style.display = 'flex';
}

function closeCourseModal() {
  document.getElementById('courseModal').style.display = 'none';
  currentEditCourseId = null;
}

async function handleCourseSubmit(e) {
  e.preventDefault();
  
  const data = {
    course_name: document.getElementById('courseName').value.trim(),
    credits: parseInt(document.getElementById('courseCredits').value),
    description: document.getElementById('courseDescription').value.trim()
  };
  
  try {
    let res;
    if (currentEditCourseId) {
      res = await updateCourse(currentEditCourseId, data);
    } else {
      res = await createCourse(data);
    }
    
    if (res.code === 200) {
      alert(currentEditCourseId ? '课程更新成功！' : '课程创建成功！');
      closeCourseModal();
      await loadCourses();
    } else {
      alert(res.msg || '操作失败');
    }
  } catch (err) {
    console.error('提交失败:', err);
    alert('网络错误');
  }
}

async function handleDeleteCourse(courseId, courseName) {
  if (!confirm(`确定要删除课程"${courseName}"吗？此操作不可撤销！`)) {
    return;
  }
  
  try {
    const res = await deleteCourse(courseId);
    if (res.code === 200) {
      alert('课程已删除');
      await loadCourses();
    } else {
      alert(res.msg || '删除失败');
    }
  } catch (err) {
    console.error('删除失败:', err);
    alert('网络错误');
  }
}

function openScheduleModal(courseId) {
  document.getElementById('scheduleCourseId').value = courseId;
  document.getElementById('scheduleModal').style.display = 'flex';
  loadCourseSchedule(courseId);
}

function closeScheduleModal() {
  document.getElementById('scheduleModal').style.display = 'none';
}

async function loadCourseSchedule(courseId) {
  const container = document.getElementById('existingSchedule');
  
  try {
    const res = await getCourseSchedule(courseId);
    
    if (res.code === 200 && res.data && res.data.length > 0) {
      let html = '<h4 style="margin-bottom: 10px;">已有安排：</h4>';
      res.data.forEach(schedule => {
        html += `
          <div class="schedule-item">
            <span>${WEEKDAY_MAP[schedule.weekday]} ${schedule.start_time}-${schedule.end_time} @ ${schedule.classroom}</span>
            <button class="delete-schedule-btn" data-id="${schedule.schedule_id}">删除</button>
          </div>
        `;
      });
      container.innerHTML = html;
      
      container.querySelectorAll('.delete-schedule-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const scheduleId = btn.dataset.id;
          await handleDeleteSchedule(scheduleId, courseId);
        });
      });
    } else {
      container.innerHTML = '<p class="no-data">暂无课程安排</p>';
    }
  } catch (err) {
    console.error('加载课程安排失败:', err);
  }
}

async function handleScheduleSubmit(e) {
  e.preventDefault();
  
  const courseId = document.getElementById('scheduleCourseId').value;
  const data = {
    weekday: parseInt(document.getElementById('scheduleWeekday').value),
    start_time: document.getElementById('scheduleStartTime').value,
    end_time: document.getElementById('scheduleEndTime').value,
    classroom: document.getElementById('scheduleClassroom').value.trim()
  };
  
  try {
    const res = await addCourseSchedule(courseId, data);
    if (res.code === 200) {
      alert('课程安排添加成功！');
      document.getElementById('scheduleForm').reset();
      await loadCourseSchedule(courseId);
    } else {
      alert(res.msg || '添加失败');
    }
  } catch (err) {
    console.error('添加失败:', err);
    alert('网络错误');
  }
}

async function handleDeleteSchedule(scheduleId, courseId) {
  if (!confirm('确定删除此课程安排？')) return;
  
  try {
    const res = await deleteSchedule(scheduleId);
    if (res.code === 200) {
      alert('已删除');
      await loadCourseSchedule(courseId);
    } else {
      alert(res.msg || '删除失败');
    }
  } catch (err) {
    console.error('删除失败:', err);
    alert('网络错误');
  }
}

async function showEnrolledStudents(courseId, courseName) {
  try {
    const res = await getEnrolledStudents(courseId);
    
    if (res.code === 200 && res.data) {
      let message = `《${courseName}》选课学生名单：\n\n`;
      if (res.data.length === 0) {
        message += '暂无学生选课';
      } else {
        res.data.forEach((student, index) => {
          message += `${index + 1}. ${student.username} (学院ID: ${student.house_id})\n`;
        });
      }
      alert(message);
    } else {
      alert('加载失败');
    }
  } catch (err) {
    console.error('加载学生名单失败:', err);
    alert('网络错误');
  }
}

function openPerformanceModal(courseId) {
  document.getElementById('performanceCourseId').value = courseId;
  
  const studentSelect = document.getElementById('performanceStudent');
  studentSelect.innerHTML = '<option value="">-- 请选择学生 --</option>';
  allStudents.forEach(student => {
    const option = document.createElement('option');
    option.value = student.user_id;
    option.textContent = `${student.username} (学院ID: ${student.house_id})`;
    studentSelect.appendChild(option);
  });
  
  document.getElementById('performanceModal').style.display = 'flex';
}

function closePerformanceModal() {
  document.getElementById('performanceModal').style.display = 'none';
  document.getElementById('performanceForm').reset();
}

async function handlePerformanceSubmit(e) {
  e.preventDefault();
  
  const data = {
    student_id: parseInt(document.getElementById('performanceStudent').value),
    course_id: parseInt(document.getElementById('performanceCourseId').value),
    performance_type: parseInt(document.getElementById('performanceType').value),
    score: parseInt(document.getElementById('performanceScore').value),
    reason: document.getElementById('performanceReason').value.trim()
  };
  
  try {
    const res = await recordClassPerformance(data);
    if (res.code === 200) {
      alert('课堂表现记录成功！积分已自动更新');
      closePerformanceModal();
    } else {
      alert(res.msg || '记录失败');
    }
  } catch (err) {
    console.error('记录失败:', err);
    alert('网络错误');
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