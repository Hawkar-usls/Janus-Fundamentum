from __future__ import annotations

import janus_trump_r50g25ap_interleaved_r33_rup_combined_potential as ap

# Technical compatibility repair only: the frozen AP implementation contains one
# accidental call to r33.simpl in the AN replay path. Bind that name to the
# already-imported r33.simplify implementation without changing any scientific
# formula, threshold, transition rule, audit domain, or falsifier class.
ap.r33.simpl = ap.r33.simplify

if __name__ == "__main__":
    ap.main()
