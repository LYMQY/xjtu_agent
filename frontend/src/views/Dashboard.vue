<template>
  <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
  </header>
  <div class="dashboard-container">
    <!-- 顶部 Banner -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">交小荣 Pro</h1>
        <p class="hero-subtitle">你的智能校园生活助手</p>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">6+</span>
            <span class="stat-label">核心功能</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">AI</span>
            <span class="stat-label">智能助手</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">24h</span>
            <span class="stat-label">随时服务</span>
          </div>
        </div>
      </div>
      <div class="hero-decoration">
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
        <div class="decoration-circle circle-3"></div>
      </div>
    </div>

    <!-- 功能卡片区域 -->
    <div class="features-section">
      <h2 class="section-title">功能服务</h2>
      <p class="section-desc">选择你想要使用的功能</p>
      
      <div class="features-grid">
        <div 
          v-for="feature in features" 
          :key="feature.id"
          class="feature-card"
          :class="{ 'featured': feature.featured }"
          @click="navigateTo(feature.path)"
        >
          <div class="feature-icon" :style="{ background: feature.gradient }">
            <el-icon :size="32"><component :is="feature.icon" /></el-icon>
          </div>
          <div class="feature-content">
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
          </div>
          <div class="feature-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="feature-badge" v-if="feature.badge">{{ feature.badge }}</div>
        </div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-section">
      <h2 class="section-title">快捷入口</h2>
      <div class="quick-links">
        <div 
          v-for="link in quickLinks" 
          :key="link.title"
          class="quick-link"
          @click="navigateTo(link.path)"
        >
          <div class="quick-icon" :style="{ background: link.gradient }">
            <el-icon :size="24"><component :is="link.icon" /></el-icon>
          </div>
          <span class="quick-text">{{ link.title }}</span>
        </div>
      </div>
    </div>

    <!-- 底部提示 -->
    <div class="tip-section">
      <el-icon><InfoFilled /></el-icon>
      <span>点击任意功能卡片即可开始使用，更多功能持续更新中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import HeaderView from '@/components/HeaderView.vue'
import { useRouter } from 'vue-router'
import { 
  ChatDotRound, Calendar, Wallet, FirstAidKit, MapLocation, 
  Document, ShoppingBag, MagicStick, ArrowRight, InfoFilled,
  Notebook, Coin, Timer, FirstAidKit as HealthIcon
} from '@element-plus/icons-vue'

const router = useRouter()

// 功能卡片数据
const features = [
  {
    id: 1,
    title: 'AI 智能助手',
    description: '基于 DeepSeek 的智能问答，解答学习、生活各类问题',
    icon: 'ChatDotRound',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    path: '/aiChat',
    featured: true,
    badge: '推荐'
  },
  {
    id: 2,
    title: '日程管理',
    description: '课程表、考试、活动提醒，一目了然',
    icon: 'Calendar',
    gradient: 'linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%)',
    path: '/calendar',
    badge: '必备'
  },
  {
    id: 3,
    title: '预算管理',
    description: '记账、预算设置、消费分析，帮你管好钱袋子',
    icon: 'Wallet',
    gradient: 'linear-gradient(135deg, #43E97B 0%, #38F9D7 100%)',
    path: '/budget'
  },
  {
    id: 4,
    title: '健康打卡',
    description: '每日健康记录、睡眠运动统计、养成好习惯',
    icon: 'FirstAidKit',
    gradient: 'linear-gradient(135deg, #FA709A 0%, #FEE140 100%)',
    path: '/health'
  },
  {
    id: 5,
    title: '旅游规划',
    description: 'AI 智能生成行程，旅行从此简单',
    icon: 'MapLocation',
    gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    path: '/travel'
  },
  {
    id: 6,
    title: '考试安排',
    description: '考试时间记录、复习计划、倒计时提醒',
    icon: 'Document',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    path: '/exam'
  },
  {
    id: 7,
    title: '二手市场',
    description: '校园闲置物品交易，省钱又环保',
    icon: 'ShoppingBag',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    path: '/market'
  },
  {
    id: 8,
    title: '选课推荐',
    description: '基于 RAG 的智能选课建议',
    icon: 'Notebook',
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    path: '/aiChat'
  }
]

// 快捷链接
const quickLinks = [
  { title: 'AI问答', icon: 'ChatDotRound', path: '/aiChat', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { title: '记一笔', icon: 'Coin', path: '/budget', gradient: 'linear-gradient(135deg, #43E97B 0%, #38F9D7 100%)' },
  { title: '打卡', icon: 'FirstAidKit', path: '/health', gradient: 'linear-gradient(135deg, #FA709A 0%, #FEE140 100%)' },
  { title: '查日程', icon: 'Timer', path: '/calendar', gradient: 'linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%)' },
  { title: '规划旅行', icon: 'MapLocation', path: '/travel', gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)' },
]

// 导航跳转
const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<style scoped lang="scss">
.dashboard-container {
  min-height: calc(100vh - 60px);
  background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  padding-bottom: 40px;
}

.hero-section {
  position: relative;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 60px 40px;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 32px;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .stat-number {
      font-size: 32px;
      font-weight: 700;
      color: #fff;
    }
    
    .stat-label {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 4px;
    }
  }
}

.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  
  .decoration-circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    
    &.circle-1 {
      width: 400px;
      height: 400px;
      background: #667eea;
      top: -100px;
      right: -100px;
      animation: float 8s ease-in-out infinite;
    }
    
    &.circle-2 {
      width: 300px;
      height: 300px;
      background: #764ba2;
      bottom: -50px;
      left: -50px;
      animation: float 6s ease-in-out infinite reverse;
    }
    
    &.circle-3 {
      width: 200px;
      height: 200px;
      background: #4facfe;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation: pulse 4s ease-in-out infinite;
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.1; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.15; }
}

.features-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  text-align: center;
  margin-bottom: 8px;
}

.section-desc {
  text-align: center;
  color: #666;
  margin-bottom: 32px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    
    .feature-arrow {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  &.featured {
    grid-column: span 2;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    .feature-title {
      color: #fff;
    }
    
    .feature-desc {
      color: rgba(255, 255, 255, 0.8);
    }
    
    .feature-icon {
      background: rgba(255, 255, 255, 0.2) !important;
    }
  }
  
  .feature-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 16px;
  }
  
  .feature-content {
    flex: 1;
  }
  
  .feature-title {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 8px;
  }
  
  .feature-desc {
    font-size: 14px;
    color: #666;
    line-height: 1.5;
  }
  
  .feature-arrow {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateX(10px);
    translate: y(-50%);
    color: #667eea;
    opacity: 0;
    transition: all 0.3s ease;
  }
  
  .feature-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 4px 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    font-size: 12px;
    border-radius: 12px;
    font-weight: 500;
  }
}

.quick-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.quick-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 24px;
}

.quick-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateY(-4px);
  }
  
  .quick-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .quick-text {
    font-size: 14px;
    color: #666;
  }
}

.tip-section {
  max-width: 1200px;
  margin: 24px auto 0;
  padding: 16px 24px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #999;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  .el-icon {
    color: #667eea;
  }
}

@media (max-width: 1200px) {
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .feature-card.featured {
    grid-column: span 2;
  }
}

@media (max-width: 600px) {
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .hero-stats {
    gap: 24px;
    
    .stat-item .stat-number {
      font-size: 24px;
    }
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-card.featured {
    grid-column: span 1;
  }
}
</style>
