const UILoading = {
  overlay: null,
  count: 0,
  
  init() {
    if (!this.overlay) {
      this.overlay = document.createElement('div');
      this.overlay.className = 'loading-overlay';
      this.overlay.innerHTML = `
        <div class="loading-content">
          <div class="loading-spinner"></div>
          <div class="loading-text">加载中...</div>
        </div>
      `;
      document.body.appendChild(this.overlay);
    }
  },
  
  show() {
    this.init();
    this.count++;
    this.overlay.classList.add('show');
  },
  
  hide() {
    this.count--;
    if (this.count <= 0) {
      this.count = 0;
      if (this.overlay) {
        this.overlay.classList.remove('show');
      }
    }
  },
  
  forceHide() {
    this.count = 0;
    if (this.overlay) {
      this.overlay.classList.remove('show');
    }
  }
};

const UIToast = {
  container: null,
  
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  
  show(message, type = 'info', duration = 3000) {
    this.init();
    
    const icons = {
      success: '✓',
      error: '✗',
      warning: '⚠',
      info: 'ℹ'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type]}</span>
      <span class="toast-message">${message}</span>
    `;
    
    this.container.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, duration);
  },
  
  success(message, duration = 3000) {
    this.show(message, 'success', duration);
  },
  
  error(message, duration = 3000) {
    this.show(message, 'error', duration);
  },
  
  warning(message, duration = 3000) {
    this.show(message, 'warning', duration);
  },
  
  info(message, duration = 3000) {
    this.show(message, 'info', duration);
  }
};

const UIConfirm = {
  overlay: null,
  
  init() {
    if (!this.overlay) {
      this.overlay = document.createElement('div');
      this.overlay.className = 'confirm-overlay';
      document.body.appendChild(this.overlay);
    }
  },
  
  show(options) {
    this.init();
    
    const {
      title = '确认操作',
      message = '',
      confirmText = '确定',
      cancelText = '取消',
      type = 'default',
      icon = '⚠️'
    } = options;
    
    return new Promise((resolve) => {
      const confirmBtnClass = type === 'danger' ? 'danger' : 'confirm';
      
      this.overlay.innerHTML = `
        <div class="confirm-dialog">
          <div class="confirm-icon">${icon}</div>
          <div class="confirm-title">${title}</div>
          <div class="confirm-message">${message}</div>
          <div class="confirm-actions">
            <button class="confirm-btn cancel">${cancelText}</button>
            <button class="confirm-btn ${confirmBtnClass}">${confirmText}</button>
          </div>
        </div>
      `;
      
      this.overlay.classList.add('show');
      
      const cancelBtn = this.overlay.querySelector('.confirm-btn.cancel');
      const confirmBtn = this.overlay.querySelector(`.confirm-btn.${confirmBtnClass}`);
      
      const close = (result) => {
        this.overlay.classList.remove('show');
        resolve(result);
      };
      
      cancelBtn.addEventListener('click', () => close(false));
      confirmBtn.addEventListener('click', () => close(true));
      
      this.overlay.addEventListener('click', (e) => {
        if (e.target === this.overlay) {
          close(false);
        }
      });
    });
  },
  
  async confirm(message, title = '确认操作') {
    return this.show({
      title,
      message,
      confirmText: '确定',
      cancelText: '取消',
      icon: '⚠️'
    });
  },
  
  async delete(itemName, title = '确认删除') {
    return this.show({
      title,
      message: `确定要删除"${itemName}"吗？此操作不可撤销！`,
      confirmText: '删除',
      cancelText: '取消',
      type: 'danger',
      icon: '🗑️'
    });
  },
  
  async enroll(courseName) {
    return this.show({
      title: '确认选课',
      message: `确定要选修《${courseName}》吗？`,
      confirmText: '选课',
      cancelText: '取消',
      icon: '📚'
    });
  },
  
  async drop(courseName) {
    return this.show({
      title: '确认退课',
      message: `确定要退选《${courseName}》吗？`,
      confirmText: '退课',
      cancelText: '取消',
      type: 'danger',
      icon: '📚'
    });
  }
};

const courseColors = {
  1: { bg: 'rgba(116, 0, 1, 0.25)', border: '#740001', name: '格兰芬多红' },
  2: { bg: 'rgba(26, 71, 42, 0.25)', border: '#1A472A', name: '斯莱特林绿' },
  3: { bg: 'rgba(14, 26, 64, 0.25)', border: '#0E1A40', name: '拉文克劳蓝' },
  4: { bg: 'rgba(55, 46, 41, 0.25)', border: '#372E29', name: '赫奇帕奇棕' },
  5: { bg: 'rgba(212, 175, 55, 0.25)', border: '#d4af37', name: '金色' },
  6: { bg: 'rgba(176, 138, 104, 0.25)', border: '#B08A68', name: '古铜色' },
  7: { bg: 'rgba(170, 170, 170, 0.25)', border: '#AAAAAA', name: '银色' },
  8: { bg: 'rgba(128, 0, 128, 0.25)', border: '#800080', name: '紫色' }
};

const CourseColorManager = {
  customColors: {},
  
  init() {
    const saved = localStorage.getItem('courseColors');
    if (saved) {
      try {
        this.customColors = JSON.parse(saved);
      } catch (e) {
        this.customColors = {};
      }
    }
  },
  
  save() {
    localStorage.setItem('courseColors', JSON.stringify(this.customColors));
  },
  
  getColor(courseName, courseId) {
    const key = courseName || `course_${courseId}`;
    
    if (this.customColors[key]) {
      console.log(`获取颜色: 课程="${key}", 使用自定义颜色:`, JSON.stringify(this.customColors[key]));
      return this.customColors[key];
    }
    
    const safeId = courseId || 1;
    const colorIndex = ((safeId - 1) % 8) + 1;
    console.log(`获取颜色: 课程="${key}", 使用默认颜色索引=${colorIndex}`);
    return courseColors[colorIndex];
  },
  
  setColor(courseName, colorIndex) {
    const key = courseName;
    console.log(`设置颜色: 课程="${key}", 颜色索引=${colorIndex}`);
    console.log('颜色对象:', JSON.stringify(courseColors[colorIndex]));
    this.customColors[key] = courseColors[colorIndex];
    this.save();
    console.log('保存后的颜色配置:', JSON.stringify(this.customColors));
  },
  
  resetColor(courseName) {
    delete this.customColors[courseName];
    this.save();
  },
  
  getCurrentColorIndex(courseName, courseId) {
    const key = courseName || `course_${courseId}`;
    
    if (this.customColors[key]) {
      for (let i = 1; i <= 8; i++) {
        if (courseColors[i].bg === this.customColors[key].bg) {
          return i;
        }
      }
    }
    
    return ((courseId - 1) % 8) + 1;
  },
  
  showColorPicker(courseName, currentColorIndex) {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.className = 'confirm-overlay show';
      
      let colorOptions = '';
      for (let i = 1; i <= 8; i++) {
        const color = courseColors[i];
        const selected = i === currentColorIndex ? 'border: 3px solid #000;' : '';
        colorOptions += `
          <div class="color-option" data-index="${i}" style="
            width: 50px;
            height: 50px;
            background: ${color.bg};
            border-left: 4px solid ${color.border};
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            ${selected}
          " title="${color.name}"></div>
        `;
      }
      
      overlay.innerHTML = `
        <div class="confirm-dialog" style="max-width: 500px;">
          <div class="confirm-icon">🎨</div>
          <div class="confirm-title">选择课程颜色</div>
          <div class="confirm-message">为《${courseName}》选择显示颜色</div>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0;">
            ${colorOptions}
          </div>
          <div class="confirm-actions">
            <button class="confirm-btn cancel">取消</button>
            <button class="confirm-btn confirm" id="resetColorBtn" style="background: rgba(184, 149, 110, 0.3); border: 2px solid var(--parchment-border);">重置默认</button>
            <button class="confirm-btn confirm" id="confirmColorBtn">确认</button>
          </div>
        </div>
      `;
      
      document.body.appendChild(overlay);
      
      let selectedColor = currentColorIndex;
      
      overlay.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', () => {
          overlay.querySelectorAll('.color-option').forEach(o => {
            o.style.border = 'none';
            o.style.borderLeft = `4px solid ${courseColors[o.dataset.index].border}`;
          });
          option.style.border = '3px solid #000';
          selectedColor = parseInt(option.dataset.index);
        });
        
        option.addEventListener('mouseenter', () => {
          option.style.transform = 'scale(1.1)';
        });
        
        option.addEventListener('mouseleave', () => {
          option.style.transform = 'scale(1)';
        });
      });
      
      overlay.querySelector('.confirm-btn.cancel').addEventListener('click', () => {
        document.body.removeChild(overlay);
        resolve(null);
      });
      
      overlay.querySelector('#resetColorBtn').addEventListener('click', () => {
        document.body.removeChild(overlay);
        resolve('reset');
      });
      
      overlay.querySelector('#confirmColorBtn').addEventListener('click', () => {
        document.body.removeChild(overlay);
        resolve(selectedColor);
      });
      
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          document.body.removeChild(overlay);
          resolve(null);
        }
      });
      
      setTimeout(() => {
        overlay.querySelector('.confirm-dialog').addEventListener('click', (e) => {
          e.stopPropagation();
        });
      }, 0);
    });
  }
};

CourseColorManager.init();

function getCourseColorClass(courseId) {
  const colorIndex = ((courseId - 1) % 8) + 1;
  return `course-color-${colorIndex}`;
}

function getCourseColorStyle(courseId, courseName) {
  return CourseColorManager.getColor(courseName, courseId);
}
