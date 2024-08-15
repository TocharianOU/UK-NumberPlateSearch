import string
import itertools
import json
import requests
import random
import os

ES_URL = "http://127.0.0.1:9200/suffix/_bulk"
CACHE_FILE = "suffix_cache.json"
BULK_SIZE = 1000

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

def generate_suffix_plate(last_state=None):
    letters = string.ascii_uppercase
    suffix_letters = list(itertools.product(letters, repeat=3))  # 生成所有可能的前缀（AAA到ZZZ）
    numbers = range(1, 1000)  # 数字从1到999

    start_letter_index = 0
    start_number_index = 0
    suffix_index = 0

    if last_state:
        prefix_letter = last_state['prefix']
        prefix_number = last_state['number']
        suffix = last_state['suffix_letter']
        
        # 查找从上次中断处开始的字母、数字和后缀索引
        start_letter_index = suffix_letters.index(tuple(prefix_letter))
        start_number_index = numbers.index(prefix_number)
        suffix_index = letters.index(suffix)
    else:
        prefix_letter = 'AAA'

    for prefix in suffix_letters[start_letter_index:]:
        for number in numbers[start_number_index:]:
            for suffix in letters[suffix_index:]:
                suf = ''.join(prefix)
                
                price = random.uniform(500, 5000)  # 随机生成价格
                discount_percentage = random.uniform(0, 50)  # 随机生成打折百分比
                
                plate = {
                    "plateNumber": f"{suf} {number}{suffix}",
                    "originalNumber": f"{suf}{number}{suffix}",
                    "plateType": f"suffix_{len(str(number))}_num",
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
        gen = generate_suffix_plate(last_state)
        
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
        prefix = last_plate.split()[0]  # 字母前缀
        number_suffix = last_plate.split()[1]  # 数字和后缀
        prefix_number = int(number_suffix[:-1])  # 数字部分
        suffix_letter = number_suffix[-1]  # 字母后缀

        last_state = {
            "prefix": prefix,
            "number": prefix_number,
            "suffix_letter": suffix_letter
        }

        save_cache(last_state)

if __name__ == "__main__":
    main()
