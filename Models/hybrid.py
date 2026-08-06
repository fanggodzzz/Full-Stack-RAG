from . import bm25_model as bm
from . import vector_model as vec
import numpy as np


def _minmax_scale(scores):
	arr = np.array(scores, dtype=float)
	if arr.size == 0:
		return arr
	mn = arr.min()
	mx = arr.max()
	if mx - mn == 0:
		# all equal -> map to zeros
		return np.zeros_like(arr)
	return (arr - mn) / (mx - mn)

def combine_scores(bm25_scores, w2v_scores, bm25_weight=0.5, top_n=20):
	# Scale to [0, 1]
	bm25_scaled = _minmax_scale(bm25_scores)
	vec_scaled = _minmax_scale(w2v_scores)

	vec_weight = 1.0 - bm25_weight

	# Full score list
	hybrid_scores = []

	for b, v in zip(bm25_scaled, vec_scaled):
		score = bm25_weight * float(b) + vec_weight * float(v)
		hybrid_scores.append(score)

	top_indices = sorted(
		range(len(hybrid_scores)),
		key=lambda i: hybrid_scores[i],
		reverse=True
	)[:top_n]

	return hybrid_scores, top_indices

def query_hybrid(bm25, w2v_model, doc_vectors, query_tokens, bm25_weight=0.5, top_n=10):
    # Get scores from both models
    bm25_scores, _ = bm.query_bm25(bm25, query_tokens, top_n=top_n)
    vec_scores, _ = vec.query_vector(w2v_model, doc_vectors, query_tokens, top_n=top_n)

    return combine_scores(bm25_scores, vec_scores, bm25_weight=bm25_weight, top_n=top_n)

