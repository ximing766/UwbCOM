import csv

filename = './dist/Distance_content.txt'
output_filename = 'Distance_content.csv'

with open(filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()

values = []
for line in lines:
    parts = line.split(':')
    if len(parts) > 2:
        value = parts[2].strip().replace('<cm>', '').replace(' ', '') 
        values.append(value)
        # Insert column names
values.insert(0, 'master_D,slaver_D,gate_D')

# 将结果写入 CSV 文件
with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    for value in values:
        csvwriter.writerow([value])

print(values)