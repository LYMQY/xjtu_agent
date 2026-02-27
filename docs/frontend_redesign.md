# 交小荣生活助手 Pro - 前端界面设计方案

## 一、整体设计理念

- **设计风格**: 清新、简约、充满活力的校园风
- **配色方案**: 
  - 主色: `#3674FB` (交大蓝)
  - 辅色: `#6BB3FF` (浅蓝)
  - 强调色: `#FF6B6B` (珊瑚红) / `#4ECDC4` (薄荷绿) / `#FFE66D` (阳光黄)
  - 背景: `#F8FAFC` (浅灰白)
- **布局**: 侧边栏导航 + 主内容区 (类似 dashboard 布局)

---

## 二、页面结构规划

```
┌─────────────────────────────────────────────────────────────────┐
│                         顶部 Header                              │
│  [Logo]  搜索栏                    [通知] [用户头像 ▼]           │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│  侧边栏   │                    主内容区                          │
│          │                                                      │
│ ┌──────┐ │  ┌─────────────────────────────────────────────┐   │
│ │ 首页  │ │  │                                             │   │
│ └──────┘ │  │           动态内容区域                         │   │
│ ┌──────┐ │  │                                             │   │
│ │ AI   │ │  │                                             │   │
│ │ 助手  │ │  └─────────────────────────────────────────────┘   │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 日程  │ │                                                      │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 预算  │ │                                                      │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 健康  │ │                                                      │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 旅游  │ │                                                      │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 考试  │ │                                                      │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 二手  │ │                                                      │
│ └──────┘ │                                                      │
│ ┌──────┐ │                                                      │
│ │ 选课  │ │                                                      │
│ └──────┘ │                                                      │
│          │                                                      │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## 三、核心页面设计

### 1. 新导航栏 (HeaderView.vue 改进版)

```vue
<template>
  <header class="main-header">
    <div class="header-left">
      <!-- Logo -->
      <div class="logo" @click="goHome">
        <img src="/logo.png" alt="交小荣" />
        <span class="logo-text">交小荣 Pro</span>
      </div>
      
      <!-- 全局搜索栏 -->
      <div class="search-box">
        <el-input
          v-model="globalSearch"
          placeholder="搜索功能、问题或帮助..."
          prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
        />
      </div>
    </div>
    
    <div class="header-right">
      <!-- 快捷功能按钮 -->
      <div class="quick-actions">
        <el-tooltip content="创建日程" placement="bottom">
          <el-button :icon="Plus" circle @click="quickAddSchedule" />
        </el-tooltip>
        <el-badge :value="notificationCount" :hidden="notificationCount === 0">
          <el-button :icon="Bell" circle @click="showNotifications" />
        </el-badge>
      </div>
      
      <!-- 用户菜单 -->
      <el-dropdown @command="handleUserCommand">
        <div class="user-info">
          <el-avatar :size="36" :src="userAvatar">
            {{ username?.charAt(0) }}
          </el-avatar>
          <span class="username">{{ username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="settings">设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>
```

**样式特点**:
- 固定顶部，白色背景 + 微妙阴影
- 搜索栏居中，突出全局搜索能力
- 快捷操作按钮 + 用户头像并排

---

### 2. 侧边栏导航 (新增 Sidebar.vue)

```vue
<template>
  <aside class="main-sidebar" :class="{ collapsed: isCollapsed }">
    <!-- 折叠按钮 -->
    <div class="collapse-btn" @click="toggleSidebar">
      <el-icon><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
    </div>
    
    <!-- 导航菜单 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapsed"
      :collapse-transition="false"
      router
    >
      <!-- 首页 -->
      <el-menu-item index="/dashboard">
        <el-icon><HomeFilled /></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      
      <!-- AI 助手 (展开子菜单) -->
      <el-sub-menu index="/ai">
        <template #title>
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 助手</span>
        </template>
        <el-menu-item index="/ai/chat">智能问答</el-menu-item>
        <el-menu-item index="/ai/courses">选课推荐</el-menu-item>
      </el-sub-menu>
      
      <!-- 日程管理 -->
      <el-menu-item index="/calendar">
        <el-icon><Calendar /></el-icon>
        <template #title>日程管理</template>
      </el-menu-item>
      
      <!-- 预算管理 -->
      <el-menu-item index="/budget">
        <el-icon><Wallet /></el-icon>
        <template #title>预算管理</template>
      </el-menu-item>
      
      <!-- 健康打卡 -->
      <el-menu-item index="/health">
        <el-icon><FirstAidKit /></el-icon>
        <template #title>健康打卡</template>
      </el-menu-item>
      
      <!-- 旅游规划 -->
      <el-menu-item index="/travel">
        <el-icon><MapLocation /></el-icon>
        <template #title>旅游规划</template>
      </el-menu-item>
      
      <!-- 考试安排 -->
      <el-menu-item index="/exam">
        <el-icon><Document /></el-icon>
        <template #title>考试安排</template>
      </el-menu-item>
      
      <!-- 二手市场 -->
      <el-menu-item index="/market">
        <el-icon><ShoppingBag /></el-icon>
        <template #title>二手市场</template>
      </el-menu-item>
    </el-menu>
    
    <!-- 底部信息 -->
    <div class="sidebar-footer" v-if="!isCollapsed">
      <div class="version">v2.0.0</div>
    </div>
  </aside>
</template>

<style scoped>
.main-sidebar {
  width: 220px;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 60px;
  z-index: 100;
  transition: width 0.3s;
  overflow-y: auto;
}

.main-sidebar.collapsed {
  width: 64px;
}

/* 菜单样式 */
:deep(.el-menu) {
  border-right: none;
  background: transparent;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 8px;
  border-radius: 8px;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: rgba(54, 116, 251, 0.2);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #3674FB 0%, #6BB3FF 100%);
  color: #fff;
}
</style>
```

**设计特点**:
- 深色渐变背景，突显专业感
- 支持折叠，节省空间
- 菜单图标使用圆角图标，视觉效果更好

---

### 3. 首页仪表盘 (Dashboard.vue 改进版)

```vue
<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>你好，{{ username }}！👋</h1>
        <p>今天也要加油鸭～ 有什么需要帮忙的吗？</p>
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
    
    <!-- 数据概览 -->
    <div class="stats-section">
      <h2 class="section-title">数据概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6F7FF; color: #1890FF;">
            <Calendar />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.schedules }}</div>
            <div class="stat-label">本周日程</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: #F6FFED; color: #52C41A;">
            <Wallet />
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.balance }}</div>
            <div class="stat-label">本月预算</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF2F0; color: #FF4D4F;">
            <FirstAidKit />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.healthDays }}</div>
            <div class="stat-label">打卡天数</div>
          </div>
        </div>
        <div class="stat-card">
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
    
    <!-- 最近活动 & AI 建议 -->
    <div class="content-section">
      <!-- 最近活动 -->
      <div class="recent-activity">
        <h2 class="section-title">最近活动</h2>
        <el-timeline>
          <el-timeline-item
            v-for="(activity, index) in recentActivities"
            :key="index"
            :icon="activity.icon"
            :type="activity.type"
            :timestamp="activity.time"
          >
            {{ activity.content }}
          </el-timeline-item>
        </el-timeline>
      </div>
      
      <!-- AI 智能建议 -->
      <div class="ai-suggestions">
        <h2 class="section-title">AI 建议</h2>
        <div class="suggestion-cards">
          <div 
            v-for="suggestion in aiSuggestions" 
            :key="suggestion.id"
            class="suggestion-card"
          >
            <div class="suggestion-icon">
              <el-icon :size="24"><MagicStick /></el-icon>
            </div>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-desc">{{ suggestion.description }}</div>
            </div>
            <el-button type="primary" size="small" @click="handleSuggestion(suggestion)">
              立即处理
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Calendar, Wallet, FirstAidKit, Document, 
  ChatDotRound, ShoppingBag, MapLocation, MagicStick 
} from '@element-plus/icons-vue'

const router = useRouter()
const username = ref('同学')

const quickCards = [
  { 
    title: 'AI 问答', 
    desc: '智能教务助手',
    icon: 'ChatDotRound',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    path: '/ai/chat'
  },
  { 
    title: '创建日程', 
    desc: '安排你的时间',
    icon: 'Calendar',
    gradient: 'linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%)',
    path: '/calendar'
  },
  { 
    title: '记一笔', 
    desc: '记录支出收入',
    icon: 'Wallet',
    gradient: 'linear-gradient(135deg, #43E97B 0%, #38F9D7 100%)',
    path: '/budget'
  },
  { 
    title: '健康打卡', 
    desc: '保持健康生活',
    icon: 'FirstAidKit',
    gradient: 'linear-gradient(135deg, #FA709A 0%, #FEE140 100%)',
    path: '/health'
  },
]

const stats = ref({
  schedules: 5,
  balance: '1250',
  healthDays: 12,
  exams: 3
})

const recentActivities = ref([
  { content: '完成了健康打卡', time: '10分钟前', icon: 'FirstAidKit', type: 'success' },
  { content: '新增日程：期末考试复习', time: '1小时前', icon: 'Calendar', type: 'primary' },
  { content: 'AI 推荐了选课建议', time: '2小时前', icon: 'MagicStick', type: 'warning' },
])

const aiSuggestions = ref([
  { id: 1, title: '考试提醒', description: '距离"数据结构"期末考还有7天' },
  { id: 2, title: '预算提醒', description: '本月餐饮支出已达预算的80%' },
  { id: 3, title: '选课建议', description: '下学期"计算机网络"推荐选修' },
])
</script>

<style scoped lang="scss">
.dashboard {
  padding: 24px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}

.welcome-section {
  margin-bottom: 32px;
}

.welcome-text {
  margin-bottom: 24px;
  
  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    font-size: 16px;
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
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .card-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    color: #333;
  }
  
  .card-title {
    font-size: 18px;
    font-weight: 600;
    color: #fff;
  }
  
  .card-desc {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 4px;
  }
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid #3674FB;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
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
    font-size: 24px;
    font-weight: 600;
    color: #1a1a2e;
  }
  
  .stat-label {
    font-size: 13px;
    color: #999;
    margin-top: 4px;
  }
}

.content-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.recent-activity,
.ai-suggestions {
  background: #fff;
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
  padding: 16px;
  background: #F8FAFC;
  border-radius: 10px;
  gap: 12px;
  
  .suggestion-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }
  
  .suggestion-content {
    flex: 1;
    
    .suggestion-title {
      font-weight: 600;
      color: #1a1a2e;
    }
    
    .suggestion-desc {
      font-size: 13px;
      color: #666;
      margin-top: 2px;
    }
  }
}

/* 响应式 */
@media (max-width: 1200px) {
  .quick-cards,
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .quick-cards,
  .stats-grid,
  .content-section {
    grid-template-columns: 1fr;
  }
}
</style>
```

---

### 4. 预算管理页面 (BudgetView.vue 新建)

```vue
<template>
  <div class="budget-page">
    <!-- 顶部统计卡片 -->
    <div class="budget-header">
      <div class="balance-card">
        <div class="balance-label">本月剩余预算</div>
        <div class="balance-amount">¥{{ remainingBalance }}</div>
        <div class="balance-progress">
          <el-progress 
            :percentage="budgetPercentage" 
            :stroke-width="10"
            :color="budgetPercentage > 80 ? '#FF4D4F' : '#52C41A'"
          />
        </div>
        <div class="balance-info">
          <span>已支出: ¥{{ totalSpent }}</span>
          <span>预算总额: ¥{{ totalBudget }}</span>
        </div>
      </div>
      
      <!-- 快捷记账 -->
      <div class="quick-add">
        <h3>快速记账</h3>
        <div class="quick-amount">
          <span class="currency">¥</span>
          <input 
            v-model="quickAmount" 
            type="number" 
            placeholder="0"
            class="amount-input"
          />
        </div>
        <div class="category-select">
          <div 
            v-for="cat in categories" 
            :key="cat.id"
            class="category-item"
            :class="{ active: selectedCategory === cat.id }"
            @click="selectedCategory = cat.id"
          >
            <el-icon><component :is="cat.icon" /></el-icon>
            <span>{{ cat.name }}</span>
          </div>
        </div>
        <el-button type="primary" block @click="addExpense">确认支出</el-button>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="chart-section">
      <div class="chart-card">
        <h3>支出分布</h3>
        <div class="chart-container">
          <!-- ECharts 饼图 -->
        </div>
      </div>
      <div class="chart-card">
        <h3>支出趋势</h3>
        <div class="chart-container">
          <!-- ECharts 折线图 -->
        </div>
      </div>
    </div>
    
    <!-- 记录列表 -->
    <div class="records-section">
      <div class="section-header">
        <h3>消费记录</h3>
        <el-radio-group v-model="timeRange" size="small">
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
          <el-radio-button label="all">全部</el-radio-button>
        </el-radio-group>
      </div>
      <el-table :data="expenseList" stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="category" label="分类">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            <span class="amount">-¥{{ row.amount }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped lang="scss">
.budget-page {
  padding: 24px;
}

.budget-header {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.balance-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
  
  .balance-label {
    font-size: 14px;
    opacity: 0.9;
  }
  
  .balance-amount {
    font-size: 36px;
    font-weight: 700;
    margin: 12px 0;
  }
  
  .balance-info {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    opacity: 0.9;
    margin-top: 12px;
  }
}

.quick-add {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  
  h3 {
    margin-bottom: 20px;
    font-size: 16px;
  }
  
  .quick-amount {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .currency {
      font-size: 24px;
      color: #999;
      margin-right: 8px;
    }
    
    .amount-input {
      font-size: 36px;
      font-weight: 600;
      border: none;
      outline: none;
      width: 100%;
      color: #1a1a2e;
    }
  }
  
  .category-select {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 20px;
    
    .category-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 12px 8px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 12px;
      color: #666;
      
      &:hover {
        background: #f0f7ff;
      }
      
      &.active {
        background: #e6f7ff;
        color: #1890FF;
      }
      
      .el-icon {
        font-size: 24px;
        margin-bottom: 4px;
      }
    }
  }
}

.chart-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  h3 {
    font-size: 16px;
    margin-bottom: 16px;
  }
  
  .chart-container {
    height: 250px;
  }
}

.records-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      font-size: 16px;
    }
  }
  
  .amount {
    color: #FF4D4F;
    font-weight: 600;
  }
}
</style>
```

---

### 5. 健康打卡页面 (HealthView.vue 新建)

```vue
<template>
  <div class="health-page">
    <!-- 打卡状态卡片 -->
    <div class="checkin-header">
      <div class="checkin-status">
        <div class="status-icon" :class="{ checked: todayChecked }">
          <el-icon :size="48">
            <CircleCheck v-if="todayChecked" />
            <Clock v-else />
          </el-icon>
        </div>
        <div class="status-text">
          <h2>{{ todayChecked ? '今日已打卡' : '今日还未打卡' }}</h2>
          <p>连续打卡 <span class="highlight">{{ consecutiveDays }}</span> 天</p>
        </div>
      </div>
      
      <!-- 打卡按钮 -->
      <el-button 
        v-if="!todayChecked"
        type="primary" 
        size="large"
        @click="doCheckIn"
      >
        立即打卡
      </el-button>
    </div>
    
    <!-- 打卡表单 -->
    <div class="checkin-form" v-if="showCheckinForm">
      <el-form :model="checkinData" label-width="80px">
        <el-form-item label="睡眠时间">
          <el-time-picker 
            v-model="checkinData.sleepTime" 
            placeholder="入睡时间"
            format="HH:mm"
          />
          <span class="time-separator">至</span>
          <el-time-picker 
            v-model="checkinData.wakeTime" 
            placeholder="起床时间"
            format="HH:mm"
          />
        </el-form-item>
        
        <el-form-item label="运动状态">
          <el-radio-group v-model="checkinData.exercise">
            <el-radio label="none">未运动</el-radio-label>
            <el-radio label="light">轻度运动</el-radio>
            <el-radio label="medium">中度运动</el-radio>
            <el-radio label="heavy">剧烈运动</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="健康状况">
          <el-select v-model="checkinData.healthStatus" placeholder="请选择">
            <el-option label="健康" value="good" />
            <el-option label="轻微不适" value="minor" />
            <el-option label="身体不适" value="bad" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="今日备注">
          <el-input 
            v-model="checkinData.remark" 
            type="textarea" 
            :rows="3"
            placeholder="记录今天的身体状况..."
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitCheckin">提交</el-button>
          <el-button @click="showCheckinForm = false">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 统计数据 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background: #E6F7FF;">
          <el-icon color="#1890FF"><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ avgSleep }}</div>
          <div class="stat-label">平均睡眠(小时)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #F6FFED;">
          <el-icon color="#52C41A"><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ exerciseRate }}%</div>
          <div class="stat-label">运动率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #FFF7E6;">
          <el-icon color="#FA8C16"><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ healthScore }}</div>
          <div class="stat-label">健康评分</div>
        </div>
      </div>
    </div>
    
    <!-- 打卡记录 -->
    <div class="records-section">
      <h3>打卡记录</h3>
      <el-calendar v-model="calendarDate">
        <template #date-cell="{ data }">
          <div class="calendar-cell" :class="{ checked: isCheckedDate(data.day) }">
            <span class="date-number">{{ data.day.split('-')[2] }}</span>
            <el-icon v-if="isCheckedDate(data.day)" class="check-icon">
              <CircleCheck />
            </el-icon>
          </div>
        </template>
      </el-calendar>
    </div>
  </div>
</template>
```

---

### 6. 旅游规划页面 (TravelView.vue 新建)

```vue
<template>
  <div class="travel-page">
    <!-- 规划入口 -->
    <div class="plan-header">
      <h2>制定旅行计划</h2>
      <el-button type="primary" @click="startPlanning">
        <el-icon><Plus /></el-icon>
        新建规划
      </el-button>
    </div>
    
    <!-- AI 规划对话 -->
    <div class="ai-plan-section">
      <div class="section-header">
        <h3><el-icon><MagicStick /></el-icon> AI 智能规划</h3>
      </div>
      <div class="plan-form">
        <el-form :model="planForm" inline>
          <el-form-item label="目的地">
            <el-input v-model="planForm.destination" placeholder="想去哪里？" />
          </el-form-item>
          <el-form-item label="出行天数">
            <el-input-number v-model="planForm.days" :min="1" :max="30" />
          </el-form-item>
          <el-form-item label="预算">
            <el-input-number v-model="planForm.budget" :min="0" :step="100" />
            <span>元</span>
          </el-form-item>
          <el-form-item label="出行方式">
            <el-select v-model="planForm.style">
              <el-option label="穷游" value="budget" />
              <el-option label="舒适" value="comfortable" />
              <el-option label="豪华" value="luxury" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="generatePlan">
              生成计划
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    
    <!-- 行程展示 -->
    <div class="itinerary-section" v-if="itinerary.length">
      <h3>行程安排</h3>
      <el-timeline>
        <el-timeline-item
          v-for="(day, index) in itinerary"
          :key="index"
          :timestamp="`第${index + 1}天`"
          placement="top"
        >
          <el-card>
            <h4>{{ day.theme }}</h4>
            <div class="activities">
              <div 
                v-for="(activity, aIndex) in day.activities" 
                :key="aIndex"
                class="activity-item"
              >
                <span class="activity-time">{{ activity.time }}</span>
                <span class="activity-name">{{ activity.name }}</span>
                <span class="activity-cost">¥{{ activity.cost }}</span>
              </div>
            </div>
            <div class="day-summary">
              预计花费: ¥{{ day.totalCost }}
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
    
    <!-- 历史规划 -->
    <div class="history-section">
      <h3>我的旅行计划</h3>
      <div class="trip-cards">
        <div 
          v-for="trip in trips" 
          :key="trip.id"
          class="trip-card"
          @click="viewTrip(trip)"
        >
          <div class="trip-cover" :style="{ background: trip.coverColor }">
            <el-icon :size="40"><MapLocation /></el-icon>
          </div>
          <div class="trip-info">
            <h4>{{ trip.destination }}</h4>
            <p>{{ trip.startDate }} - {{ trip.endDate }}</p>
            <div class="trip-budget">
              预算: ¥{{ trip.budget }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

---

### 7. 二手市场页面 (MarketView.vue 新建)

```vue
<template>
  <div class="market-page">
    <!-- 顶部搜索 & 发布 -->
    <div class="market-header">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索商品..."
        prefix-icon="Search"
        size="large"
        class="search-input"
      />
      <el-button type="primary" size="large" @click="publishGoods">
        <el-icon><Plus /></el-icon>
        发布闲置
      </el-button>
    </div>
    
    <!-- 分类筛选 -->
    <div class="category-tabs">
      <el-tabs v-model="activeCategory">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="电子产品" name="electronics" />
        <el-tab-pane label="图书教材" name="books" />
        <el-tab-pane label="生活用品" name="daily" />
        <el-tab-pane label="运动健身" name="sports" />
        <el-tab-pane label="美妆服饰" name="fashion" />
      </el-tabs>
    </div>
    
    <!-- 商品列表 -->
    <div class="goods-grid">
      <div 
        v-for="goods in filteredGoods" 
        :key="goods.id"
        class="goods-card"
        @click="viewDetail(goods)"
      >
        <div class="goods-image">
          <el-image 
            :src="goods.images[0]" 
            fit="cover"
            lazy
          />
          <div class="goods-tag" v-if="goods.isNegotiable">
            可议价
          </div>
        </div>
        <div class="goods-info">
          <h4 class="goods-title">{{ goods.title }}</h4>
          <p class="goods-desc">{{ goods.description }}</p>
          <div class="goods-meta">
            <span class="goods-price">¥{{ goods.price }}</span>
            <span class="goods-time">{{ goods.time }}</span>
          </div>
          <div class="goods-user">
            <el-avatar :size="24" :src="goods.userAvatar" />
            <span>{{ goods.username }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 发布对话框 -->
    <el-dialog v-model="showPublishDialog" title="发布闲置" width="600px">
      <el-form :model="publishForm" label-width="80px">
        <el-form-item label="商品标题">
          <el-input v-model="publishForm.title" placeholder="简洁明了的标题" />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="publishForm.category">
            <el-option label="电子产品" value="electronics" />
            <el-option label="图书教材" value="books" />
            <el-option label="生活用品" value="daily" />
            <el-option label="运动健身" value="sports" />
            <el-option label="美妆服饰" value="fashion" />
          </el-select>
        </el-form-item>
        <el-form-item label="商品价格">
          <el-input-number v-model="publishForm.price" :min="0" />
          <el-checkbox v-model="publishForm.isNegotiable">可议价</el-checkbox>
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input 
            v-model="publishForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="描述商品的型号、新旧程度、使用情况..."
          />
        </el-form-item>
        <el-form-item label="商品图片">
          <el-upload
            v-model:file-list="publishForm.images"
            action="/api/upload"
            list-type="picture-card"
            :limit="9"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPublishDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPublish">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>
```

---

## 四、路由配置更新

```typescript
// router/index.ts
const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 首页
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('@/views/Dashboard.vue') },
    
    // 登录
    { path: '/login', component: () => import('@/views/Login.vue') },
    
    // AI 助手
    { 
      path: '/ai', 
      redirect: '/ai/chat',
      children: [
        { path: 'chat', component: () => import('@/views/AiChatView.vue') },
        { path: 'courses', component: () => import('@/views/CourseSelectView.vue') },
      ]
    },
    
    // 日程管理
    { path: '/calendar', component: () => import('@/views/CalendarView.vue') },
    
    // 预算管理
    { path: '/budget', component: () => import('@/views/BudgetView.vue') },
    
    // 健康打卡
    { path: '/health', component: () => import('@/views/HealthView.vue') },
    
    // 旅游规划
    { path: '/travel', component: () => import('@/views/TravelView.vue') },
    
    // 考试安排
    { path: '/exam', component: () => import('@/views/ExamView.vue') },
    
    // 二手市场
    { path: '/market', component: () => import('@/views/MarketView.vue') },
  ]
})
```

---

## 五、App.vue 布局整合

```vue
<template>
  <el-config-provider>
    <div class="app-container">
      <!-- 顶部导航 -->
      <HeaderView />
      
      <!-- 主体布局 -->
      <div class="main-layout">
        <!-- 侧边栏 -->
        <Sidebar />
        
        <!-- 内容区 -->
        <main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
  </el-config-provider>
</template>

<style>
.app-container {
  min-height: 100vh;
  background: #F8FAFC;
}

.main-layout {
  display: flex;
  padding-top: 60px;
}

.main-content {
  flex: 1;
  margin-left: 220px;
  min-height: calc(100vh - 60px);
  transition: margin-left 0.3s;
}

/* 侧边栏折叠时 */
.sidebar-collapsed .main-content {
  margin-left: 64px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
```

---

## 六、新增页面汇总

| 页面 | 文件 | 说明 |
|------|------|------|
| 首页 | Dashboard.vue | 仪表盘，聚合各模块关键信息 |
| 预算管理 | BudgetView.vue | 记账、预算、统计图表 |
| 健康打卡 | HealthView.vue | 每日打卡、健康统计 |
| 旅游规划 | TravelView.vue | AI 生成行程、行程管理 |
| 考试安排 | ExamView.vue | 考试列表、复习计划 |
| 二手市场 | MarketView.vue | 商品发布、浏览、详情 |
| 选课推荐 | CourseSelectView.vue | AI 选课建议、课程评价 |

---

## 七、视觉设计规范

### 配色系统
```scss
// 主题色
$primary: #3674FB;        // 交大蓝
$primary-light: #6BB3FF; // 浅蓝
$primary-dark: #1A4FBF;  // 深蓝

// 功能色
$success: #52C41A;       // 成功-绿
$warning: #FAAD14;       // 警告-橙
$danger: #FF4D4F;        // 危险-红
$info: #909399;          // 信息-灰

// 中性色
$text-primary: #1A1A2E;   // 主要文字
$text-regular: #666666;    // 常规文字
$text-secondary: #999999; // 次要文字
$border: #E5E7EB;         // 边框
$bg-white: #FFFFFF;      // 白色背景
$bg-page: #F8FAFC;       // 页面背景
```

### 组件规范
- 卡片圆角: `12px` 或 `16px`
- 按钮高度: `36px` (默认), `44px` (大按钮)
- 间距系统: `8px`, `12px`, `16px`, `24px`, `32px`
- 阴影: `0 2px 8px rgba(0, 0, 0, 0.06)` (卡片)
- 字体: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

---

这份设计方案保留了现有项目的交大特色，同时增加了更多实用的功能模块，界面更加模块化和现代化。你可以根据实际需要逐步实现这些页面。
