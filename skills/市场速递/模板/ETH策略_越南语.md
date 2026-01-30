# 越南语版 · ETH策略模板

```
NIVEX · CHIẾN LƯỢC ETH | {DD.MM.YYYY} {情绪emoji}

💡 {一句话定调 — 强调等BTC先}

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
- Chờ: BTC ổn định trên ${价格} (tiên quyết) | {条件2} | {条件3}

📝 Lưu ý
- {注意1 — ETH biến động mạnh hơn BTC}
- {注意2 — 等BTC先}
- BẢO VỆ VỐN > LỢI NHUẬN

⚠️⚠️ Phân tích chỉ mang tính tham khảo - {风险描述}!
Nivex | Để giao dịch trở nên đơn giản hơn
```

## ETH特殊规则
- 观察条件第一条必须是 BTC ổn định
- 注意事项必须提 ETH biến động mạnh hơn BTC 和 等BTC先
- ETH杠杆比BTC低一档，仓位更小
- ETH không bao giờ đảo chiều trước BTC

## 格式规则
- 总长度控制在25行左右
- **标题不加粗，纯文本输出**
- **所有条目用 `- ` 折号开头**
- **入场、止损、目标各占一行，不并排**
- 输出时用代码块包裹
- **不包含 Invalidation/Nếu tôi sai 板块**

## 参数差异
| 参数 | BTC | ETH |
|---|---|---|
| 顺势杠杆 | 5-10x | 5-8x |
| 逆势杠杆 | 3-5x | 3x |
| 仓位 | 3-5% | 2-3% |
| 极端行情 | 1-2% | 1% |

## 越南语写作铁律
- 禁止英文术语：BOS、CHoCH、MA、structure、bias等一律不用
- 禁止引用图表指标名称
- Short→"Bán"，Long→"Mua"，Trend following→"Theo xu hướng"，Reversal→"Đảo chiều"
- 策略描述用普通越南语，目标读者是普通投资者
