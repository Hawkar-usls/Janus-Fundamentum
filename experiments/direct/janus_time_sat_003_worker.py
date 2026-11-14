#!/usr/bin/env python3
"""Process isolated cold 003 A/B single-arm measurement for peak RSS."""
import json
import resource
import sys
from janus_time_sat_003 import run_arm

if __name__=="__main__":
    data=json.load(sys.stdin)
    result=run_arm(data["rows"],data["n"],data["kind"],
                   solver_name=data["solver"],arm=data["arm"])
    result["process_isolated_peak_rss_kib"]=resource.getrusage(
        resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(result,sort_keys=True))
