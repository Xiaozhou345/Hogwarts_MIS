const roleSelect = document.getElementById('role');
const houseGroup = document.getElementById('houseGroup');

roleSelect.addEventListener('change', () => {
  if (roleSelect.value === '0') {
    houseGroup.style.display = 'block';
  } else {
    houseGroup.style.display = 'none';
    document.getElementById('house_id').value = '';
    document.getElementById('houseError').textContent = '';
  }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const role = document.getElementById('role').value;
  const house_id = document.getElementById('house_id').value;
  
  const submitBtn = document.getElementById('submitBtn');
  const btnText = document.getElementById('btnText');
  const errorMsg = document.getElementById('errorMsg');
  const successMsg = document.getElementById('successMsg');
  
  document.getElementById('usernameError').textContent = '';
  document.getElementById('passwordError').textContent = '';
  document.getElementById('confirmPasswordError').textContent = '';
  document.getElementById('roleError').textContent = '';
  document.getElementById('houseError').textContent = '';
  errorMsg.textContent = '';
  successMsg.textContent = '';
  
  let isValid = true;
  
  if (!username) {
    document.getElementById('usernameError').textContent = '请输入用户名';
    isValid = false;
  } else if (username.length < 3) {
    document.getElementById('usernameError').textContent = '用户名至少3个字符';
    isValid = false;
  }
  
  if (!password) {
    document.getElementById('passwordError').textContent = '请输入密码';
    isValid = false;
  } else if (password.length < 6) {
    document.getElementById('passwordError').textContent = '密码至少6个字符';
    isValid = false;
  }
  
  if (password !== confirmPassword) {
    document.getElementById('confirmPasswordError').textContent = '两次密码不一致';
    isValid = false;
  }
  
  if (!role) {
    document.getElementById('roleError').textContent = '请选择角色';
    isValid = false;
  }
  
  if (role === '0' && !house_id) {
    document.getElementById('houseError').textContent = '请选择所属学院';
    isValid = false;
  }
  
  if (!isValid) return;
  
  submitBtn.disabled = true;
  btnText.textContent = '注册中...';
  
  try {
    const data = {
      username,
      password,
      role: parseInt(role)
    };
    
    if (role === '0') {
      data.house_id = parseInt(house_id);
    }
    
    const res = await register(data);
    
    if (res.code === 200) {
      successMsg.textContent = '注册成功！即将跳转到登录页面...';
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 1500);
    } else {
      errorMsg.textContent = res.msg || '注册失败，请重试';
    }
  } catch (err) {
    errorMsg.textContent = '网络错误，请检查连接';
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = '注册';
  }
});
