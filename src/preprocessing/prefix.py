def generate_prefixes(seq, prefix_lengths, max_len):
    out = []
    for k in prefix_lengths:
        if len(seq) >= k:
            p = seq[:k] + [0] * (max_len - k)
            out.append(p)
    return out
