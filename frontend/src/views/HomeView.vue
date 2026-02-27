<template>
  <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
  </header>
  <div class="dashboard-page">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>你好，{{ username }}！👋</h1>
          <p>{{ greeting }}，今天也要加油鸭～ 有什么需要帮忙的吗？</p>
        </div>
        <div class="weather-widget">
          <el-icon :size="32"><Sunny /></el-icon>
          <div class="weather-info">
            <div class="temp">18°C</div>
            <div class="city">西安</div>
          </div>
        </div>
      </div>
      
      <!-- 快捷操作卡片 -->
      <div class="quick-cards">
        <div 
          v-for="card in quickCards" 
          :key="card.path"
          class="quick-card"
          :style="{ background: card.gradient }"
          @click="router.push(card.path)"
        >
          <div class="card-icon">
            <el-icon :size="28"><component :is="card.icon" /></el-icon>
          </div>
          <div class="card-content">
            <div class="card-title">{{ card.title }}</div>
            <div class="card-desc">{{ card.desc }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧列 -->
      <div class="left-column">
        <!-- 数据概览 -->
        <div class="stats-section">
          <h2 class="section-title">数据概览</h2>
          <div class="stats-grid">
            <div class="stat-card" @click="router.push('/calendar')">
              <div class="stat-icon" style="background: #E6F7FF; color: #1890FF;">
                <Calendar />
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.schedules }}</div>
                <div class="stat-label">本周日程</div>
              </div>
            </div>
            <div class="stat-card" @click="router.push('/budget')">
              <div class="stat-icon" style="background: #F6FFED; color: #52C41A;">
                <Wallet />
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ stats.balance }}</div>
                <div class="stat-label">本月预算</div>
              </div>
            </div>
            <div class="stat-card" @click="router.push('/health')">
              <div class="stat-icon" style="background: #FFF2F0; color: #FF4D4F;">
                <FirstAidKit />
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.healthDays }}</div>
                <div class="stat-label">打卡天数</div>
              </div>
            </div>
            <div class="stat-card" @click="router.push('/exam')">
              <div class="stat-icon" style="background: #F9F0FF; color: #722ED1;">
                <Document />
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.exams }}</div>
                <div class="stat-label">即将考试</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 最近活动 -->
        <div class="activity-section">
          <h2 class="section-title">最近动态</h2>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities" 
              :key="index"
              :icon="activity.icon"
              :type="activity.type"
              :timestamp="activity.time"
              placement="top"
            >
              <div class="activity-content">{{ activity.content }}</div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      
      <!-- 右侧列 -->
      <div class="right-column">
        <!-- AI 智能建议 -->
        <div class="ai-section">
          <h2 class="section-title">
            <el-icon><MagicStick /></el-icon>
            AI 建议
          </h2>
          <div class="suggestion-cards">
            <div 
              v-for="suggestion in aiSuggestions" 
              :key="suggestion.id"
              class="suggestion-card"
              @click="handleSuggestion(suggestion)"
            >
              <div class="suggestion-icon" :style="{ background: suggestion.gradient }">
                <el-icon :size="20"><component :is="suggestion.icon" /></el-icon>
              </div>
              <div class="suggestion-content">
                <div class="suggestion-title">{{ suggestion.title }}</div>
                <div class="suggestion-desc">{{ suggestion.description }}</div>
              </div>
              <el-icon class="arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
        
        <!-- 快捷功能 -->
        <div class="quick-section">
          <h2 class="section-title">快捷功能</h2>
          <div class="quick-grid">
            <div 
              v-for="func in quickFunctions" 
              :key="func.path"
              class="quick-func"
              @click="router.push(func.path)"
            >
              <div class="func-icon" :style="{ background: func.bg }">
                <el-icon :size="20" :color="func.color"><component :is="func.icon" /></el-icon>
              </div>
              <span>{{ func.name }}</span>
            </div>
          </div>
        </div>
        
        <!-- 日程预览 -->
        <div class="schedule-preview">
          <div class="section-header">
            <h2 class="section-title"> upcoming schedule</h2>
            <el-button type="primary" link @click="router.push('/calendar')">
              查看全部 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <div class="schedule-list" v-if="upcomingSchedules.length">
            <div 
              v-for="schedule in upcomingSchedules" 
              :key="schedule.id"
              class="schedule-item"
            >
              <div class="schedule-date">
                <div class="day">{{ schedule.day }}</div>
                <div class="month">{{ schedule.month }}</div>
              </div>
              <div class="schedule-info">
                <div class="schedule-name">{{ schedule.name }}</div>
                <div class="schedule-time">{{ schedule.time }}</div>
              </div>
              <div class="schedule-tag" :style="{ background: schedule.color + '20', color: schedule.color }">
                {{ schedule.tag }}
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无 upcoming schedule" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import HeaderView from "@/components/HeaderView.vue";
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Calendar, Wallet, FirstAidKit, Document, ChatDotRound, 
  ShoppingBag, MapLocation, MagicStick, Sunny, ArrowRight,
  Bell, Clock, Plus, Wallet as BudgetIcon
} from '@element-plus/icons-vue'
import { getToken } from '@/utils/auth'

const router = useRouter()
const username = ref('同学')

// 根据时间生成问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

// 快捷操作卡片
const quickCards = [
  { 
    title: 'AI 问答', 
    desc: '智能教务助手',
    icon: 'ChatDotRound',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    path: '/aiChat'
  },
  { 
    title: '创建日程', 
    desc: '安排你的时间',
    icon: 'Plus',
    gradient: 'linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%)',
    path: '/calendar'
  },
  { 
    title: '记一笔', 
    desc: '记录支出',
    icon: 'Wallet',
    gradient: 'linear-gradient(135deg, #43E97B 0%, #38F9D7 100%)',
    path: '/budget'
  },
  { 
    title: '健康打卡', 
    desc: '保持健康',
    icon: 'FirstAidKit',
    gradient: 'linear-gradient(135deg, #FA709A 0%, #FEE140 100%)',
    path: '/health'
  },
]

// 数据统计
const stats = ref({
  schedules: 5,
  balance: 1250,
  healthDays: 12,
  exams: 3
})

// 最近活动
const recentActivities = ref([
  { content: '完成了健康打卡', time: '10分钟前', icon: 'FirstAidKit', type: 'success' },
  { content: '新增日程：期末考试复习', time: '1小时前', icon: 'Calendar', type: 'primary' },
  { content: '餐饮支出 ¥25', time: '2小时前', icon: 'Wallet', type: 'warning' },
  { content: 'AI 推荐了选课建议', time: '昨天', icon: 'MagicStick', type: 'info' },
])

// AI 建议
const aiSuggestions = ref([
  { 
    id: 1, 
    title: '考试提醒', 
    description: '距离"数据结构"期末考还有7天',
    icon: 'Document',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    path: '/exam'
  },
  { 
    id: 2, 
    title: '预算提醒', 
    description: '本月餐饮支出已达预算的80%',
    icon: 'Wallet',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    path: '/budget'
  },
  { 
    id: 3, 
    title: '选课建议', 
    description: '下学期"计算机网络"推荐选修',
    icon: 'ChatDotRound',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    path: '/aiChat'
  },
])

// 快捷功能
const quickFunctions = [
  { name: '订外卖', icon: 'ShoppingBag', path: '/budget', bg: '#FFF2F0', color: '#FF4D4F' },
  { name: '查天气', icon: 'Sunny', path: 'https://www.weather.com.cn/', bg: '#E6F7FF', color: '#1890FF' },
  { name: '旅游规划', icon: 'MapLocation', path: '/travel', bg: '#F6FFED', color: '#52C41A' },
  { name: '校园二手', icon: 'ShoppingBag', path: '/market', bg: '#F9F0FF', color: '#722ED1' },
  { name: '考试安排', icon: 'Document', path: '/exam', bg: '#FFF7E6', color: '#FA8C16' },
  { name: '更多功能', icon: 'Plus', path: '/aiChat', bg: '#F0F7FF', color: '#3674FB' },
]

// upcoming schedule
const upcomingSchedules = ref([
  { id: '1', day: '28', month: '周五', name: '数据结构期末考试', time: '09:00-11:00', color: '#FF4D4F', tag: '考试' },
  { id: '2', day: '01', month: '周六', name: '课题组组会', time: '14:00-16:00', color: '#1890FF', tag: '会议' },
  { id: '3', day: '03', month: '周一', name: '体育课', time: '08:00-10:00', color: '#52C41A', tag: '课程' },
])

// 处理建议点击
const handleSuggestion = (suggestion: any) => {
  router.push(suggestion.path)
}

// 初始化
onMounted(() => {
  // 从 localStorage 获取用户名
  const storedUsername = localStorage.getItem('username')
  if (storedUsername) {
    username.value = storedUsername
  }
  
  // 加载数据统计
  loadStats()
})

// 加载统计数据
const loadStats = () => {
  // 这里可以从后端 API 获取实际数据
  // 暂时使用模拟数据
}
</script>

<style scoped lang="scss">
.dashboard-page {
  padding: 24px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0px;
  padding: 32px;
  margin-bottom: 24px;
  color: #fff;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.welcome-text {
  h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  
  p {
    font-size: 15px;
    opacity: 0.9;
  }
}

.weather-widget {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.2);
  padding: 12px 20px;
  border-radius: 12px;
  
  .weather-info {
    .temp {
      font-size: 20px;
      font-weight: 600;
    }
    .city {
      font-size: 12px;
      opacity: 0.8;
    }
  }
}

.quick-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.quick-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  
  .card-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #333;
    margin-right: 14px;
  }
  
  .card-title {
    font-size: 17px;
    font-weight: 600;
    color: #fff;
  }
  
  .card-desc {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 4px;
  }
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
  }
  
  .stat-value {
    font-size: 22px;
    font-weight: 600;
    color: #1a1a2e;
  }
  
  .stat-label {
    font-size: 13px;
    color: #999;
    margin-top: 4px;
  }
}

.activity-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .activity-content {
    font-size: 14px;
    color: #333;
  }
}

.ai-section,
.quick-section,
.schedule-preview {
  background: #F8FAFC;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.suggestion-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-card {
  display: flex;
  align-items: center;
  padding: 14px;
  background: #F8FAFC;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f0f7ff;
    transform: translateX(4px);
  }
  
  .suggestion-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-right: 12px;
  }
  
  .suggestion-content {
    flex: 1;
    
    .suggestion-title {
      font-weight: 600;
      color: #1a1a2e;
      font-size: 14px;
    }
    
    .suggestion-desc {
      font-size: 12px;
      color: #666;
      margin-top: 2px;
    }
  }
  
  .arrow {
    color: #ccc;
  }
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quick-func-wrapper {
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  display: flex;
  gap: 12px;
  padding-bottom: 10px;
  width: 100%;
  overflow: auto;
  scroll-behavior: smooth;
}

.quick-func {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  scroll-snap-align: start;
  
  &:hover {
    background: #f5f7fa;
  }
  
  .func-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
  }
  
  span {
    font-size: 12px;
    color: #666;
  }
}

.schedule-preview {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .section-title {
      margin-bottom: 0;
    }
  }
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f0f7ff;
  }
  
  .schedule-date {
    width: 44px;
    text-align: center;
    margin-right: 12px;
    
    .day {
      font-size: 20px;
      font-weight: 600;
      color: #1a1a2e;
    }
    .month {
      font-size: 12px;
      color: #999;
    }
  }
  
  .schedule-info {
    flex: 1;
    
    .schedule-name {
      font-size: 14px;
      font-weight: 500;
      color: #1a1a2e;
    }
    .schedule-time {
      font-size: 12px;
      color: #999;
      margin-top: 2px;
    }
  }
  
  .schedule-tag {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .quick-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .quick-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-content {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
