import string
import itertools
import json
import requests
import random
import os

ES_URL = "http://127.0.0.1:9200/prefix/_bulk"
CACHE_FILE = "prefix_cache.json"
BULK_SIZE = 1000

# 自定义的数字迭代区间
PREFIX_NUMBERS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 40, 44, 50, 55, 60, 66, 
    70, 77, 80, 88, 90, 99, 100, 111, 123, 155, 200, 222, 300, 321, 333, 
    400, 444, 500, 555, 600, 666, 700, 777, 800, 888, 900, 999
]

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

def generate_prefix_plate(last_state=None):
    letters = string.ascii_uppercase
    suffix_letters = list(itertools.product(letters, repeat=3))  # 生成所有可能的后缀

    start_letter_index = 0
    start_number_index = 0
    suffix_index = 0

    if last_state:
        prefix_letter = last_state['prefix_letter']
        prefix_number = last_state['prefix_number']
        suffix = last_state['suffix']
        
        # 查找从上次中断处开始的字母、数字和后缀索引
        start_letter_index = letters.index(prefix_letter)
        start_number_index = PREFIX_NUMBERS.index(prefix_number)
        suffix_index = suffix_letters.index(tuple(suffix))
    else:
        prefix_letter = 'A'

    for letter in letters[start_letter_index:]:
        for number in PREFIX_NUMBERS[start_number_index:]:
            for suffix in suffix_letters[suffix_index:]:
                suf = ''.join(suffix)
                
                price = random.uniform(500, 5000)  # 随机生成价格
                discount_percentage = random.uniform(0, 50)  # 随机生成打折百分比
                
                plate = {
                    "plateNumber": f"{letter}{number} {suf}",
                    "originalNumber": f"{letter}{number}{suf}",
                    "plateType": f"prefix_{len(str(number))}_num",
                    "currency": "GBP",
                    "price": round(price, 2),  # 保留两位小数
                    "discountPercentage": round(discount_percentage, 2),  # 保留两位小数
                    "isAvailable": False
                }
                
                #print(plate['plateNumber'])  # 打印生成的车牌数据
                
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
        gen = generate_prefix_plate(last_state)
        
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
        
        # 解析plateNumber以提取prefix_letter、prefix_number和suffix
        prefix_letter = last_plate[0]  # 第一个字母
        rest = last_plate[1:].split()  # 剩余部分拆分为数字和后缀
        prefix_number = int(rest[0])  # 数字部分
        suffix = rest[1]  # 字母后缀

        last_state = {
            "prefix_letter": prefix_letter,
            "prefix_number": prefix_number,
            "suffix": suffix
        }

        save_cache(last_state)

if __name__ == "__main__":
    main()
