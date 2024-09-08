import numpy as np
from sklearn.neighbors import NearestNeighbors

# 字符集：26个字母 + 10个数字
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# 相似度字典，使用提供的相似度矩阵
char_similarity = {
    ('A', '4'): 0.8, ('B', '8'): 0.9, ('B', '3'): 0.6,
    ('D', 'O'): 0.8, ('D', '0'): 0.8, ('E', '3'): 0.7,
    ('G', '6'): 0.8, ('C', 'G'): 0.5, ('I', '1'): 0.95,
    ('I', 'L'): 0.6, ('O', '0'): 0.9, ('O', 'Q'): 0.7,
    ('S', '5'): 0.9, ('Z', '2'): 0.85, ('T', '7'): 0.85,
    ('L', '1'): 0.85, ('P', 'R'): 0.6, ('U', 'V'): 0.75,
    ('V', 'Y'): 0.5, ('M', 'N'): 0.6, ('K', 'X'): 0.5
}

# 构建字符的相似度向量，未知字符相似度设为0
def build_char_vector(char):
    vector = np.zeros(len(chars))
    for i, c in enumerate(chars):
        if char == c:
            vector[i] = 1.0  # 自己和自己相似度为1
        else:
            vector[i] = char_similarity.get((char, c), char_similarity.get((c, char), 0))
    return vector

# 将车牌转换为特征向量
def plate_to_vector(plate):
    vectors = [build_char_vector(c) for c in plate]
    return np.concatenate(vectors)

# 计算两个车牌的相似度，使用余弦相似度
def plate_similarity(plate1, plate2):
    vec1 = plate_to_vector(plate1)
    vec2 = plate_to_vector(plate2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 计算所有样本之间的相似度距离矩阵
def compute_similarity_matrix(plates):
    n = len(plates)
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            similarity_matrix[i][j] = plate_similarity(plates[i], plates[j])
    
    return similarity_matrix

# 车牌数据
plates = ['AB1234', 'AB123A', 'A8123A', 'EF1236']

# 计算样本车牌之间的相似度矩阵
similarity_matrix = compute_similarity_matrix(plates)

# 打印相似度矩阵
print("车牌相似度矩阵：")
for i, plate1 in enumerate(plates):
    for j, plate2 in enumerate(plates):
        print(f"{plate1} 和 {plate2} 的相似度: {similarity_matrix[i][j]:.2f}")
