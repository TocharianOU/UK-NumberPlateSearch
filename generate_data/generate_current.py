import string
import itertools
import json
import requests
import random
import os

ES_URL = "http://127.0.0.1:9200/current/_bulk"
CACHE_FILE = "current_cache.json"
BULK_SIZE = 1000

# 当前样式的数字迭代序列
CURRENT_NUMBERS = [
    51, 2, 52, 3, 53, 4, 54, 5, 55, 6, 56, 7, 57, 8, 58, 9, 59, 
    10, 60, 11, 61, 12, 62, 13, 63, 14, 64, 15, 65, 16, 66, 17, 
    67, 18, 68, 19, 69, 20, 70, 21, 71, 22, 72, 23, 73, 24, 74
]

CURRENT_NUMBERS = sorted(CURRENT_NUMBERS)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

def generate_current_plate(last_state=None):
    letters = string.ascii_uppercase
    suffix_letters = list(itertools.product(letters, repeat=3))  # 生成所有可能的后缀（AAA到ZZZ）

    start_prefix_index = 0
    start_number_index = 0
    suffix_index = 0

    if last_state:
        prefix = last_state['prefix']
        prefix_number = last_state['prefix_number']
        suffix = last_state['suffix']
        
        # 查找从上次中断处开始的字母、数字和后缀索引
        start_prefix_index = letters.index(prefix[0]) * 26 + letters.index(prefix[1])
        start_number_index = CURRENT_NUMBERS.index(prefix_number)
        suffix_index = suffix_letters.index(tuple(suffix))
    else:
        prefix = 'AA'

    for prefix in itertools.product(letters, repeat=2):
        prefix = ''.join(prefix)
        for number in CURRENT_NUMBERS[start_number_index:]:
            for suffix in suffix_letters[suffix_index:]:
                suf = ''.join(suffix)
                
                price = random.uniform(500, 5000)  # 随机生成价格
                discount_percentage = random.uniform(0, 50)  # 随机生成打折百分比
                
                plate = {
                    "plateNumber": f"{prefix}{number} {suf}",
                    "originalNumber": f"{prefix}{number}{suf}",
                    "plateType": f"current_{len(str(number))}_num",
                    "currency": "GBP",
                    "price": round(price, 2),  # 保留两位小数
                    "discountPercentage": round(discount_percentage, 2),  # 保留两位小数
                    "isAvailable": False
                }
                
               # print(plate['plateNumber'])  # 打印生成的车牌数据
                
                yield plate
            
            suffix_index = 0  # 当数字变化时，重置后缀为初始值
            
        start_number_index = 0  # 当字母变化时，重置数字和后缀为初始值

def bulk_write_to_es(data):
    headers = {'Content-Type': 'application/json'}
    bulk_data = ''
    for entry in data:
        bulk_data += json.dumps({"index": {"_id": entry["plateNumber"]}}) + "\n"
        bulk_data += json.dumps(entry) + "\n"

    response = requests.post(ES_URL, headers=headers, data=bulk_data)
    response.raise_for_status()

def main():
    last_state = load_cache()
    
    while True:
        generated_data = []
        gen = generate_current_plate(last_state)
        
        while len(generated_data) < BULK_SIZE:
            try:
                generated_data.append(next(gen))
            except StopIteration:
                break
        
        if not generated_data:
            print("All possible plates generated.")
            break
        
        bulk_write_to_es(generated_data)
        last_plate = generated_data[-1]['plateNumber']
        
        # 解析plateNumber以提取prefix、number和suffix_letter
        prefix = last_plate[:2]  # 字母前缀
        number = int(last_plate[2:4])  # 两位数字部分
        suffix = last_plate.split()[1]  # 三字母后缀

        last_state = {
            "prefix": prefix,
            "prefix_number": number,
            "suffix": suffix
        }

        save_cache(last_state)

if __name__ == "__main__":
    main()
 