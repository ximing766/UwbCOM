def format_numbers(numbers):
    # 将输入的数字字符串分割成每两个字符一组
    formatted_numbers = [numbers[i:i+2] for i in range(0, len(numbers), 2)]
    
    # 添加前缀0x和逗号
    formatted_numbers = [f"0x{num}" for num in formatted_numbers]
    
    # 将格式化后的数字列表转换为字符串，并用逗号间隔
    result = ",".join(formatted_numbers)
    
    return result

# 示例输入
input_numbers = "805401000F0000000120240821185844B2568CE508"

formatted_result = format_numbers(input_numbers)
print(f'{formatted_result},')
print(f'len = {len(input_numbers) / 2}')
