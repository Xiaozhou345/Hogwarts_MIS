const API_BASE_URL = 'http://localhost:5000/api';

async function request(url, options = {}) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers
    });
    
    const data = await response.json();
    
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('username');
      localStorage.removeItem('house_id');
      window.location.href = 'login.html';
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

async function login(data) {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function register(data) {
  return request('/register', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function logout() {
  return request('/logout', {
    method: 'POST'
  });
}

async function getStudents() {
  return request('/students', {
    method: 'GET'
  });
}

async function submitPoints(data) {
  return request('/points', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function getProfessorLogs() {
  return request('/professor/logs', {
    method: 'GET'
  });
}

async function getStudentInfo() {
  return request('/student/info', {
    method: 'GET'
  });
}

async function getStudentLogs() {
  return request('/student/logs', {
    method: 'GET'
  });
}

async function getHouseRanking() {
  return request('/house/ranking', {
    method: 'GET'
  });
}

async function getPublicLogs() {
  return request('/public/logs', {
    method: 'GET'
  });
}

async function createCourse(data) {
  return request('/professor/course', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function getProfessorCourses() {
  return request('/professor/courses', {
    method: 'GET'
  });
}

async function updateCourse(courseId, data) {
  return request(`/professor/course/${courseId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

async function deleteCourse(courseId) {
  return request(`/professor/course/${courseId}`, {
    method: 'DELETE'
  });
}

async function addCourseSchedule(courseId, data) {
  return request(`/professor/course/${courseId}/schedule`, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function getCourseSchedule(courseId) {
  return request(`/professor/course/${courseId}/schedule`, {
    method: 'GET'
  });
}

async function deleteSchedule(scheduleId) {
  return request(`/professor/schedule/${scheduleId}`, {
    method: 'DELETE'
  });
}

async function getEnrolledStudents(courseId) {
  return request(`/professor/course/${courseId}/students`, {
    method: 'GET'
  });
}

async function recordClassPerformance(data) {
  return request('/professor/class-performance', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function getCoursePerformances(courseId) {
  return request(`/professor/course/${courseId}/performances`, {
    method: 'GET'
  });
}

async function getAvailableCourses() {
  return request('/student/courses/available', {
    method: 'GET'
  });
}

async function getCourseDetail(courseId) {
  return request(`/student/course/${courseId}`, {
    method: 'GET'
  });
}

async function enrollCourse(data) {
  return request('/student/enroll', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function dropCourse(enrollmentId) {
  return request(`/student/enroll/${enrollmentId}`, {
    method: 'DELETE'
  });
}

async function getMyCourses() {
  return request('/student/my-courses', {
    method: 'GET'
  });
}

async function getMySchedule() {
  return request('/student/schedule', {
    method: 'GET'
  });
}

async function getMyPerformances() {
  return request('/student/my-performances', {
    method: 'GET'
  });
}

async function getAllCourses() {
  return request('/public/courses', {
    method: 'GET'
  });
}

async function getPopularCourses() {
  return request('/public/courses/popular', {
    method: 'GET'
  });
}

async function getHouseCourseStats() {
  return request('/public/courses/house-stats', {
    method: 'GET'
  });
}
