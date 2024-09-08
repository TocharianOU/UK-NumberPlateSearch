import string
import itertools
import json
import requests
import random
import os

ES_URL = "http://127.0.0.1:9200/current/_bulk"
ES_INDEX_URL = "http://127.0.0.1:9200/current"
CACHE_FILE = "./current_cache.json"
BULK_SIZE = 1000

# 当前样式的数字迭代序列
CURRENT_NUMBERS = [
    51, 2, 52, 3, 53, 4, 54, 5, 55, 6, 56, 7, 57, 8, 58, 9, 59, 
    10, 60, 11, 61, 12, 62, 13, 63, 14, 64, 15, 65, 16, 66, 17, 
    67, 18, 68, 19, 69, 20, 70, 21, 71, 22, 72, 23, 73, 24, 74
]

CURRENT_NUMBERS = sorted(CURRENT_NUMBERS)

# 索引配置
INDEX_CONFIG = {
    "mappings": {
      "properties": {
        "currency": {
          "type": "keyword"
        },
        "discountPercentage": {
          "type": "float"
        },
        "isAvailable": {
          "type": "boolean"
        },
        "originalNumber": {
          "type": "keyword"
        },
        "plateNumber": {
          "type": "text",
          "store": True,
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            },
            "phonetic": {
              "type": "text",
              "analyzer": "phonetic_analyzer_soundex"
            }
          },
          "analyzer": "letters_only_analyzer_ngram",
          "fielddata": True
        },
        "plateType": {
          "type": "keyword"
        },
        "price": {
          "type": "float"
        }
      }
    },
    "settings": {
      "index": {
        "max_ngram_diff": "4",
        "routing": {
          "allocation": {
            "include": {
              "_tier_preference": "data_content"
            }
          }
        },
        "number_of_shards": "1",
        "analysis": {
          "filter": {
            "soundex_filter": {
              "replace": "false",
              "type": "phonetic",
              "encoder": "soundex"
            }
          },
          "char_filter": {
            "first_token_filter": {
              "pattern": """(\S+)(\s+\S+)?""",
              "type": "pattern_replace",
              "replacement": "$1"
            },
            "remove_spaces_filter": {
              "pattern": """\s+""",
              "type": "pattern_replace",
              "replacement": ""
            },
            "remove_digits_and_spaces_filter": {
              "pattern": """[\d\s]+""",
              "type": "pattern_replace",
              "replacement": ""
            },
            "character_replacement_filter": {
              "type": "mapping",
              "mappings": [
                "A => α",
                "4 => α",
                "B => β",
                "8 => β",
                "3 => β",
                "D => δ",
                "O => δ",
                "0 => δ",
                "E => ε",
                "G => γ",
                "6 => γ",
                "C => ξ",
                "I => ι",
                "1 => ι",
                "L => ι",
                "Q => ο",
                "S => σ",
                "5 => σ",
                "Z => ζ",
                "2 => ζ",
                "T => τ",
                "7 => τ",
                "P => π",
                "R => π",
                "U => μ",
                "V => μ",
                "Y => ν",
                "M => μ",
                "N => μ",
                "K => κ",
                "X => κ"
              ]
            },
            "second_token_filter": {
              "pattern": """(\S+\s+)?(\S+)""",
              "type": "pattern_replace",
              "replacement": "$2"
            }
          },
          "analyzer": {
            "phonetic_analyzer_soundex": {
              "filter": [
                "lowercase",
                "soundex_filter"
              ],
              "char_filter": [
                "remove_digits_and_spaces_filter"
              ],
              "type": "custom",
              "tokenizer": "whitespace_tokenizer"
            },
            "letters_only_analyzer_ngram": {
              "type": "custom",
              "char_filter": [
                "remove_digits_and_spaces_filter",
                "character_replacement_filter"
              ],
              "tokenizer": "ngram_tokenizer"
            }
          },
          "tokenizer": {
            "ngram_tokenizer": {
              "token_chars": [
                "letter"
              ],
              "min_gram": "2",
              "type": "ngram",
              "max_gram": "4"
            },
            "whitespace_tokenizer": {
              "pattern": """\s+""",
              "type": "pattern"
            }
          }
        },
        "number_of_replicas": "0"
      }
    }
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

def check_and_create_index():
    # 检查索引是否存在
    response = requests.head(ES_INDEX_URL)
    if response.status_code == 404:
        print("Index not found, creating a new one...")
        # 如果索引不存在，则创建
        response = requests.put(ES_INDEX_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(INDEX_CONFIG))
        if response.status_code == 200:
            print("Index created successfully.")
        else:
            print(f"Failed to create index: {response.text}")
    elif response.status_code == 200:
        print("Index already exists.")
    else:
        print(f"Error checking index: {response.status_code} - {response.text}")

def generate_current_plate(last_state=None):
    letters = string.ascii_uppercase
    suffix_letters = list(itertools.product(letters, repeat=3))  # 生成所有可能的后缀（AAA到ZZZ）

    start_prefix = "AA"
    start_number_index = 0
    suffix_index = 0

    if last_state:
        start_prefix = last_state['prefix']
        prefix_number = last_state['prefix_number']
        suffix = last_state['suffix']
        
        # 查找从上次中断处开始的字母、数字和后缀索引
        start_number_index = CURRENT_NUMBERS.index(prefix_number)
        suffix_index = suffix_letters.index(tuple(suffix))
    else:
        prefix_number = CURRENT_NUMBERS[0]

    # 开始字母迭代
    for prefix in itertools.product(letters, repeat=2):
        prefix = ''.join(prefix)

        if prefix < start_prefix:
            continue  # 跳过直到达到缓存的前缀位置

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
                
                yield plate
            
            suffix_index = 0  # 当数字变化时，重置后缀为初始值
            
        start_number_index = 0  # 当字母变化时，重置数字为初始值
        suffix_index = 0  # 重置后缀为初始值

def bulk_write_to_es(data):
    headers = {'Content-Type': 'application/json'}
    bulk_data = ''
    for entry in data:
        bulk_data += json.dumps({"index": {"_id": entry["plateNumber"]}}) + "\n"
        bulk_data += json.dumps(entry) + "\n"

    response = requests.post(ES_URL, headers=headers, data=bulk_data)
    response.raise_for_status()

def main():
    check_and_create_index()  # 检查并创建索引
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
