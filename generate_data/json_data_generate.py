# 文件路径: generate_ecommerce_sample_data.py

import json
import random
from faker import Faker

# 创建一个Faker实例
fake = Faker()

# 产品类别样本
categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Health & Beauty", "Toys", "Automotive"]

# 生成单个产品的样本数据
def generate_product_data(product_id):
    return {
        "product_id": product_id,
        "name": fake.catch_phrase(),
        "description": fake.text(max_nb_chars=200),
        "price": round(random.uniform(5.0, 500.0), 2),
        "category": random.choice(categories),
        "stock_quantity": random.randint(0, 1000),
        "rating": round(random.uniform(1.0, 5.0), 1),
        "date_added": fake.date_this_decade().isoformat()
    }

# 生成指定数量的样本数据并保存为JSON
def generate_sample_data(num_products, output_file):
    products = []
    for i in range(1, num_products + 1):
        product = generate_product_data(i)
        products.append(product)
    
    # 将数据写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(products, file, ensure_ascii=False, indent=4)
    
    print(f"Successfully generated {num_products} sample products into {output_file}")

# 主函数
if __name__ == "__main__":
    num_products = 200000  # 生成20万个样本数据
    output_file = "ecommerce_sample_data.json"  # 输出JSON文件名
    generate_sample_data(num_products, output_file)
