# 🚀 Railway Resource Optimization Guide

## 📊 Resource Configuration Options

### 🎯 Hobby Tier ($5/month)
**File**: `infra/railway.hobby.toml`
- **Memory**: 512MB RAM
- **CPU**: 0.25 core
- **Brain Interval**: 10 minutes (conservative)
- **Rate Limit**: 100 requests/hour
- **Cache TTL**: 10 minutes
- **DB Pool**: 5 connections

### 🚀 Production Tier (~$20/month)
**File**: `infra/railway.production.toml`
- **Memory**: 1GB RAM
- **CPU**: 0.5 core
- **Brain Interval**: 5 minutes (standard)
- **Rate Limit**: 1000 requests/hour
- **Cache TTL**: 5 minutes
- **DB Pool**: 10 connections

## 🔧 Resource Management API

### **Start Resource Monitoring**
```bash
curl -X POST https://railway-engine-production.up.railway.app/api/admin/resources/monitoring/start
```

### **Get Current Resource Status**
```bash
curl https://railway-engine-production.up.railway.app/api/admin/resources
```

### **Get Performance Baseline**
```bash
curl https://railway-engine-production.up.railway.app/api/admin/resources/baseline
```

### **Export Resource Metrics**
```bash
curl https://railway-engine-production.up.railway.app/api/admin/resources/export
```

## 📈 Resource Monitoring Features

### **Real-time Metrics**
- **Memory Usage**: Current RAM consumption
- **CPU Usage**: Processor utilization
- **Disk Usage**: Storage consumption
- **Network I/O**: Data transfer metrics
- **Process Count**: Active processes
- **GC Stats**: Garbage collection metrics

### **Credit Usage Estimation**
- **Hourly Cost**: Based on memory/CPU usage
- **Monthly Projection**: 30-day cost estimate
- **Budget Tracking**: $5/month budget monitoring
- **Remaining Budget**: Credit balance calculation

### **Optimization Recommendations**
- **Memory Alerts**: High usage warnings
- **CPU Alerts**: High utilization alerts
- **Credit Alerts**: Budget overrun warnings
- **Memory Leak Detection**: Uncollectable objects

## 🎯 Performance Baselines

### **Hobby Tier Targets**
- **Memory Usage**: < 400MB average
- **CPU Usage**: < 50% average
- **API Latency**: P95 < 800ms
- **Brain Cycle Time**: < 30 seconds
- **Monthly Cost**: $5.00

### **Production Tier Targets**
- **Memory Usage**: < 800MB average
- **CPU Usage**: < 70% average
- **API Latency**: P95 < 500ms
- **Brain Cycle Time**: < 20 seconds
- **Monthly Cost**: ~$20.00

## 🔍 Verification Suite Integration

### **Resource-Aware Verification**
The verification engine now includes resource monitoring:

```bash
# Run verification with resource tracking
curl https://railway-engine-production.up.railway.app/api/admin/verification
```

### **Baseline Locking Process**
1. **Deploy with resource limits**
2. **Start resource monitoring**
3. **Run verification suite 3x**
4. **Lock baseline metrics**
5. **Monitor for deviations**

## 📊 Expected Resource Metrics

### **Normal Operation (Hobby Tier)**
```json
{
  "memory_usage_mb": 280,
  "memory_percent": 55,
  "cpu_percent": 25,
  "process_count": 12,
  "thread_count": 8,
  "gc_collections": 45,
  "gc_uncollectable": 2,
  "cost_per_hour": 0.007,
  "projected_usage": 5.02
}
```

### **High Load (Hobby Tier)**
```json
{
  "memory_usage_mb": 420,
  "memory_percent": 82,
  "cpu_percent": 65,
  "process_count": 18,
  "thread_count": 12,
  "gc_collections": 89,
  "gc_uncollectable": 15,
  "cost_per_hour": 0.008,
  "projected_usage": 5.76
}
```

## ⚡ Optimization Strategies

### **Memory Optimization**
- **Aggressive GC**: Lower GC thresholds
- **Cache Management**: Regular cache clearing
- **Connection Pooling**: Optimize DB connections
- **Process Cleanup**: Remove unused processes

### **CPU Optimization**
- **Background Tasks**: Optimize scheduler intervals
- **API Optimization**: Reduce response times
- **Database Queries**: Optimize slow queries
- **Caching**: Reduce database hits

### **Credit Optimization**
- **Resource Monitoring**: Continuous tracking
- **Alert System**: Budget warnings
- **Auto-scaling**: Adjust resources based on load
- **Cost Control**: Feature toggles for expensive operations

## 🚨 Resource Alerts

### **Memory Alerts**
- **Warning**: > 400MB usage
- **Critical**: > 500MB usage
- **Action**: Enable aggressive GC

### **CPU Alerts**
- **Warning**: > 70% usage
- **Critical**: > 85% usage
- **Action**: Optimize background tasks

### **Credit Alerts**
- **Warning**: Projected > $6/month
- **Critical**: Projected > $8/month
- **Action**: Reduce resource usage

## 🔄 Continuous Monitoring

### **Automatic Monitoring**
The brain automatically starts resource monitoring when:
- Brain loop initializes
- Resource thresholds exceeded
- Manual monitoring requested

### **Metrics History**
- **Retention**: Last 1000 data points
- **Export**: JSON format available
- **Baseline**: Automatic baseline calculation
- **Trends**: Usage pattern analysis

## 📋 Deployment Checklist

### **Before Deployment**
- [ ] Choose appropriate resource config
- [ ] Set resource limits in Railway
- [ ] Configure environment variables
- [ ] Test resource monitoring

### **After Deployment**
- [ ] Start resource monitoring
- [ ] Run verification suite
- [ ] Lock performance baseline
- [ ] Set up alert thresholds

### **Ongoing Monitoring**
- [ ] Check resource usage daily
- [ ] Monitor credit consumption
- [ ] Review optimization recommendations
- [ ] Adjust resources as needed

## 🎯 Quick Start Commands

### **1. Deploy with Hobby Resources**
```bash
# Copy hobby config
cp infra/railway.hobby.toml railway.toml
git add railway.toml
git commit -m "Configure for hobby tier resources"
git push origin main
```

### **2. Start Resource Monitoring**
```bash
curl -X POST https://railway-engine-production.up.railway.app/api/admin/resources/monitoring/start
```

### **3. Run Verification Suite**
```bash
curl https://railway-engine-production.up.railway.app/api/admin/verification
```

### **4. Check Resource Status**
```bash
curl https://railway-engine-production.up.railway.app/api/admin/resources
```

### **5. Lock Performance Baseline**
```bash
curl https://railway-engine-production.up.railway.app/api/admin/resources/baseline
```

## 📈 Success Metrics

### **Resource Efficiency**
- **Memory Utilization**: 70-80% of allocated
- **CPU Utilization**: 40-60% average
- **Credit Usage**: Within $5 budget
- **API Performance**: P95 < target latency

### **Verification Results**
- **Brain Stress Test**: 100+ cycles passed
- **Performance Benchmark**: Latency targets met
- **Resource Limits**: No threshold breaches
- **Cost Control**: Budget maintained

**🎉 Your system is now optimized for Railway resource limits with comprehensive monitoring!**
