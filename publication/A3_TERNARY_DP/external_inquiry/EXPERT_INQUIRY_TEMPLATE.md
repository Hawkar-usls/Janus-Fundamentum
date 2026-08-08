# External Expert Inquiry Template

Subject: Prior-art / technical review request: endpoint-compressed path-width DP for repeated subspace classes

Dear Professor [Name],

I am preparing a proof-carrying manuscript on a restricted finite-field subspace-arrangement path-width problem and would be grateful for a quick prior-art or technical sanity check.

The result concerns arrangements with `k` distinct geometric subspace classes and arbitrary positive multiplicities. After first/last endpoint compression, the ordering problem is represented by an exact state graph with `2^s*3^r` states (`s` singleton classes, `r` repeated classes) and

`s*2^(s-1)*3^r + 2r*2^s*3^(r-1)`

transitions. This gives `O(k*3^k)` combinatorial bottleneck-DP work after `2^k` subset-rank preprocessing.

Frozen technical package:
- publication head: `811d954e52296893898062d9abea7aaf572629be`
- deterministic PDF SHA-256: `a3a6e87376d38e9336d9e101640ebfaf5f41499a885f0477e2f46b88cf3cd5e4`
- publication artifact ID: `9025859191`

I am not claiming historical priority or universal absence from the literature. The current novelty status is only `N3_EXHAUSTIVELY_SEARCHED_WITHIN_DECLARED_PROTOCOL`, with N4 explicitly `NOT_ESTABLISHED`.

If you have seen an equivalent theorem, a result that directly subsumes it, or terminology under which this construction is already standard, I would especially appreciate the citation. I would also welcome any counterexample, hidden assumption, or reference that should be added before public submission.

Thank you for your time.

Best regards,
Oleksandr / Hawkar
