def format_numbers(numbers):
    # 将输入的数字字符串分割成每两个字符一组
    formatted_numbers = [numbers[i:i+2] for i in range(0, len(numbers), 2)]
    
    # 添加前缀0x和逗号
    formatted_numbers = [f"0x{num}" for num in formatted_numbers]
    
    # 将格式化后的数字列表转换为字符串，并用逗号间隔
    result = ",".join(formatted_numbers)
    
    return result

# 示例输入
input = "350080DC00F0300300000002790011020400000000000015000000000000224A20250114142937584012215840FFFFFFFF000000000000"

formatted_result = format_numbers(input)
print(f'{formatted_result},')
print(f'len = {len(input) / 2}')
