<template>
    <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
    </header>
  <div class="health-page">
    <!-- 打卡状态卡片 -->
    <div class="checkin-header">
      <div class="checkin-status">
        <div class="status-icon" :class="{ checked: todayChecked }">
          <el-icon :size="56">
            <CircleCheck v-if="todayChecked" />
            <Clock v-else />
          </el-icon>
        </div>
        <div class="status-text">
          <h2>{{ todayChecked ? '今日已打卡' : '今日还未打卡' }}</h2>
          <p>连续打卡 <span class="highlight">{{ consecutiveDays }}</span> 天</p>
        </div>
      </div>
      
      <el-button 
        v-if="!todayChecked"
        type="primary" 
        size="large"
        @click="showCheckinForm = true"
      >
        <el-icon><Plus /></el-icon>
        立即打卡
      </el-button>
      <el-button 
        v-else
        size="large"
        @click="showCheckinForm = true"
      >
        <el-icon><Edit /></el-icon>
        修改打卡
      </el-button>
    </div>
    
    <!-- 打卡表单对话框 -->
    <el-dialog 
      v-model="showCheckinForm" 
      :title="todayChecked ? '修改打卡记录' : '每日健康打卡'" 
      width="500px"
    >
      <el-form :model="checkinData" label-width="90px">
        <el-form-item label="睡眠时间">
          <div class="time-range">
            <el-time-picker 
              v-model="checkinData.sleepTime" 
              placeholder="入睡时间"
              format="HH:mm"
              size="default"
            />
            <span class="time-separator">至</span>
            <el-time-picker 
              v-model="checkinData.wakeTime" 
              placeholder="起床时间"
              format="HH:mm"
              size="default"
            />
          </div>
        </el-form-item>
        
        <el-form-item label="睡眠时长">
          <div class="sleep-duration">
            <el-tag type="success" size="large">{{ sleepDuration }} 小时</el-tag>
          </div>
        </el-form-item>
        
        <el-form-item label="今日运动">
          <el-radio-group v-model="checkinData.exercise">
            <el-radio-button label="none">未运动</el-radio-button>
            <el-radio-button label="light">轻度(30min内)</el-radio-button>
            <el-radio-button label="medium">中度(30-60min)</el-radio-button>
            <el-radio-button label="heavy">剧烈(60min+)</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="今日步数">
          <div class="steps-input">
            <el-input-number v-model="checkinData.steps" :min="0" :max="100000" :step="100" />
            <span class="steps-unit">步</span>
          </div>
        </el-form-item>
        
        <el-form-item label="健康状况">
          <el-select v-model="checkinData.healthStatus" placeholder="请选择" style="width: 100%">
            <el-option label="💚 非常健康" value="excellent" />
            <el-option label="💙 健康" value="good" />
            <el-option label="💛 轻微不适" value="minor" />
            <el-option label="🧡 身体不适" value="bad" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="今日体重">
          <div class="weight-input">
            <el-input-number v-model="checkinData.weight" :min="30" :max="200" :precision="1" />
            <span class="weight-unit">kg</span>
          </div>
        </el-form-item>
        
        <el-form-item label="今日备注">
          <el-input 
            v-model="checkinData.remark" 
            type="textarea" 
            :rows="3"
            placeholder="记录今天的身体状况、情绪等..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCheckinForm = false">取消</el-button>
        <el-button type="primary" @click="submitCheckin">
          {{ todayChecked ? '保存修改' : '确认打卡' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 统计数据卡片 -->
    <div class="stats-section">
      <h3 class="section-title">健康数据概览</h3>
      <div class="stats-grid">
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
            <el-icon color="#52C41A"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ avgSteps }}</div>
            <div class="stat-label">平均步数</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF7E6;">
            <el-icon color="#FA8C16"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ exerciseRate }}%</div>
            <div class="stat-label">运动率</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon" style="background: #F9F0FF;">
            <el-icon color="#722ED1"><FirstAidKit /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ healthScore }}</div>
            <div class="stat-label">健康评分</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="chart-section">
      <div class="chart-card">
        <h3>睡眠时长趋势</h3>
        <div ref="sleepChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <h3>运动与步数</h3>
        <div ref="exerciseChartRef" class="chart-container"></div>
      </div>
    </div>
    
    <!-- 打卡日历 -->
    <div class="calendar-section">
      <h3 class="section-title">打卡日历</h3>
      <div class="calendar-wrapper">
        <el-calendar v-model="calendarDate">
          <template #date-cell="{ data }">
            <div 
              class="calendar-cell" 
              :class="{ 
                checked: isCheckedDate(data.day),
                excellent: getCheckStatus(data.day) === 'excellent',
                good: getCheckStatus(data.day) === 'good',
                bad: getCheckStatus(data.day) === 'bad'
              }"
            >
              <span class="date-number">{{ data.day.split('-')[2] }}</span>
              <div class="check-indicator" v-if="isCheckedDate(data.day)">
                <el-icon v-if="getCheckStatus(data.day) === 'excellent'"><Sunny /></el-icon>
                <el-icon v-else-if="getCheckStatus(data.day) === 'good'"><CircleCheck /></el-icon>
                <el-icon v-else-if="getCheckStatus(data.day) === 'bad'"><Warning /></el-icon>
                <el-icon v-else><CircleCheck /></el-icon>
              </div>
            </div>
          </template>
        </el-calendar>
      </div>
    </div>
    
    <!-- 打卡记录列表 -->
    <div class="records-section">
      <div class="section-header">
        <h3>打卡记录</h3>
        <el-radio-group v-model="timeRange" size="small" @change="loadCheckins">
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
        </el-radio-group>
      </div>
      
      <el-table :data="checkinList" stripe v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column label="睡眠" width="100">
          <template #default="{ row }">
            <span>{{ row.sleepDuration || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="运动" width="100">
          <template #default="{ row }">
            <el-tag :type="getExerciseType(row.exercise)" size="small">
              {{ getExerciseText(row.exercise) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="steps" label="步数" width="100" />
        <el-table-column label="健康" width="100">
          <template #default="{ row }">
            <el-tag :type="getHealthType(row.healthStatus)" size="small">
              {{ getHealthText(row.healthStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column prop="remark" label="备注" min-width="150" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import HeaderView from "@/components/CHeaderView.vue";
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  CircleCheck, Clock, Plus, Edit, Sunny, TrendCharts, 
  DataLine, FirstAidKit, Warning 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getToken } from '@/utils/auth'

const loading = ref(false)
const showCheckinForm = ref(false)
const todayChecked = ref(false)
const consecutiveDays = ref(0)
const calendarDate = ref(new Date())
const timeRange = ref('month')

const sleepChartRef = ref<HTMLElement>()
const exerciseChartRef = ref<HTMLElement>()
let sleepChart: echarts.ECharts | null = null
let exerciseChart: echarts.ECharts | null = null

// 打卡数据
const checkinList = ref<any[]>([])
const checkinMap = ref<Record<string, any>>({})

// 打卡表单
const checkinData = ref({
  sleepTime: '',
  wakeTime: '',
  exercise: 'none',
  steps: 5000,
  healthStatus: 'good',
  weight: 60,
  remark: ''
})

// 计算睡眠时长
const sleepDuration = computed(() => {
  if (!checkinData.value.sleepTime || !checkinData.value.wakeTime) return 0
  const sleep = new Date(checkinData.value.sleepTime)
  const wake = new Date(checkinData.value.wakeTime)
  let diff = (wake.getTime() - sleep.getTime()) / (1000 * 60 * 60)
  if (diff < 0) diff += 24
  return diff.toFixed(1)
})

// 统计数据
const avgSleep = ref('7.5')
const avgSteps = ref('6500')
const exerciseRate = ref(75)
const healthScore = ref(85)

const getToday = () => new Date().toISOString().split('T')[0]

// 检查某日期是否打卡
const isCheckedDate = (date: string) => {
  const dateStr = date.slice(0, 10)
  return !!checkinMap.value[dateStr]
}

// 获取打卡状态
const getCheckStatus = (date: string) => {
  const dateStr = date.slice(0, 10)
  return checkinMap.value[dateStr]?.healthStatus || null
}

// 加载打卡记录
const loadCheckins = async () => {
  loading.value = true
  try {
    const token = getToken()
    if (!token) {
      loadMockData()
      return
    }
    
    const response = await fetch('http://localhost:8000/api/health/checkins/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      checkinList.value = data.items || data || []
      updateCheckinMap()
    }
  } catch (error) {
    console.error('加载打卡记录失败:', error)
    loadMockData()
  } finally {
    loading.value = false
  }
}

// 加载模拟数据
const loadMockData = () => {
  const today = getToday()
  const mockData = [
    { id: '1', date: today, sleepDuration: '7.5', exercise: 'medium', steps: 8500, healthStatus: 'good', weight: 60, remark: '状态不错' },
    { id: '2', date: '2024-01-26', sleepDuration: '6.5', exercise: 'light', steps: 5200, healthStatus: 'good', weight: 60.5, remark: '' },
    { id: '3', date: '2024-01-25', sleepDuration: '8', exercise: 'medium', steps: 12000, healthStatus: 'excellent', weight: 60, remark: '跑步了' },
    { id: '4', date: '2024-01-24', sleepDuration: '7', exercise: 'none', steps: 3000, healthStatus: 'minor', weight: 61, remark: '有点感冒' },
    { id: '5', date: '2024-01-23', sleepDuration: '7.5', exercise: 'light', steps: 6800, healthStatus: 'good', weight: 60.5, remark: '' },
    { id: '6', date: '2024-01-22', sleepDuration: '8', exercise: 'heavy', steps: 15000, healthStatus: 'excellent', weight: 60, remark: '马拉松训练' },
    { id: '7', date: '2024-01-21', sleepDuration: '7', exercise: 'medium', steps: 7500, healthStatus: 'good', weight: 60, remark: '' },
  ]
  
  checkinList.value = mockData
  updateCheckinMap()
  checkTodayStatus()
}

// 更新打卡映射
const updateCheckinMap = () => {
  checkinMap.value = {}
  checkinList.value.forEach(item => {
    checkinMap.value[item.date] = item
  })
  checkTodayStatus()
}

// 检查今日打卡状态
const checkTodayStatus = () => {
  const today = getToday()
  todayChecked.value = !!checkinMap.value[today]
  
  // 计算连续打卡天数
  let consecutive = 0
  let checkDate = new Date()
  while (true) {
    const dateStr = checkDate.toISOString().split('T')[0]
    if (checkinMap.value[dateStr]) {
      consecutive++
      checkDate.setDate(checkDate.getDate() - 1)
    } else {
      break
    }
  }
  consecutiveDays.value = consecutive
}

// 提交打卡
const submitCheckin = async () => {
  const today = getToday()
  const newCheckin = {
    date: today,
    sleepDuration: sleepDuration.value,
    exercise: checkinData.value.exercise,
    steps: checkinData.value.steps,
    healthStatus: checkinData.value.healthStatus,
    weight: checkinData.value.weight,
    remark: checkinData.value.remark
  }
  
  try {
    const token = getToken()
    if (token) {
      await fetch('http://localhost:8000/api/health/checkins/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newCheckin)
      })
    }
  } catch (error) {
    console.log('使用本地模拟数据')
  }
  
  // 更新本地数据
  const index = checkinList.value.findIndex(item => item.date === today)
  if (index > -1) {
    checkinList.value[index] = { id: today, ...newCheckin }
  } else {
    checkinList.value.unshift({ id: today, ...newCheckin })
  }
  
  updateCheckinMap()
  showCheckinForm.value = false
  ElMessage.success(todayChecked.value ? '修改成功' : '打卡成功')
  
  // 更新图表
  nextTick(() => updateCharts())
}

// 更新图表
const updateCharts = () => {
  // 睡眠趋势图
  const sleepData = checkinList.value.slice(0, 14).reverse()
  const sleepValues = sleepData.map(d => d.sleepDuration || 0)
  const sleepDates = sleepData.map(d => d.date.slice(5))
  
  if (sleepChartRef.value) {
    if (!sleepChart) {
      sleepChart = echarts.init(sleepChartRef.value)
    }
    sleepChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: sleepDates, axisLabel: { rotate: 45 } },
      yAxis: { type: 'value', min: 0, max: 12, axisLabel: { formatter: '{value}h' } },
      series: [{
        data: sleepValues,
        type: 'bar',
        barWidth: '50%',
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        markLine: {
          data: [{ yAxis: 7, name: '推荐睡眠' }],
          lineStyle: { color: '#52C41A', type: 'dashed' }
        }
      }]
    })
  }
  
  // 运动步数图
  const stepsValues = sleepData.map(d => d.steps || 0)
  
  if (exerciseChartRef.value) {
    if (!exerciseChart) {
      exerciseChart = echarts.init(exerciseChartRef.value)
    }
    exerciseChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: sleepDates, axisLabel: { rotate: 45 } },
      yAxis: { type: 'value', axisLabel: { formatter: '{value}步' } },
      series: [
        {
          name: '步数',
          data: stepsValues,
          type: 'line',
          smooth: true,
          areaStyle: { color: 'rgba(82, 196, 26, 0.2)' },
          itemStyle: { color: '#52C41A' },
          lineStyle: { width: 2 }
        }
      ]
    })
  }
}

// 类型转换函数
const getExerciseType = (exercise: string) => {
  const typeMap: Record<string, string> = {
    none: 'info',
    light: 'success',
    medium: 'warning',
    heavy: 'danger'
  }
  return typeMap[exercise] || ''
}

const getExerciseText = (exercise: string) => {
  const textMap: Record<string, string> = {
    none: '未运动',
    light: '轻度',
    medium: '中度',
    heavy: '剧烈'
  }
  return textMap[exercise] || exercise
}

const getHealthType = (status: string) => {
  const typeMap: Record<string, string> = {
    excellent: 'success',
    good: 'primary',
    minor: 'warning',
    bad: 'danger'
  }
  return typeMap[status] || ''
}

const getHealthText = (status: string) => {
  const textMap: Record<string, string> = {
    excellent: '非常健康',
    good: '健康',
    minor: '轻微不适',
    bad: '身体不适'
  }
  return textMap[status] || status
}

// 监听日历月份变化
watch(calendarDate, () => {
  nextTick(() => updateCharts())
})

// 窗口大小变化
const handleResize = () => {
  sleepChart?.resize()
  exerciseChart?.resize()
}

onMounted(() => {
  loadCheckins()
  nextTick(() => updateCharts())
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.health-page {
  padding: 24px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}

.checkin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  color: #fff;
}

.checkin-status {
  display: flex;
  align-items: center;
  gap: 20px;
  
  .status-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    
    &.checked {
      background: #52C41A;
    }
  }
  
  .status-text {
    h2 {
      font-size: 24px;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 14px;
      opacity: 0.9;
      
      .highlight {
        font-size: 20px;
        font-weight: 700;
        margin: 0 4px;
      }
    }
  }
}

.stats-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
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
    color: #1a1a2e;
  }
  
  .chart-container {
    height: 250px;
  }
}

.calendar-section {
  margin-bottom: 24px;
}

.calendar-wrapper {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.calendar-cell {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  
  .date-number {
    font-size: 14px;
  }
  
  .check-indicator {
    position: absolute;
    bottom: 2px;
    font-size: 12px;
  }
  
  &.checked {
    background: #E6F7FF;
    border-radius: 6px;
  }
  
  &.excellent {
    background: #F6FFED;
    .check-indicator { color: #52C41A; }
  }
  
  &.good {
    background: #E6F7FF;
    .check-indicator { color: #1890FF; }
  }
  
  &.bad {
    background: #FFF1F0;
    .check-indicator { color: #FF4D4F; }
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
      color: #1a1a2e;
    }
  }
}

// 表单样式
.time-range {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .time-separator {
    color: #999;
  }
}

.sleep-duration {
  :deep(.el-tag) {
    font-size: 16px;
    padding: 8px 16px;
  }
}

.steps-input, .weight-input {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .steps-unit, .weight-unit {
    color: #666;
  }
}

@media (max-width: 1024px) {
  .stats-grid,
  .chart-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .checkin-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .checkin-status {
    flex-direction: column;
  }
}
</style>
