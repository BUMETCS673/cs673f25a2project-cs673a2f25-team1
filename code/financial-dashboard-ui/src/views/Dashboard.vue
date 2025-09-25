<template>
  <div class="dashboard">
    <!-- Top Bar -->
    <TopBar />
    
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="main-content">
      <!-- Header -->
      <div class="dashboard-header">
        <h1>Asset Management Anomaly Detection</h1>
        <div class="header-actions">
          <button class="btn-primary">View Full Report</button>
        </div>
      </div>
      <!-- Metrics Cards -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon purple">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">Household</h3>
            <p class="metric-value">96</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon orange">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M16 4H18C18.5304 4 19.0391 4.21071 19.4142 4.58579C19.7893 4.96086 20 5.46957 20 6V20C20 20.5304 19.7893 21.0391 19.4142 21.4142C19.0391 21.7893 18.5304 22 18 22H6C5.46957 22 4.96086 21.7893 4.58579 21.4142C4.21071 21.0391 4 20.5304 4 20V6C4 5.46957 4.21071 4.96086 4.58579 4.58579C4.96086 4.21071 5.46957 4 6 4H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 2V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 10H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">Clients</h3>
            <p class="metric-value">3,650</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon blue">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2"/>
              <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">Projects</h3>
            <p class="metric-value">356</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon red">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">Events</h3>
            <p class="metric-value">696</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon green">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
            </svg>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">Payroll</h3>
            <p class="metric-value">$96k</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon purple">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="metric-content">
            <h3 class="metric-title">Reports</h3>
            <p class="metric-value">59</p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <!-- Revenue Updates Chart -->
        <div class="chart-card large">
          <div class="chart-header">
            <div class="chart-title">
              <h3>Revenue Updates</h3>
              <p>Overview of Profit</p>
            </div>
            <div class="chart-controls">
              <select v-model="selectedMonth" class="month-selector">
                <option value="march">March 2024</option>
                <option value="april">April 2024</option>
                <option value="may">May 2024</option>
              </select>
            </div>
          </div>
          <div class="chart-container">
            <v-chart 
              class="chart" 
              :option="profitExpensesOption" 
              autoresize
            />
          </div>
          <div class="chart-summary">
            <div class="summary-item">
              <div class="summary-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M3 3H21L19 21H5L3 3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="summary-content">
                <span class="summary-label">Total Earnings</span>
                <span class="summary-value">$63,489.50</span>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-dot blue"></div>
              <div class="summary-content">
                <span class="summary-label">Earnings this month</span>
                <span class="summary-value">$48,820</span>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-dot teal"></div>
              <div class="summary-content">
                <span class="summary-label">Expense this month</span>
                <span class="summary-value">$26,498</span>
              </div>
            </div>
            <button class="view-report-btn">View Full Report</button>
          </div>
        </div>

        <!-- Yearly Breakup Chart -->
        <div class="chart-card">
          <div class="chart-header">
              <h3>Yearly Breakup</h3>
            <div class="chart-value">$36,358</div>
          </div>
          <div class="chart-container">
            <v-chart 
              class="chart" 
              :option="trafficOption" 
              autoresize
            />
          </div>
          <div class="chart-summary">
            <div class="summary-item">
                <span class="summary-label">Change</span>
                <span class="summary-value positive">+9% last year</span>
            </div>
            <div class="chart-legend">
              <div class="legend-item">
                <div class="legend-dot blue"></div>
                <span>2024</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot gray"></div>
                <span>2024</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="bottom-section">
        <!-- Monthly Earnings -->
        <div class="chart-card">
          <div class="chart-header">
              <h3>Monthly Earnings</h3>
            <div class="chart-value">$6,820</div>
          </div>
          <div class="chart-container">
            <v-chart 
              class="chart" 
              :option="productSalesOption" 
              autoresize
            />
          </div>
          <div class="chart-summary">
            <div class="summary-item">
                <span class="summary-label">Change</span>
                <span class="summary-value negative">-9% last year</span>
            </div>
          </div>
        </div>

        <!-- Additional Cards -->
        <div class="additional-cards">
          <div class="chart-card">
            <div class="chart-header">
              <h3>Employee Salary</h3>
              <p>Every month</p>
            </div>
            <div class="card-content">
              <div class="salary-chart">
                <div class="salary-bar" style="width: 70%"></div>
              </div>
              <div class="salary-info">
                <span class="salary-amount">$45,000</span>
                <span class="salary-period">Average Monthly</span>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h3>Customers</h3>
              <div class="chart-value">36,358</div>
            </div>
            <div class="chart-summary">
              <div class="summary-item">
                <span class="summary-label">Change</span>
                <span class="summary-value negative">-9%</span>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h3>Projects</h3>
              <div class="chart-value">78,298</div>
            </div>
            <div class="chart-summary">
              <div class="summary-item">
                <span class="summary-label">Change</span>
                <span class="summary-value positive">+9%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import Sidebar from '@/components/Sidebar.vue'
import TopBar from '@/components/TopBar.vue'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  BarChart,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 响应式数据
const selectedMonth = ref('march')

// 利润与支出图表配置
const profitExpensesOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {
      color: '#fff'
    }
  },
  legend: {
    show: false
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['16/08', '17/08', '18/08', '19/08', '20/08', '21/08'],
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#6B7280',
      fontSize: 12
    }
  },
  yAxis: {
    type: 'value',
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#6B7280',
      fontSize: 12
    },
    splitLine: {
      lineStyle: {
        color: '#F3F4F6'
      }
    },
    min: -5,
    max: 5
  },
  series: [
    {
      name: 'Profit',
      type: 'bar',
      data: [2.5, 3.2, 1.8, 4.1, 2.9, 3.7],
      itemStyle: {
        color: '#3B82F6',
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '60%'
    },
    {
      name: 'Expenses',
      type: 'bar',
      data: [-1.2, -2.1, -0.8, -1.9, -1.5, -2.3],
      itemStyle: {
        color: '#EF4444',
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '60%'
    }
  ]
}))

// 流量分布图表配置
const trafficOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {
      color: '#fff'
    }
  },
  legend: {
    show: false
  },
  series: [
    {
      name: 'Traffic Distribution',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 65, name: 'Desktop', itemStyle: { color: '#3B82F6' } },
        { value: 25, name: 'Mobile', itemStyle: { color: '#10B981' } },
        { value: 10, name: 'Tablet', itemStyle: { color: '#F59E0B' } }
      ]
    }
  ]
}))

// 产品销售图表配置
const productSalesOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {
      color: '#fff'
    }
  },
  legend: {
    show: false
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#6B7280',
      fontSize: 12
    }
  },
  yAxis: {
    type: 'value',
    axisLine: {
      show: false
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#6B7280',
      fontSize: 12
    },
    splitLine: {
      lineStyle: {
        color: '#F3F4F6'
      }
    }
  },
  series: [
    {
      name: 'Sales',
      type: 'line',
      data: [1200, 1900, 3000, 5000, 2000, 3000, 4500, 6800],
      smooth: true,
      lineStyle: {
        color: '#3B82F6',
        width: 3
      },
      itemStyle: {
        color: '#3B82F6',
        borderColor: '#fff',
        borderWidth: 2
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ]
        }
      },
      symbol: 'circle',
      symbolSize: 6,
      emphasis: {
        scale: true,
        scaleSize: 8
      }
    }
  ]
}))
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
}

.main-content {
  margin-left: 280px;
  margin-top: 70px;
  padding: 24px;
  min-height: calc(100vh - 70px);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background-color: #3B82F6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2563EB;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.metric-icon.purple {
  background: linear-gradient(135deg, #8B5CF6, #7C3AED);
}

.metric-icon.orange {
  background: linear-gradient(135deg, #F59E0B, #D97706);
}

.metric-icon.blue {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
}

.metric-icon.red {
  background: linear-gradient(135deg, #EF4444, #DC2626);
}

.metric-icon.green {
  background: linear-gradient(135deg, #10B981, #059669);
}

.metric-content {
  flex: 1;
}

.metric-title {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.chart-card.large {
  grid-column: 1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.chart-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.chart-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.chart-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.month-selector {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
}

.month-selector:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.chart-container {
  height: 300px;
  margin-bottom: 20px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-icon {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.summary-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.summary-dot.blue {
  background: #3B82F6;
}

.summary-dot.teal {
  background: #06B6D4;
}

.summary-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.summary-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.summary-value.positive {
  color: #10B981;
}

.summary-value.negative {
  color: #EF4444;
}

.view-report-btn {
  background: #3B82F6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 8px;
}

.view-report-btn:hover {
  background: #2563EB;
}

.chart-legend {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-dot.blue {
  background: #3B82F6;
}

.legend-dot.gray {
  background: #9ca3af;
}

.bottom-section {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
}

.additional-cards {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.salary-chart {
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.salary-bar {
  height: 100%;
  background: linear-gradient(90deg, #3B82F6, #1D4ED8);
  border-radius: 4px;
}

.salary-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.salary-amount {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.salary-period {
  font-size: 12px;
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .bottom-section {
    grid-template-columns: 1fr;
  }
  
  .additional-cards {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 16px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .additional-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>