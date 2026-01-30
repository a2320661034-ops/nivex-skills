# 越南语版 · BTC策略模板

```
NIVEX · CHIẾN LƯỢC BTC | {DD.MM.YYYY} {情绪emoji}

💡 {一句话定调}

Nhận định {情绪emoji}
- Xu hướng: {趋势} | Giá: ${价格} | Chiến lược: {一词概括}

Các mốc giá quan trọng
- Kháng cự: ${R1} ({%}) → ${R2} ({%}) → ${R3} ({%})
- ▸ Giá hiện tại: ${价格}
- Hỗ trợ: ${S1} ({%}) → ${S2} ({%}) → ${S3} ({%})
- Mốc then chốt: ${关键位1} {场景} | ${关键位2} {场景}

📉 Bán 🔴 ({类型})
- Vào lệnh: ${入场}
- Cắt lỗ: ${止损}
- Mục tiêu: ${目标1} → ${目标2} → ${目标3}
- Đòn bẩy: {X}x | Khối lượng: {Y}%

📈 Mua 🟢 ({类型})
- Vào lệnh: ${入场}
- Cắt lỗ: ${止损}
- Mục tiêu: ${目标1} → ${目标2} → ${目标3}
- Đòn bẩy: {X}x | Khối lượng: {Y}%

⏸️ Quan sát ({推荐强度})
- Chờ: {条件1} | {条件2} | {条件3}

📝 Lưu ý
- {注意1}
- {注意2}
- BẢO VỆ VỐN > LỢI NHUẬN

⚠️⚠️ Phân tích chỉ mang tính tham khảo - {风险描述}!
Nivex | Để giao dịch trở nên đơn giản hơn
```

## 格式规则
- 总长度控制在25行左右
- **标题不加粗，纯文本输出**
- **所有条目用 `- ` 折号开头**
- **入场、止损、目标各占一行，不并排**
- 输出时用代码块包裹
- 注意事项最多2条+保护本金
- **不包含 Invalidation/Nếu tôi sai 板块**

## 策略逻辑
- 🔴🔴: 主策略=不做，Short=trend following高风险，Long=仅expert
- 🔴: Short=主策略，Long=counter-trend
- 🟡: Range trading，Short/Long均等
- 🟢: Long=主策略，Short=counter-trend
- 🟢🟢: 主策略=aggressive long，Short=仅expert

## 止损/目标
- 顺势SL: 1-2% | 逆势SL: 2-3%
- TP1: 2-3% | TP2: 4-5% | TP3: 6-8%

## 越南语写作铁律
- 禁止英文术语：BOS、CHoCH、MA、structure、bias等一律不用
- 禁止引用图表指标名称
- Short→"Bán"，Long→"Mua"，Trend following→"Theo xu hướng"，Reversal→"Đảo chiều"
- 策略描述用普通越南语，目标读者是普通投资者
