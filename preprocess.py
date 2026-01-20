
import re
import csv

# 读取文件内容
with open('yahooFNew.txt', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 提取所有<tr>标签内容
tr_pattern = r'<tr class="yf-1m2i7s2">(.*?)</tr>'
tr_matches = re.findall(tr_pattern, html_content, re.DOTALL)

csv_data = []
headers = ['date', 'open', 'high', 'low', 'close', 'adjclose', 'volume']
csv_data.append(headers)

# 处理每一行
for tr_content in tr_matches:
    # 跳过股息行
    if 'Dividend' in tr_content:
        continue
    
    # 提取<td>内容
    td_pattern = r'<td class="yf-1m2i7s2">([^<]+)</td>'
    td_matches = re.findall(td_pattern, tr_content)
    
    if len(td_matches) == 7:
        date, open_price, high, low, close, adj_close, volume = td_matches
        
        # 清理数据
        data_fields = [date.strip()]
        for field in [open_price, high, low, close, adj_close, volume]:
            cleaned = field.replace(',', '').strip()
            data_fields.append(cleaned)
        
        csv_data.append(data_fields)

# 保存CSV文件
with open('stock_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(csv_data)

print(f"转换完成！共 {len(csv_data)-1} 行数据已保存到 stock_data.csv")