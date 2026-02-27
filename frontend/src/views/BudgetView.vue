<template>
    <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
    </header>
  <div class="budget-page">
    <!-- 顶部统计卡片 -->
    <div class="budget-header">
      <div class="balance-card">
        <div class="balance-label">本月剩余预算</div>
        <div class="balance-amount">¥{{ remainingBalance }}</div>
        <div class="balance-progress">
          <el-progress 
            :percentage="budgetPercentage" 
            :stroke-width="12"
            :color="budgetPercentage > 80 ? '#FF4D4F' : budgetPercentage > 60 ? '#FAAD14' : '#52C41A'"
            :show-text="false"
          />
        </div>
        <div class="balance-info">
          <span>已支出: ¥{{ totalSpent }}</span>
          <span>预算总额: ¥{{ totalBudget }}</span>
        </div>
        <div class="budget-actions">
          <el-button size="small" @click="showBudgetDialog = true">
            <el-icon><Setting /></el-icon>
            设置预算
          </el-button>
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
        <el-input
          v-model="quickDesc"
          placeholder="添加备注（可选）"
          size="small"
          class="quick-desc"
        />
        <el-button type="primary" block @click="addExpense" :disabled="!quickAmount">
          确认支出
        </el-button>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="chart-section">
      <div class="chart-card">
        <h3>支出分布</h3>
        <div ref="pieChartRef" class="chart-container"></div>
      </div>
      <div class="chart-card">
        <h3>支出趋势</h3>
        <div ref="lineChartRef" class="chart-container"></div>
      </div>
    </div>
    
    <!-- 记录列表 -->
    <div class="records-section">
      <div class="section-header">
        <h3>消费记录</h3>
        <div class="header-actions">
          <el-radio-group v-model="timeRange" size="small" @change="loadExpenses">
            <el-radio-button label="week">本周</el-radio-button>
            <el-radio-button label="month">本月</el-radio-button>
            <el-radio-button label="all">全部</el-radio-button>
          </el-radio-group>
          <el-button size="small" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加记录
          </el-button>
        </div>
      </div>
      
      <el-table :data="expenseList" stripe v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" />
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">
            <span class="amount-minus">-¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="danger" link :icon="Delete" @click="deleteExpense(row.id)" />
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="total > pageSize"
        class="pagination"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 添加记录对话框 -->
    <el-dialog v-model="showAddDialog" title="添加消费记录" width="450px">
      <el-form :model="expenseForm" label-width="80px">
        <el-form-item label="金额">
          <el-input-number v-model="expenseForm.amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="expenseForm.category" placeholder="选择分类">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="expenseForm.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="expenseForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitExpense">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 设置预算对话框 -->
    <el-dialog v-model="showBudgetDialog" title="设置月度预算" width="400px">
      <el-form label-width="80px">
        <el-form-item label="预算金额">
          <el-input-number v-model="newBudget" :min="0" :step="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBudgetDialog = false">取消</el-button>
        <el-button type="primary" @click="saveBudget">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import HeaderView from "@/components/CHeaderView.vue";
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Plus, Setting } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getToken } from '@/utils/auth'

const loading = ref(false)
const showAddDialog = ref(false)
const showBudgetDialog = ref(false)
const quickAmount = ref('')
const quickDesc = ref('')
const selectedCategory = ref('food')
const timeRange = ref('month')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const newBudget = ref(1500)

// 图表容器
const pieChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()
let pieChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

// 分类定义
const categories = [
  { id: 'food', name: '餐饮', icon: 'Food' },
  { id: 'transport', name: '交通', icon: 'Bus' },
  { id: 'shopping', name: '购物', icon: 'ShoppingBag' },
  { id: 'entertainment', name: '娱乐', icon: 'Film' },
  { id: 'study', name: '学习', icon: 'Notebook' },
  { id: 'living', name: '住宿', icon: 'House' },
  { id: 'other', name: '其他', icon: 'More' },
]

// 数据
const expenseList = ref<any[]>([])
const totalBudget = ref(1500)
const totalSpent = ref(0)

const remainingBalance = computed(() => totalBudget.value - totalSpent.value)

const budgetPercentage = computed(() => {
  if (totalBudget.value === 0) return 0
  return Math.min(100, Math.round((totalSpent.value / totalBudget.value) * 100))
})

const expenseForm = ref({
  amount: 0,
  category: 'food',
  date: new Date().toISOString().split('T')[0],
  description: ''
})

const categoryMap: Record<string, string> = {
  food: '餐饮',
  transport: '交通',
  shopping: '购物',
  entertainment: '娱乐',
  study: '学习',
  living: '住宿',
  other: '其他'
}

const getCategoryType = (category: string) => {
  const typeMap: Record<string, string> = {
    food: 'warning',
    transport: '',
    shopping: 'success',
    entertainment: 'danger',
    study: 'primary',
    living: 'info',
    other: ''
  }
  return typeMap[category] || ''
}

// 加载消费记录
const loadExpenses = async () => {
  loading.value = true
  try {
    const token = getToken()
    if (!token) {
      ElMessage.error('请先登录')
      return
    }
    
    const response = await fetch('http://localhost:8000/api/expenses/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      expenseList.value = data.items || data || []
      total.value = expenseList.value.length
      
      // 计算总支出
      totalSpent.value = expenseList.value.reduce((sum: number, item: any) => sum + (item.amount || 0), 0)
      
      // 更新图表
      nextTick(() => {
        updateCharts()
      })
    }
  } catch (error) {
    console.error('加载消费记录失败:', error)
    // 使用模拟数据
    expenseList.value = generateMockData()
    totalSpent.value = expenseList.value.reduce((sum, item) => sum + item.amount, 0)
    updateCharts()
  } finally {
    loading.value = false
  }
}

// 生成模拟数据
const generateMockData = () => {
  const mockData = [
    { id: '1', date: '2024-01-15', category: 'food', description: '午餐', amount: 15 },
    { id: '2', date: '2024-01-15', category: 'transport', description: '地铁', amount: 4 },
    { id: '3', date: '2024-01-14', category: 'shopping', description: '文具', amount: 23 },
    { id: '4', date: '2024-01-13', category: 'entertainment', description: '电影', amount: 45 },
    { id: '5', date: '2024-01-12', category: 'food', description: '晚餐', amount: 20 },
    { id: '6', date: '2024-01-11', category: 'study', description: '教材', amount: 56 },
    { id: '7', date: '2024-01-10', category: 'food', description: '早餐', amount: 8 },
    { id: '8', date: '2024-01-09', category: 'living', description: '水电费', amount: 120 },
  ]
  return mockData
}

// 更新图表
const updateCharts = () => {
  // 饼图 - 分类统计
  const categoryData: Record<string, number> = {}
  expenseList.value.forEach(item => {
    const cat = item.category || 'other'
    categoryData[cat] = (categoryData[cat] || 0) + item.amount
  })
  
  const pieData = Object.entries(categoryData).map(([key, value]) => ({
    name: categoryMap[key] || key,
    value
  }))
  
  if (pieChartRef.value) {
    if (!pieChart) {
      pieChart = echarts.init(pieChartRef.value)
    }
    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
      legend: { bottom: '0%', left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: pieData,
        color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
      }]
    })
  }
  
  // 折线图 - 趋势
  const dateData: Record<string, number> = {}
  expenseList.value.forEach(item => {
    const date = item.date?.slice(0, 10) || ''
    dateData[date] = (dateData[date] || 0) + item.amount
  })
  
  const sortedDates = Object.keys(dateData).sort()
  const lineData = sortedDates.map(date => dateData[date])
  
  if (lineChartRef.value) {
    if (!lineChart) {
      lineChart = echarts.init(lineChartRef.value)
    }
    lineChart.setOption({
      tooltip: { trigger: 'axis', formatter: '¥{c}' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: sortedDates, axisLabel: { rotate: 45 } },
      yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
      series: [{
        data: lineData,
        type: 'line',
        smooth: true,
        areaStyle: { color: 'rgba(54, 116, 251, 0.2)' },
        itemStyle: { color: '#3674FB' },
        lineStyle: { width: 2 }
      }]
    })
  }
}

// 添加支出
const addExpense = async () => {
  if (!quickAmount.value || Number(quickAmount.value) <= 0) {
    ElMessage.warning('请输入有效金额')
    return
  }
  
  const newExpense = {
    amount: Number(quickAmount.value),
    category: selectedCategory.value,
    description: quickDesc.value || categoryMap[selectedCategory.value],
    date: new Date().toISOString().split('T')[0]
  }
  
  try {
    const token = getToken()
    if (token) {
      await fetch('http://localhost:8000/api/expenses/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newExpense)
      })
    }
  } catch (error) {
    console.log('使用本地模拟数据')
  }
  
  // 添加到列表
  expenseList.value.unshift({
    id: Date.now().toString(),
    ...newExpense
  })
  
  totalSpent.value += Number(quickAmount.value)
  total.value = expenseList.value.length
  
  quickAmount.value = ''
  quickDesc.value = ''
  
  ElMessage.success('添加成功')
  updateCharts()
}

// 提交消费记录
const submitExpense = async () => {
  if (expenseForm.value.amount <= 0) {
    ElMessage.warning('请输入有效金额')
    return
  }
  
  try {
    const token = getToken()
    if (token) {
      await fetch('http://localhost:8000/api/expenses/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(expenseForm.value)
      })
    }
  } catch (error) {
    console.log('使用本地模拟数据')
  }
  
  expenseList.value.unshift({
    id: Date.now().toString(),
    ...expenseForm.value
  })
  
  totalSpent.value += expenseForm.value.amount
  total.value = expenseList.value.length
  
  showAddDialog.value = false
  ElMessage.success('添加成功')
  updateCharts()
  
  // 重置表单
  expenseForm.value = {
    amount: 0,
    category: 'food',
    date: new Date().toISOString().split('T')[0],
    description: ''
  }
}

// 删除消费记录
const deleteExpense = async (id: string) => {
  const index = expenseList.value.findIndex(item => item.id === id)
  if (index > -1) {
    const amount = expenseList.value[index].amount
    expenseList.value.splice(index, 1)
    totalSpent.value -= amount
    total.value = expenseList.value.length
    ElMessage.success('删除成功')
    updateCharts()
  }
}

// 保存预算
const saveBudget = () => {
  totalBudget.value = newBudget.value
  showBudgetDialog.value = false
  ElMessage.success('预算设置成功')
}

// 分页
const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 窗口大小变化时重新调整图表
const handleResize = () => {
  pieChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  loadExpenses()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.budget-page {
  padding: 24px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
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
  padding: 28px;
  color: #fff;
  position: relative;
  
  .balance-label {
    font-size: 14px;
    opacity: 0.9;
  }
  
  .balance-amount {
    font-size: 42px;
    font-weight: 700;
    margin: 12px 0 16px;
  }
  
  .balance-progress {
    margin-bottom: 12px;
    
    :deep(.el-progress-bar__outer) {
      background: rgba(255, 255, 255, 0.2);
    }
  }
  
  .balance-info {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    opacity: 0.9;
  }
  
  .budget-actions {
    position: absolute;
    top: 20px;
    right: 20px;
    
    .el-button {
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: #fff;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
      }
    }
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
    color: #1a1a2e;
  }
  
  .quick-amount {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
    
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
      background: transparent;
      
      &::placeholder {
        color: #ccc;
      }
    }
  }
  
  .category-select {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 16px;
    
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
      border: 1px solid #eee;
      
      &:hover {
        background: #f5f7fa;
        border-color: #ddd;
      }
      
      &.active {
        background: #e6f7ff;
        border-color: #1890ff;
        color: #1890ff;
      }
      
      .el-icon {
        font-size: 22px;
        margin-bottom: 4px;
      }
    }
  }
  
  .quick-desc {
    margin-bottom: 16px;
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
    height: 280px;
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
    
    .header-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
  
  .amount-minus {
    color: #FF4D4F;
    font-weight: 600;
    font-size: 14px;
  }
  
  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}

@media (max-width: 1024px) {
  .budget-header,
  .chart-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .quick-add .category-select {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
