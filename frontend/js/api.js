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
