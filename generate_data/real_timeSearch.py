# 文件路径: index_and_search_ecommerce_data.py

import json
from datetime import datetime
import requests

# Elasticsearch的URL
ES_URL = "http://localhost:9200"

# 使用requests提交数据到Elasticsearch
def bulk_upload_to_es(data, index_name, batch_size):
    bulk_data = ""
    count = 0
    for item in data:
        action = {"index": {"_index": index_name}}
        bulk_data += json.dumps(action) + "\n" + json.dumps(item) + "\n"
        count += 1
        
        # 只进行一次写入操作，达到批量大小后退出
        if count == batch_size:
            headers = {"Content-Type": "application/x-ndjson"}
            response = requests.post(f"{ES_URL}/_bulk", headers=headers, data=bulk_data)
            
            if response.status_code == 200:
                print(f"Successfully indexed {batch_size} documents to {index_name}")
            else:
                print(f"Error indexing data: {response.text}")
            
            return  # 只进行一次写入，完成后退出

# 搜索操作
def search_in_es(index_name, query):
    response = requests.get(f"{ES_URL}/{index_name}/_search", json=query)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error searching data: {response.text}")
        return None

# 主函数
def main():
    # 第一步: 读取JSON文件数据
    input_file = "ecommerce_sample_data.json"  # 输入JSON文件名
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 第二步: 配置Elasticsearch索引
    query = {"query": {"match_all": {}}}
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    index_name = f"my_index_{timestamp}"  # 使用时间戳生成唯一索引名
    batch_size = 10000  # 设定批量大小（可以根据需要调整）

    # 第三步: 提交数据到Elasticsearch并立即开始计时
    start_time = datetime.utcnow()
    
    bulk_upload_to_es(data, index_name, batch_size)  # 只进行一次写入
    response = search_in_es(index_name, query)
    
    end_time = datetime.utcnow()  # 结束时间

    # 计算时间差并转换为毫秒
    total_time_ms = (end_time - start_time).total_seconds() * 1000
    
    # 打印搜索结果和时间信息
    if response:
        print(f"Data submission and search completed at: {end_time}")
        print(f"Total time from data submission to search completion: {total_time_ms:.2f} ms")
        print(f"Total documents found: {response['hits']['total']['value']}")

if __name__ == "__main__":
    main()
