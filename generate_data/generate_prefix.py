import string
import itertools
import json
import requests
import random
import os

ES_URL = "http://127.0.0.1:9200/prefix/_bulk"
ES_INDEX_URL = "http://127.0.0.1:9200/prefix"
CACHE_FILE = "./prefix_cache.json"
BULK_SIZE = 1000

# 自定义的数字迭代区间
PREFIX_NUMBERS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 40, 44, 50, 55, 60, 66,
    70, 77, 80, 88, 90, 99, 100, 111, 123, 155, 200, 222, 300, 321, 333,
    400, 444, 500, 555, 600, 666, 700, 777, 800, 888, 900, 999
]

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
    check_and_create_index()  # 检查并创建索引
    
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
