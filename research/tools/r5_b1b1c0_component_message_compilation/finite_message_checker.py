#!/usr/bin/env python3
"""Finite checker for B1B1C0 monotone 4-color component-message language.

Enumerates all Boolean functions on 2^[4], keeps exactly downward-closed
good-mask families, counts them, and computes the maximum number of
inclusion-minimal bad masks.
"""
MASKS=range(16)

def subset(a,b):
    return (a & ~b)==0

count=0
max_min_bad=0
for goodbits in range(1<<16):
    down=True
    for F in MASKS:
        if (goodbits>>F)&1:
            for G in MASKS:
                if subset(G,F) and not ((goodbits>>G)&1):
                    down=False
                    break
            if not down:
                break
    if not down:
        continue
    count+=1
    bad=[F for F in MASKS if not ((goodbits>>F)&1)]
    min_bad=[
        F for F in bad
        if not any(G!=F and subset(G,F) for G in bad)
    ]
    max_min_bad=max(max_min_bad,len(min_bad))

assert count==168, count
assert max_min_bad==6, max_min_bad
print({"status":"PASS","monotone_message_count":count,"max_MIN_BAD_size":max_min_bad})
