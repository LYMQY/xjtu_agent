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
        <h1 class="hero-title">AI UniStudent</h1>
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
      
      <div class="features-carousel-wrapper">
        <el-carousel height="550px" :autoplay="false" indicator-position="outside" arrow="always">
          <el-carousel-item v-for="(group, index) in groupedFeatures" :key="index">
            <div class="features-grid">
              <div 
                v-for="feature in group" 
                :key="feature.id"
                class="feature-card"
                @click="navigateTo(feature.path)"
              >
                <p class="feature-example">{{ feature.example }}</p>
                <div class="feature-title-container">
                  <el-icon class="feature-icon"><component :is="feature.icon" /></el-icon>
                  <h3 class="feature-title">{{ feature.title }}</h3>
                </div>
                <el-button class="feature-button" circle @click.stop="navigateTo(feature.path)">
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
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
import { useRouter } from 'vue-router';
import { computed } from 'vue';
import { 
  ChatDotRound, Calendar, Wallet, FirstAidKit, MapLocation, 
  Document, ShoppingBag, MagicStick, ArrowRight, InfoFilled,
  Notebook, Coin, Timer, FirstAidKit as HealthIcon
} from '@element-plus/icons-vue'

const router = useRouter()

// 将功能分组，每组3个，用于轮播
const groupedFeatures = computed(() => {
  const result = [];
  for (let i = 0; i < features.length; i += 3) {
    result.push(features.slice(i, i + 3));
  }
  return result;
});

// 功能卡片数据
const features = [
  {
    id: 1,
    title: 'AI 智能助手',
    icon: 'ChatDotRound',
    example: '“帮我总结一下《百年孤独》的主要内容和主题思想。”“用Python写一个快速排序算法。”',
    path: '/aiChat',
  },
  {
    id: 2,
    title: '日程管理',
    icon: 'Calendar',
    example: '“提醒我明天下午三点在创新港有团队会议。”“下周五上午十点有高数考试。”',
    path: '/calendar',
  },
  {
    id: 3,
    title: '预算管理',
    icon: 'Wallet',
    example: '“记一笔支出，今天午饭在康桥吃的刀削面，花了12元。”“查询我这个月的餐饮消费总额。”',
    path: '/budget'
  },
  {
    id: 4,
    title: '健康助手',
    icon: 'FirstAidKit',
    example: '“我今天晚上睡眠质量怎么样？”“记录我今天跑步了3公里。”',
    path: '/health'
  },
  {
    id: 5,
    title: '旅游助手',
    icon: 'MapLocation',
    example: '“我想周末去趟壶口瀑布，帮我规划一个两天的行程。”“推荐一些西安本地的美食。”',
    path: '/travel'
  },
  {
    id: 6,
    title: '考试助手',
    icon: 'Document',
    example: '“我的大学物理期末考试在什么时候？帮我制定一个复习计划。”“距离四级考试还有多少天？”',
    path: '/exam'
  },
  {
    id: 7,
    title: '校园市场',
    icon: 'ShoppingBag',
    example: '“我想卖一本九成新的《C++ Primer》，应该标价多少？”“求购一个二手自行车。”',
    path: '/market'
  },
  {
    id: 8,
    title: '选课助手',
    icon: 'Notebook',
    example: '“我是计算机科学专业的，下学期有什么推荐的选修课吗？”“王老师的《数据结构》这门课怎么样？”',
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
  background: linear-gradient(135deg, #232344 0%, #16213e 50%, #0f3460 100%);
  padding: 60px 40px;
  overflow: hidden;
  height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
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
      animation: float 12s ease-in-out infinite;
    }
    
    &.circle-2 {
      width: 300px;
      height: 300px;
      background: #764ba2;
      bottom: -50px;
      left: -50px;
      animation: float 15s ease-in-out infinite reverse;
    }
    
    &.circle-3 {
      width: 200px;
      height: 200px;
      background: #4facfe;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation: pulse 6s ease-in-out infinite;
    }
  }
}

@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(-5deg); }
  50% { transform: translateY(-5px) rotate(5deg); }
  75% { transform: translateY(-25px) rotate(10deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.1; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.2; }
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
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  padding: 0 40px; /* 为轮播箭头留出空间 */
}

.features-carousel-wrapper {
  :deep(.el-carousel__item) {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  :deep(.el-carousel__arrow) {
    background-color: rgba(31, 45, 61, 0.5);
    color: white;
    &:hover {
      background-color: rgba(31, 45, 61, 0.8);
    }
  }
  :deep(.el-carousel__indicator.is-active button) {
    background-color: #667eea;
  }
}

.feature-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    
    .feature-button {
      transform: scale(1.1);
    }
  }

  .feature-example {
    font-size: 18px;
    color: #888;
    margin: 0;
    line-height: 1.6;
    text-align: center;
  }
  
  .feature-title-container {
    position: absolute;
    left: 32px;
    bottom: 28px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .feature-icon {
    font-size: 20px;
    color: #333;
  }
  
  .feature-title {
    font-size: 18px;
    font-weight: 600;
    color: #000;
    margin: 0;
  }
  
  .feature-button {
    position: absolute;
    right: 32px;
    bottom: 20px;
    background-color: #fff;
    border: 1px solid #000;
    color: #000;
    transition: transform 0.2s ease;

    &:hover {
      background-color: #f8f8f8;
      border-color: #000;
      color: #000;
    }
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
  
  /* The responsive styles for features-grid are no longer needed as it's a single column. */
}
</style>
