import numpy as np

# 相似度矩阵
similarity_pairs = {
    ('A', '4'): 0.8,
    ('B', '8'): 0.9, ('B', '3'): 0.6,
    ('D', 'O'): 0.8, ('D', '0'): 0.8,
    ('E', '3'): 0.7,
    ('G', '6'): 0.8, ('C', 'G'): 0.5,
    ('I', '1'): 0.95, ('I', 'L'): 0.6,
    ('O', '0'): 0.9, ('O', 'Q'): 0.7,
    ('S', '5'): 0.9,
    ('Z', '2'): 0.85,
    ('T', '7'): 0.85,
    ('L', '1'): 0.85,
    ('P', 'R'): 0.6,
    ('U', 'V'): 0.75,
    ('V', 'Y'): 0.5,
    ('M', 'N'): 0.6,
    ('K', 'X'): 0.5,
}

def get_similarity(c1, c2):
    if c1 == c2:
        return 1.0
    if (c1, c2) in similarity_pairs:
        return similarity_pairs[(c1, c2)]
    if (c2, c1) in similarity_pairs:
        return similarity_pairs[(c2, c1)]
    return 0.0

def custom_levenshtein_automaton(str1, str2, max_dist=3):
    len1, len2 = len(str1), len(str2)
    dp = np.full((len1 + 1, len2 + 1), float('inf'))  # 用inf初始化矩阵
    dp[0][0] = 0  # 初始状态

    for i in range(len1 + 1):
        for j in range(len2 + 1):
            if i > 0:
                dp[i][j] = min(dp[i][j], dp[i - 1][j] + 1)  # 删除
            if j > 0:
                dp[i][j] = min(dp[i][j], dp[i][j - 1] + 1)  # 插入
            if i > 0 and j > 0:
                cost_substitution = 1 - get_similarity(str1[i - 1], str2[j - 1])
                dp[i][j] = min(dp[i][j], dp[i - 1][j - 1] + cost_substitution)  # 替换
            if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] and str1[i - 2] == str2[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)  # 交换

    final_distance = dp[len1][len2]
    
    if final_distance > max_dist:
        return float('inf')
    
    return final_distance

def adjusted_jaccard_similarity(str1, str2, similarity_threshold=0.5):
    set1 = set(str1)
    set2 = set(str2)
    intersection = 0
    union = len(set1) + len(set2)

    for char1 in set1:
        for char2 in set2:
            similarity = get_similarity(char1, char2)
            if similarity > similarity_threshold:
                intersection += similarity
                union -= 1  # 因为它们被算作相似，所以从并集中减去一项

    return intersection / union if union != 0 else 0

def mixed_similarity(input_str, record_str, alpha=0.5, beta=0.5, similarity_threshold=0.5, max_dist=3):
    # 使用莱文斯坦自动机计算自定义的 Levenshtein 距离
    dl_distance = custom_levenshtein_automaton(input_str, record_str, max_dist)
    
    # 如果距离超过了最大允许距离，则直接返回最小相似度，跳过 Jaccard 计算
    if dl_distance == float('inf'):
        return 0.0  # 直接返回 0.0
    
    # 将距离转化为相似度
    max_len = max(len(input_str), len(record_str))
    dl_similarity = 1 / (1 + dl_distance)  # 距离越大，相似度越小

    # 计算调整后的 Jaccard 相似度
    jaccard_sim = adjusted_jaccard_similarity(input_str, record_str, similarity_threshold)
    
    # 混合得分，alpha 和 beta 用于调整两个指标的权重
    mixed_score = alpha * dl_similarity + beta * jaccard_sim
    
    return mixed_score

def calculate_mixed_distances(input_str, database, alpha=0.5, beta=0.5, similarity_threshold=0.5, max_dist=3):
    distances = {}
    
    for key, record in database.items():
        similarity = mixed_similarity(input_str, record, alpha, beta, similarity_threshold, max_dist)
        distances[key] = similarity

    return distances

def sort_distances(distances, reverse=True):
    sorted_distances = sorted(distances.items(), key=lambda item: item[1], reverse=reverse)
    return sorted_distances

# 示例用法
input_str = "MARK"
database = {
    "record1": "M4 ARK",
    "record2": "M2 ARK",
    "record3": "4B12 CDE",
    "record4": "4B1C PPP",
    "record44": "4B1 GPP",
    "record445": "M4 CRK",
    "record5": "M4 KRK",
    "record6": "M4 BRK",
}

# 控制 Levenshtein 和 Jaccard 的相对重要性
alpha = 0.7  # Levenshtein 的权重
beta = 0.3   # Jaccard 的权重

distances = calculate_mixed_distances(input_str, database, alpha, beta)
sorted_distances = sort_distances(distances)

# 输出排序后的结果
for key, similarity in sorted_distances:
    print(f"Similarity between '{input_str}' and '{database[key]}' (record '{key}'): {similarity}")
