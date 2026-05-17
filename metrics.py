def precision_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    hits = sum(1 for book_id in recommended_at_k if book_id in relevant)
    return hits / k if k > 0 else 0

def recall_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    hits = sum(1 for book_id in recommended_at_k if book_id in relevant)
    return hits / len(relevant) if relevant else 0

def ctr(clicks, impressions):
    return clicks / impressions if impressions > 0 else 0
