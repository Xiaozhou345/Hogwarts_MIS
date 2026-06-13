let timeTurnerData = {
  hasTimeTurner: false,
  houseName: null,
  isTopHouse: false,
  activities: [],
  myActivities: []
};

let timeTurnerPanel = null;
let isPanelOpen = false;

async function initTimeTurner() {
  try {
    const res = await getTimeTurnerStatus();
    
    if (res.code === 200 && res.data) {
      timeTurnerData.hasTimeTurner = res.data.has_time_turner;
      timeTurnerData.houseName = res.data.house_name;
      timeTurnerData.isTopHouse = res.data.is_top_house;
      
      if (timeTurnerData.hasTimeTurner) {
        createTimeTurnerTrigger();
        await loadActivities();
      }
    }
  } catch (err) {
    console.error('初始化时间转换器失败:', err);
  }
}

async function loadActivities() {
  try {
    const res = await getAllActivities();
    
    if (res.code === 200 && res.data) {
      timeTurnerData.activities = res.data;
    }
    
    const myRes = await getMyActivities();
    if (myRes.code === 200 && myRes.data) {
      timeTurnerData.myActivities = myRes.data;
    }
  } catch (err) {
    console.error('加载活动失败:', err);
  }
}

function createTimeTurnerTrigger() {
  const trigger = document.createElement('div');
  trigger.className = 'time-turner-trigger';
  trigger.innerHTML = '⏳';
  trigger.title = '时间转换器 - 点击选择活动';
  
  trigger.addEventListener('click', toggleTimeTurnerPanel);
  
  document.body.appendChild(trigger);
}

function toggleTimeTurnerPanel() {
  if (isPanelOpen) {
    closeTimeTurnerPanel();
  } else {
    openTimeTurnerPanel();
  }
}

function openTimeTurnerPanel() {
  if (isPanelOpen) return;
  isPanelOpen = true;
  
  if (!timeTurnerPanel) {
    createTimeTurnerPanel();
  }
  
  timeTurnerPanel.classList.add('show');
  updateActivitiesList();
}

function closeTimeTurnerPanel() {
  if (timeTurnerPanel) {
    timeTurnerPanel.classList.remove('show');
    isPanelOpen = false;
  }
}

function createTimeTurnerPanel() {
  timeTurnerPanel = document.createElement('div');
  timeTurnerPanel.className = 'time-turner-panel';
  
  timeTurnerPanel.innerHTML = `
    <div class="time-turner-header">
      <div class="time-turner-icon">⏳</div>
      <div class="time-turner-title">时间转换器</div>
      <div class="time-turner-subtitle">Time Turner</div>
      <button class="time-turner-close" id="closeTimeTurner">×</button>
    </div>
    <div class="time-turner-info">
      <div class="time-turner-badge">
        <span class="badge-icon">🏆</span>
        <span class="badge-text">${timeTurnerData.houseName} - 第一名</span>
      </div>
    </div>
    <div class="time-turner-divider"></div>
    <div class="time-turner-instruction">
      <p>🎯 拖动活动到课表中有课的时间段</p>
      <p class="instruction-note">活动时间将自动匹配课程时间</p>
    </div>
    <div class="time-turner-activities" id="timeTurnerActivities">
      <p class="loading-text">加载中...</p>
    </div>
  `;
  
  document.body.appendChild(timeTurnerPanel);
  
  const closeBtn = document.getElementById('closeTimeTurner');
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeTimeTurnerPanel();
    });
  }
  
  const header = timeTurnerPanel.querySelector('.time-turner-header');
  if (header) {
    header.addEventListener('mousedown', (e) => {
      if (e.target.id !== 'closeTimeTurner') {
        initDragPanel(e);
      }
    });
  }
}

function initDragPanel(e) {
  const panel = timeTurnerPanel;
  let isDragging = false;
  let startX, startY, initialX, initialY;
  
  startX = e.clientX;
  startY = e.clientY;
  
  const rect = panel.getBoundingClientRect();
  initialX = rect.left;
  initialY = rect.top;
  
  function onMouseMove(e) {
    const deltaX = e.clientX - startX;
    const deltaY = e.clientY - startY;
    
    if (!isDragging && (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5)) {
      isDragging = true;
      panel.style.transition = 'none';
    }
    
    if (isDragging) {
      let newX = initialX + deltaX;
      let newY = initialY + deltaY;
      
      newX = Math.max(0, Math.min(newX, window.innerWidth - panel.offsetWidth));
      newY = Math.max(0, Math.min(newY, window.innerHeight - panel.offsetHeight));
      
      panel.style.left = newX + 'px';
      panel.style.top = newY + 'px';
      panel.style.right = 'auto';
      panel.style.transform = 'none';
    }
  }
  
  function onMouseUp() {
    if (isDragging) {
      panel.style.transition = 'all 0.3s ease';
    }
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }
  
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
}

function updateActivitiesList() {
  const container = document.getElementById('timeTurnerActivities');
  if (!container) return;
  
  if (!timeTurnerData.activities || timeTurnerData.activities.length === 0) {
    container.innerHTML = '<p class="no-data">暂无可用活动</p>';
    return;
  }
  
  let html = '';
  timeTurnerData.activities.forEach(activity => {
    const duration = activity.suggested_duration ? `（建议${activity.suggested_duration}分钟）` : '';
    
    html += `
      <div class="time-turner-activity" 
           draggable="true"
           data-activity-id="${activity.activity_id}"
           data-activity-name="${activity.activity_name_cn}">
        <div class="activity-header">
          <span class="activity-icon">✨</span>
          <span class="activity-name">${activity.activity_name_cn}</span>
        </div>
        <div class="activity-info">
          📍 ${activity.location || '地点待定'} ${duration}
        </div>
        <div class="activity-desc">
          ${activity.description || ''}
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
  
  container.querySelectorAll('.time-turner-activity[draggable="true"]').forEach(el => {
    el.addEventListener('dragstart', handleActivityDragStart);
    el.addEventListener('dragend', handleActivityDragEnd);
  });
}

function handleActivityDragStart(e) {
  const activityId = e.target.dataset.activityId;
  const activityName = e.target.dataset.activityName;
  
  e.dataTransfer.setData('text/plain', JSON.stringify({
    type: 'activity',
    activityId: activityId,
    activityName: activityName
  }));
  
  e.target.classList.add('dragging');
  
  highlightDroppableCells();
}

function handleActivityDragEnd(e) {
  e.target.classList.remove('dragging');
  clearCellHighlights();
}

function highlightDroppableCells() {
  const cells = document.querySelectorAll('.schedule-table td.course-cell:not(.split-cell)');
  
  console.log('找到可放置的单元格数量:', cells.length);
  
  cells.forEach(cell => {
    cell.classList.add('drop-highlight');
    cell.addEventListener('dragover', handleDragOver);
    cell.addEventListener('drop', handleDrop);
    cell.addEventListener('dragleave', handleDragLeave);
  });
  
  const emptyCells = document.querySelectorAll('.schedule-table td.empty-cell');
  emptyCells.forEach(cell => {
    cell.classList.add('drop-reject');
  });
}

// 监听课程表加载完成事件，重新绑定拖拽事件
window.addEventListener('scheduleLoaded', () => {
  console.log('课程表加载完成，重新绑定拖拽事件');
  // 如果有正在拖拽的活动，重新高亮可放置的单元格
  const draggingActivity = document.querySelector('.time-turner-activity.dragging');
  if (draggingActivity) {
    highlightDroppableCells();
  }
});

function clearCellHighlights() {
  document.querySelectorAll('.drop-highlight, .drop-reject').forEach(cell => {
    cell.classList.remove('drop-highlight', 'drop-reject');
  });
  
  document.querySelectorAll('.schedule-table td').forEach(cell => {
    cell.removeEventListener('dragover', handleDragOver);
    cell.removeEventListener('drop', handleDrop);
    cell.removeEventListener('dragleave', handleDragLeave);
  });
}

function handleDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'copy';
  e.target.classList.add('drag-over');
}

function handleDragLeave(e) {
  e.target.classList.remove('drag-over');
}

async function handleDrop(e) {
  e.preventDefault();
  
  const data = JSON.parse(e.dataTransfer.getData('text/plain'));
  
  if (data.type !== 'activity') return;
  
  const cell = e.target.closest('td');
  console.log('拖拽目标元素:', e.target);
  console.log('找到的单元格:', cell);
  
  if (!cell) {
    UIToast.error('未找到目标单元格');
    return;
  }
  
  cell.classList.remove('drag-over');
  
  if (cell.classList.contains('empty-cell')) {
    UIToast.warning('时间转换器只能在有课的时间段使用！');
    return;
  }
  
  if (cell.classList.contains('split-cell')) {
    UIToast.warning('该时间段已经安排了活动！');
    return;
  }
  
  const weekday = parseInt(cell.dataset.weekday);
  const timeSlot = cell.dataset.time;
  
  console.log('单元格的 dataset:', cell.dataset);
  console.log('weekday:', weekday, 'timeSlot:', timeSlot);
  
  if (!weekday || !timeSlot) {
    UIToast.error('无法获取课程时间信息');
    return;
  }
  
  const startTime = timeSlot + ':00';
  const endTime = calculateEndTime(timeSlot);
  
  const requestData = {
    activity_id: parseInt(data.activityId),
    weekday: weekday,
    start_time: startTime,
    end_time: endTime
  };
  
  console.log('准备发送的数据:', JSON.stringify(requestData, null, 2));
  console.log('activityId:', data.activityId, '转换后:', parseInt(data.activityId));
  console.log('weekday:', weekday, '类型:', typeof weekday);
  console.log('start_time:', startTime, '类型:', typeof startTime);
  console.log('end_time:', endTime, '类型:', typeof endTime);
  
  try {
    UILoading.show();
    
    const res = await enrollActivity(requestData);
    
    if (res.code === 200) {
      UIToast.success(`成功选择活动「${data.activityName}」`);
      await loadMySchedule();
      await loadActivities();
    } else {
      UIToast.error(res.msg || '选择活动失败');
    }
  } catch (err) {
    console.error('选择活动失败:', err);
    UIToast.error('网络错误');
  } finally {
    UILoading.hide();
  }
}

function calculateEndTime(startTime) {
  const [hours, minutes] = startTime.split(':').map(Number);
  let endMinutes = minutes + 50;
  let endHours = hours;
  
  if (endMinutes >= 60) {
    endHours += 1;
    endMinutes -= 60;
  }
  
  return `${String(endHours).padStart(2, '0')}:${String(endMinutes).padStart(2, '0')}:00`;
}

async function cancelActivityFromCell(enrollmentId) {
  try {
    const res = await cancelActivityEnrollment(enrollmentId);
    
    if (res.code === 200) {
      UIToast.success('活动已取消');
      await loadMySchedule();
      await loadActivities();
    } else {
      UIToast.error(res.msg || '取消失败');
    }
  } catch (err) {
    console.error('取消活动失败:', err);
    UIToast.error('网络错误');
  }
}
