<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-left">
        <div class="welcome-text">
          <h2>Server Monitor System</h2>
          <p>实时监控 · 精准告警 · 数据回溯</p>
        </div>
        <div class="monitor-illustration">
          <!-- 简单的CSS绘图示意服务器监控 -->
          <div class="chart-mock">
            <div class="bar bar-1"></div>
            <div class="bar bar-2"></div>
            <div class="bar bar-3"></div>
            <div class="bar bar-4"></div>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-box">
          <div class="header">
            <h3>欢迎回来</h3>
            <p>请登录您的管理员账号</p>
          </div>
          
          <el-form 
            ref="formRef"
            :model="loginForm"
            :rules="rules"
            @submit.prevent
            size="large"
          >
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名" 
                :prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码" 
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                class="login-btn" 
                :loading="loading" 
                @click="handleLogin" 
                round
              >
                {{ loading ? '登录中...' : '立即登录' }}
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="footer-tip">
            <span>没有账号？请联系系统管理员</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
})

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await authStore.login(loginForm)
        
        if (result.success) {
          ElMessage.success('登录成功，欢迎回来！')
          router.push('/home')
        } else {
          ElMessage.error(result.message || '登录失败，请检查用户名或密码')
        }
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error(error.message || '网络连接失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  if (authStore.token && authStore.user) {
    router.push('/home')
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.login-wrapper {
  display: flex;
  width: 900px;
  height: 550px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  padding: 40px;
  position: relative;
}

.welcome-text {
  text-align: center;
  z-index: 2;
  margin-bottom: 40px;
}

.welcome-text h2 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.welcome-text p {
  font-size: 14px;
  opacity: 0.9;
  letter-spacing: 2px;
}

.monitor-illustration {
  width: 200px;
  height: 160px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-mock {
  display: flex;
  gap: 15px;
  align-items: flex-end;
}

.bar {
  width: 20px;
  background: white;
  border-radius: 3px;
  animation: heightChange 2s infinite ease-in-out alternate;
}

.bar-1 { height: 40px; animation-delay: 0s; }
.bar-2 { height: 70px; animation-delay: 0.2s; }
.bar-3 { height: 50px; animation-delay: 0.4s; }
.bar-4 { height: 90px; animation-delay: 0.6s; }

@keyframes heightChange {
  from { transform: scaleY(0.8); opacity: 0.7; }
  to { transform: scaleY(1.2); opacity: 1; }
}

.login-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.login-box {
  width: 320px;
}

.header {
  margin-bottom: 35px;
}

.header h3 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.header p {
  color: #999;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  margin-top: 10px;
  box-shadow: 0 4px 15px rgba(24, 144, 255, 0.3);
  transition: all 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4);
}

.footer-tip {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #bbb;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .login-wrapper {
    width: 90%;
    flex-direction: column;
    height: auto;
  }
  
  .login-left {
    display: none; /* 移动端隐藏左侧装饰 */
  }
  
  .login-right {
    padding: 40px 20px;
  }
}
</style>

