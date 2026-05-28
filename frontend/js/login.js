document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const submitBtn = document.getElementById('submitBtn');
  const btnText = document.getElementById('btnText');
  const errorMsg = document.getElementById('errorMsg');
  
  document.getElementById('usernameError').textContent = '';
  document.getElementById('passwordError').textContent = '';
  errorMsg.textContent = '';
  
  let isValid = true;
  
  if (!username) {
    document.getElementById('usernameError').textContent = '请输入用户名';
    isValid = false;
  }
  
  if (!password) {
    document.getElementById('passwordError').textContent = '请输入密码';
    isValid = false;
  }
  
  if (!isValid) return;
  
  submitBtn.disabled = true;
  btnText.textContent = '登录中...';
  
  try {
    const res = await login({ username, password });
    
    if (res.code === 200) {
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('role', res.data.role);
      localStorage.setItem('user_id', res.data.user_id);
      localStorage.setItem('username', username);
      if (res.data.house_id) {
        localStorage.setItem('house_id', res.data.house_id);
      }
      
      window.location.href = 'index.html';
    } else {
      errorMsg.textContent = res.msg || '登录失败，请重试';
    }
  } catch (err) {
    errorMsg.textContent = '网络错误，请检查连接';
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = '登录';
  }
});
