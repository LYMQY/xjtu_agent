<template>
  <div class="travel-page">
    <!-- 顶部 Banner -->
    <div class="travel-banner">
      <div class="banner-content">
        <h1>🧳 旅游规划助手</h1>
        <p>AI 智能规划你的下一次旅程</p>
      </div>
    </div>
    
    <!-- 规划入口 -->
    <div class="plan-section">
      <h2 class="section-title">制定旅行计划</h2>
      
      <!-- AI 规划表单 -->
      <div class="ai-plan-card">
        <div class="plan-header">
          <el-icon :size="24"><MagicStick /></el-icon>
          <span>AI 智能规划</span>
        </div>
        
        <el-form :model="planForm" inline class="plan-form">
          <el-form-item label="目的地">
            <el-input 
              v-model="planForm.destination" 
              placeholder="想去哪里？如：西安、成都"
              size="large"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="出行天数">
            <el-input-number 
              v-model="planForm.days" 
              :min="1" 
              :max="30" 
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="人均预算">
            <el-input-number 
              v-model="planForm.budget" 
              :min="0" 
              :step="100"
              size="large"
            />
            <span class="unit">元</span>
          </el-form-item>
          
          <el-form-item label="出行方式">
            <el-select v-model="planForm.style" size="large" placeholder="选择出行风格">
              <el-option label="🚶 穷游省票" value="budget" />
              <el-option label="🚗 舒适自由" value="comfortable" />
              <el-option label="✈️ 豪华体验" value="luxury" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="出行人数">
            <el-input-number v-model="planForm.people" :min="1" :max="20" size="large" />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              @click="generatePlan"
              :loading="generating"
            >
              <el-icon v-if="!generating"><MagicStick /></el-icon>
              {{ generating ? 'AI 规划中...' : '生成计划' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="plan-tips">
          <el-icon><InfoFilled /></el-icon>
          <span>输入你的旅行偏好，AI 将为你生成详细的行程安排</span>
        </div>
      </div>
    </div>
    
    <!-- AI 生成的行程展示 -->
    <div class="itinerary-section" v-if="generatedItinerary">
      <div class="itinerary-header">
        <h2 class="section-title">行程安排</h2>
        <div class="itinerary-actions">
          <el-button @click="saveItinerary" type="primary">
            <el-icon><DocumentChecked /></el-icon>
            保存行程
          </el-button>
          <el-button @click="exportItinerary">
            <el-icon><Download /></el-icon>
            导出行程
          </el-button>
        </div>
      </div>
      
      <div class="itinerary-stats">
        <div class="stat-item">
          <el-icon><Location /></el-icon>
          <span>{{ generatedItinerary.destination }}</span>
        </div>
        <div class="stat-item">
          <el-icon><Calendar /></el-icon>
          <span>{{ generatedItinerary.days }} 天</span>
        </div>
        <div class="stat-item">
          <el-icon><Money /></el-icon>
          <span>约 ¥{{ generatedItinerary.totalCost }}</span>
        </div>
        <div class="stat-item">
          <el-icon><User /></el-icon>
          <span>{{ generatedItinerary.people }} 人</span>
        </div>
      </div>
      
      <el-timeline>
        <el-timeline-item
          v-for="(day, index) in generatedItinerary.schedule"
          :key="index"
          :timestamp="`第 ${index + 1} 天`"
          placement="top"
          :type="index === 0 ? 'primary' : ''"
          size="large"
        >
          <el-card class="day-card">
            <div class="day-header">
              <h3>{{ day.theme }}</h3>
              <el-tag type="success">预算 ¥{{ day.dayCost }}</el-tag>
            </div>
            
            <div class="activities">
              <div 
                v-for="(activity, aIndex) in day.activities" 
                :key="aIndex"
                class="activity-item"
              >
                <div class="activity-time">{{ activity.time }}</div>
                <div class="activity-content">
                  <div class="activity-name">{{ activity.name }}</div>
                  <div class="activity-desc">{{ activity.desc }}</div>
                  <div class="activity-meta">
                    <span v-if="activity.location">
                      <el-icon><Location /></el-icon>
                      {{ activity.location }}
                    </span>
                    <span v-if="activity.cost">
                      <el-icon><Money /></el-icon>
                      ¥{{ activity.cost }}
                    </span>
                    <span v-if="activity.duration">
                      <el-icon><Clock /></el-icon>
                      {{ activity.duration }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="day-footer">
              <div class="meals">
                <span v-if="day.meals?.breakfast">🌅 早餐: {{ day.meals.breakfast }}</span>
                <span v-if="day.meals?.lunch">🌞 午餐: {{ day.meals.lunch }}</span>
                <span v-if="day.meals?.dinner">🌙 晚餐: {{ day.meals.dinner }}</span>
              </div>
              <div class="day-tips" v-if="day.tips">
                <el-icon><InfoFilled /></el-icon>
                {{ day.tips }}
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
    
    <!-- 历史规划 -->
    <div class="history-section">
      <h2 class="section-title">我的旅行计划</h2>
      
      <div class="trip-cards" v-if="tripList.length">
        <div 
          v-for="trip in tripList" 
          :key="trip.id"
          class="trip-card"
          @click="viewTrip(trip)"
        >
          <div class="trip-cover" :style="{ background: trip.coverGradient }">
            <div class="trip-dates">{{ trip.startDate }} - {{ trip.endDate }}</div>
          </div>
          <div class="trip-info">
            <h3>{{ trip.destination }}</h3>
            <div class="trip-meta">
              <span><el-icon><Calendar /></el-icon> {{ trip.days }} 天</span>
              <span><el-icon><User /></el-icon> {{ trip.people }} 人</span>
              <span><el-icon><Money /></el-icon> ¥{{ trip.budget }}</span>
            </div>
            <div class="trip-status">
              <el-tag :type="trip.status === 'upcoming' ? 'warning' : trip.status === 'completed' ? 'success' : 'info'" size="small">
                {{ trip.statusText }}
              </el-tag>
            </div>
          </div>
          <div class="trip-actions">
            <el-button type="primary" link @click.stop="viewTrip(trip)">查看</el-button>
            <el-button type="danger" link @click.stop="deleteTrip(trip.id)">删除</el-button>
          </div>
        </div>
      </div>
      
      <el-empty v-else description="暂无旅行计划，开始规划你的第一次旅行吧！">
        <el-button type="primary" @click="scrollToPlan">开始规划</el-button>
      </el-empty>
    </div>
    
    <!-- 推荐目的地 -->
    <div class="recommend-section">
      <h2 class="section-title">热门目的地推荐</h2>
      <div class="recommend-grid">
        <div 
          v-for="place in recommendPlaces" 
          :key="place.name"
          class="recommend-card"
          @click="quickPlan(place)"
        >
          <div class="recommend-cover" :style="{ background: place.gradient }">
            <span class="recommend-tag">{{ place.tag }}</span>
          </div>
          <div class="recommend-info">
            <h4>{{ place.name }}</h4>
            <p>{{ place.desc }}</p>
            <div class="recommend-price">
              <span>人均</span>
              <strong>¥{{ place.price }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  MagicStick, InfoFilled, Location, Calendar, Money, User, Clock,
  DocumentChecked, Download 
} from '@element-plus/icons-vue'

const generating = ref(false)
const generatedItinerary = ref<any>(null)

// 规划表单
const planForm = ref({
  destination: '',
  days: 3,
  budget: 1500,
  style: 'comfortable',
  people: 1
})

// 历史旅行列表
const tripList = ref<any[]>([])

// 推荐目的地
const recommendPlaces = ref([
  {
    name: '西安',
    desc: '千年古都，兵马俑、大雁塔',
    tag: '历史人文',
    price: 1200,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    name: '成都',
    desc: '天府之国，美食与熊猫',
    tag: '休闲美食',
    price: 1000,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    name: '杭州',
    desc: '西湖美景，江南水乡',
    tag: '自然风光',
    price: 1100,
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    name: '厦门',
    desc: '海滨城市，鼓浪屿',
    tag: '海滨度假',
    price: 1300,
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  },
  {
    name: '重庆',
    desc: '山城雾都，火锅美食',
    tag: '美食之旅',
    price: 900,
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    name: '大理',
    desc: '风花雪月，洱海苍山',
    tag: '文艺慢生活',
    price: 1100,
    gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
  }
])

// 生成旅行计划
const generatePlan = async () => {
  if (!planForm.value.destination) {
    ElMessage.warning('请输入目的地')
    return
  }
  
  generating.value = true
  
  // 模拟 AI 生成过程
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  const { destination, days, budget, style, people } = planForm.value
  
  // 模拟生成行程
  const itinerary = generateMockItinerary(destination, days, budget, style, people)
  
  generatedItinerary.value = itinerary
  generating.value = false
  
  ElMessage.success('行程生成成功！')
}

// 生成模拟行程数据
const generateMockItinerary = (destination: string, days: number, budget: number, style: string, people: number) => {
  const activities = [
    { time: '08:00', name: '酒店早餐', desc: '享用酒店自助早餐', location: '酒店', cost: 0, duration: '1小时' },
    { time: '09:00', name: '抵达景点', desc: '开始游览', location: '', cost: 50, duration: '30分钟' },
    { time: '10:00', name: '主要景点游览', desc: '深度游览', location: '', cost: 80, duration: '3小时' },
    { time: '13:00', name: '当地特色午餐', desc: '品尝当地美食', location: '', cost: 40, duration: '1小时' },
    { time: '14:00', name: '下午景点', desc: '继续游览', location: '', cost: 60, duration: '2小时' },
    { time: '17:00', name: '自由活动', desc: '购物或休息', location: '', cost: 0, duration: '2小时' },
    { time: '19:00', name: '晚餐', desc: '当地特色晚餐', location: '', cost: 60, duration: '1.5小时' },
    { time: '21:00', name: '返回酒店', desc: '休息', location: '酒店', cost: 0, duration: '30分钟' }
  ]
  
  const themes = [
    '历史文化探秘',
    '美食之旅',
    '自然风光欣赏',
    '城市漫步',
    '休闲度假'
  ]
  
  const meals = [
    { breakfast: '酒店自助', lunch: '特色小吃', dinner: '当地火锅' },
    { breakfast: '豆浆油条', lunch: '川菜', dinner: '夜市美食' },
    { breakfast: '酒店自助', lunch: '景区简餐', dinner: '特色餐厅' }
  ]
  
  const schedule = []
  let totalCost = 0
  
  for (let i = 0; i < days; i++) {
    const dayActivities = activities.slice(0, 4 + Math.floor(Math.random() * 4))
    const dayCost = dayActivities.reduce((sum: number, a: any) => sum + (a.cost || 0), 0) + 100 // 加上住宿预算
    
    schedule.push({
      theme: themes[i % themes.length],
      dayCost,
      activities: dayActivities,
      meals: meals[i % meals.length],
      tips: i === 0 ? '第一天建议早睡，适应行程' : i === days - 1 ? '最后一天注意返程时间' : ''
    })
    
    totalCost += dayCost
  }
  
  return {
    destination,
    days,
    people,
    totalCost,
    budget,
    style,
    schedule
  }
}

// 保存行程
const saveItinerary = () => {
  if (!generatedItinerary.value) return
  
  const newTrip = {
    id: Date.now().toString(),
    destination: generatedItinerary.value.destination,
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date(Date.now() + generatedItinerary.value.days * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    days: generatedItinerary.value.days,
    people: generatedItinerary.value.people,
    budget: generatedItinerary.value.totalCost,
    status: 'upcoming',
    statusText: '即将出行',
    coverGradient: recommendPlaces.value[Math.floor(Math.random() * recommendPlaces.value.length)].gradient
  }
  
  tripList.value.unshift(newTrip)
  localStorage.setItem('tripList', JSON.stringify(tripList.value))
  
  ElMessage.success('行程已保存！')
}

// 导出行程
const exportItinerary = () => {
  if (!generatedItinerary.value) return
  
  const content = generateItineraryText()
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${generatedItinerary.value.destination}_行程规划.md`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('行程已导出！')
}

// 生成行程文本
const generateItineraryText = () => {
  const it = generatedItinerary.value
  let text = `# ${it.destination} ${it.days}天${it.people}人旅行规划\n\n`
  text += `> 预算: ¥${it.totalCost} | 风格: ${it.style}\n\n`
  
  it.schedule.forEach((day: any, index: number) => {
    text += `## 第${index + 1}天 - ${day.theme}\n\n`
    text += `> 预计花费: ¥${day.dayCost}\n\n`
    
    day.activities.forEach((a: any) => {
      text += `- **${a.time}** ${a.name} - ${a.desc}`
      if (a.location) text += ` (${a.location})`
      if (a.cost) text += ` ¥${a.cost}`
      text += `\n`
    })
    
    if (day.tips) {
      text += `\n> 💡 小贴士: ${day.tips}\n`
    }
    text += `\n---\n\n`
  })
  
  return text
}

// 查看行程
const viewTrip = (trip: any) => {
  planForm.value = {
    destination: trip.destination,
    days: trip.days,
    budget: trip.budget,
    style: 'comfortable',
    people: trip.people
  }
  generatePlan()
}

// 删除行程
const deleteTrip = (id: string) => {
  const index = tripList.value.findIndex(t => t.id === id)
  if (index > -1) {
    tripList.value.splice(index, 1)
    localStorage.setItem('tripList', JSON.stringify(tripList.value))
    ElMessage.success('删除成功')
  }
}

// 快速规划
const quickPlan = (place: any) => {
  planForm.value.destination = place.name
  planForm.value.budget = place.price * 2
  scrollToPlan()
  ElMessage.success(`已选择目的地: ${place.name}`)
}

// 滚动到规划区域
const scrollToPlan = () => {
  const el = document.querySelector('.plan-section')
  el?.scrollIntoView({ behavior: 'smooth' })
}

// 加载历史数据
const loadTrips = () => {
  try {
    const saved = localStorage.getItem('tripList')
    if (saved) {
      tripList.value = JSON.parse(saved)
    } else {
      // 添加一些模拟历史数据
      tripList.value = [
        {
          id: '1',
          destination: '西安',
          startDate: '2024-01-15',
          endDate: '2024-01-18',
          days: 3,
          people: 2,
          budget: 2500,
          status: 'completed',
          statusText: '已完成',
          coverGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }
      ]
    }
  } catch (e) {
    console.error('加载旅行数据失败:', e)
  }
}

onMounted(() => {
  loadTrips()
})
</script>

<style scoped lang="scss">
.travel-page {
  padding: 24px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}

.travel-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 32px;
  text-align: center;
  color: #fff;
  
  h1 {
    font-size: 32px;
    margin-bottom: 12px;
  }
  
  p {
    font-size: 16px;
    opacity: 0.9;
  }
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 20px;
  padding-left: 12px;
  border-left: 4px solid #3674FB;
}

.plan-section {
  margin-bottom: 32px;
}

.ai-plan-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  
  .plan-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    color: #667eea;
    margin-bottom: 20px;
  }
  
  .plan-form {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    
    .el-form-item {
      margin-bottom: 0;
    }
    
    .unit {
      margin-left: 8px;
      color: #666;
    }
  }
  
  .plan-tips {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 16px;
    padding: 12px;
    background: #f0f7ff;
    border-radius: 8px;
    color: #666;
    font-size: 14px;
  }
}

.itinerary-section {
  margin-bottom: 32px;
  
  .itinerary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .section-title {
      margin-bottom: 0;
    }
    
    .itinerary-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .itinerary-stats {
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    padding: 16px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #666;
      
      .el-icon {
        color: #3674FB;
      }
    }
  }
}

.day-card {
  margin-bottom: 16px;
  
  .day-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      font-size: 16px;
      margin: 0;
    }
  }
  
  .activities {
    .activity-item {
      display: flex;
      gap: 16px;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .activity-time {
        width: 60px;
        color: #3674FB;
        font-weight: 600;
        font-size: 14px;
      }
      
      .activity-content {
        flex: 1;
        
        .activity-name {
          font-weight: 600;
          color: #1a1a2e;
        }
        
        .activity-desc {
          font-size: 13px;
          color: #666;
          margin: 4px 0;
        }
        
        .activity-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #999;
          
          span {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
  }
  
  .day-footer {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px dashed #eee;
    
    .meals {
      display: flex;
      gap: 16px;
      margin-bottom: 8px;
      font-size: 13px;
      color: #666;
    }
    
    .day-tips {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: #fa8c16;
    }
  }
}

.history-section {
  margin-bottom: 32px;
}

.trip-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.trip-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .trip-cover {
    height: 120px;
    display: flex;
    align-items: flex-end;
    padding: 16px;
    
    .trip-dates {
      color: #fff;
      font-size: 13px;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
  }
  
  .trip-info {
    padding: 16px;
    
    h3 {
      font-size: 16px;
      margin: 0 0 8px;
    }
    
    .trip-meta {
      display: flex;
      gap: 16px;
      font-size: 13px;
      color: #999;
      margin-bottom: 8px;
      
      span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
  
  .trip-actions {
    padding: 0 16px 16px;
    display: flex;
    gap: 8px;
  }
}

.recommend-section {
  margin-bottom: 24px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.recommend-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-4px);
  }
  
  .recommend-cover {
    height: 100px;
    position: relative;
    
    .recommend-tag {
      position: absolute;
      top: 12px;
      right: 12px;
      background: rgba(255, 255, 255, 0.9);
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      color: #333;
    }
  }
  
  .recommend-info {
    padding: 16px;
    
    h4 {
      font-size: 16px;
      margin: 0 0 8px;
    }
    
    p {
      font-size: 13px;
      color: #666;
      margin: 0 0 12px;
    }
    
    .recommend-price {
      display: flex;
      align-items: baseline;
      gap: 4px;
      
      span {
        font-size: 12px;
        color: #999;
      }
      
      strong {
        font-size: 18px;
        color: #FF4D4F;
      }
    }
  }
}

@media (max-width: 1024px) {
  .trip-cards,
  .recommend-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .trip-cards,
  .recommend-grid {
    grid-template-columns: 1fr;
  }
  
  .ai-plan-card .plan-form {
    flex-direction: column;
    
    .el-form-item {
      width: 100%;
    }
  }
  
  .itinerary-section .itinerary-stats {
    flex-wrap: wrap;
  }
}
</style>
