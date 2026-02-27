<script lang="ts" setup>
import { useRouter, useRoute } from "vue-router";
import { ChatDotRound, User, ArrowDown, Wallet, Calendar, FirstAidKit, MapLocation } from "@element-plus/icons-vue";
import { ref } from "vue";
import { ElMessage } from "element-plus";

const router = useRouter();
const route = useRoute();
const isLoggedIn = ref(false); // 示例登录状态

// 判断当前路由是否激活
const isActive = (path: string) => {
  return route.path === path;
};

// 点击logo 的处理
const logoImgClickHandle = () => {
  window.location.href = "https://www.xjtu.edu.cn/";
};

// 点击导航菜单 的处理
const navClickHandle = () => {
  router.push("/aiChat");
};

// 登录/登出处理
const handleLogin = (command?: string) => {
  if (!isLoggedIn.value) {
    // 处理登录逻辑
    router.push("/login"); // 假设登录路由为/login
  }
};
</script>

<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo区域 - 替换为交小荣logo.svg -->
        <div class="logo-container" @click="logoImgClickHandle">
          <el-image
            src="/logoo.png"  
            class="logo-image"
            fit="contain"
            alt="交小荣Logo"
          />
          <span class="logo-text">AI UniStudent</span>
        </div>
        
        <!-- 导航区域 - 调整结构确保横向排列 -->
        <nav class="nav-container">
          <div class="nav-list">
            <span 
              class="nav-item" 
              @click="router.push('/aiChat')"
              :class="{ 'active': isActive('/aiChat') }"
            >
              <el-icon class="nav-icon">
                <ChatDotRound />
              </el-icon>
              <span>AI助手</span>
            </span>
            
            <span 
              class="nav-item" 
              @click="router.push('/calendar')"
              :class="{ 'active': isActive('/calendar') }"
            >
              <el-icon class="nav-icon">
                <Calendar />
              </el-icon>
              <span>日程管理</span>
            </span>
            
            <span 
              class="nav-item" 
              @click="router.push('/budget')"
              :class="{ 'active': isActive('/budget') }"
            >
              <el-icon class="nav-icon">
                <Wallet />
              </el-icon>
              <span>预算管理</span>
            </span>
            
            <span 
              class="nav-item" 
              @click="router.push('/health')"
              :class="{ 'active': isActive('/health') }"
            >
              <el-icon class="nav-icon">
                <FirstAidKit />
              </el-icon>
              <span>健康助手</span>
            </span>
            
            <span 
              class="nav-item" 
              @click="router.push('/travel')"
              :class="{ 'active': isActive('/travel') }"
            >
              <el-icon class="nav-icon">
                <MapLocation />
              </el-icon>
              <span>旅游助手</span>
            </span>
          </div>
        </nav>
        
        <!-- 登录按钮 -->
        <div class="login-container">
          <el-button
            v-if="!isLoggedIn"
            type="primary"
            @click="handleLogin"
            class="login-btn"
          >
            <el-icon><User /></el-icon>
            <span>登录</span>
          </el-button>
        </div>
      </div>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.page-header {
  background-color: rgba($color: #ffffff, $alpha: 0.5);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 12px 0; /* 稍微调整内边距以适应logo尺寸 */
  position: sticky;
  top: 0;
  z-index: 100;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px; /* 增加元素间距，避免拥挤 */
  }
  
  // Logo区域 - 调整样式以适应svg logo
  .logo-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: transform 0.2s ease;
    flex-shrink: 0; /* 防止logo被挤压 */
    
    &:hover {
      transform: scale(1.02);
    }
    
    .logo-image {
      height: 44px; /* 适当调整logo高度 */
      width: auto;
      margin-left: -80px;
    }
  }
  
  // 导航区域 - 核心修改：确保横向排列
  .nav-container {
    flex: 1; /* 让导航区域占满中间空间 */
    .nav-list {
      display: flex; /* 关键：设置flex实现横向排列 */
      justify-content: center; /* 导航项居中对齐 */
      align-items: center;
      gap: 8px; /* 导航项之间的间距 */
      width: 100%;
    }
    
    .nav-item {
      display: flex;
      align-items: center;
      padding: 8px 15px;
      border-radius: 6px;
      transition: all 0.2s ease;
      color: #000000;
      cursor: pointer;
      white-space: nowrap; /* 防止文字换行 */
      
      &:hover {
        background-color: #f5f7fa;
        color: #409eff;
      }
      
      &.active {
        background-color: #e6f4ff;
        color: #165dff;
      }
      
      .nav-icon {
        margin-right: 8px;
        font-size: 18px;
      }
    }
  }
  
  // 登录区域
  .login-container {
    flex-shrink: 0; /* 防止登录按钮被挤压 */
    .login-btn {
      display: flex;
      align-items: center;
      height: 36px;
      border-radius: 6px;
      transition: all 0.2s ease;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(64, 158, 255, 0.3);
      }
      
      .el-icon {
        margin-right: 5px;
      }
    }
    
    .user-btn {
      display: flex;
      align-items: center;
      color: #606266;
      
      .user-name {
        margin: 0 5px;
      }
    }
  }
}

.logo-container {
  display: flex; /* 使用Flex布局 */
  align-items: center; /* 垂直居中对齐 */
  gap: 8px; /* 图片和文本之间的间距 */
}

.logo-text {
  font-size: 25px; /* 调整字体大小 */
  font-weight: bold; /* 加粗 */
  color: #86c8f1; /* 文本颜色 */
}

// 响应式设计 - 适配小屏幕
@media (max-width: 992px) {
  .page-header {
    .nav-container .nav-item {
      padding: 8px 10px;
      
      .nav-icon {
        margin-right: 4px;
        font-size: 16px;
      }
      
      span {
        font-size: 14px;
      }
    }
  }
}

@media (max-width: 768px) {
  .page-header {
    .logo-text {
      font-size: 18px;
    }
    
    .nav-container .nav-item span {
      display: none; /* 小屏幕隐藏文字，只显示图标 */
    }
    
    .nav-container .nav-item .nav-icon {
      margin-right: 0;
    }
  }
}
</style>