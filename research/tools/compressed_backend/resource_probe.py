import argparse, json, psutil, subprocess, time

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("cmd",nargs=argparse.REMAINDER)
    a=ap.parse_args()
    if not a.cmd: raise SystemExit("missing command")
    t0=time.perf_counter()
    p=subprocess.Popen(a.cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    proc=psutil.Process(p.pid); peak=0
    while p.poll() is None:
        try:
            rss=proc.memory_info().rss
            for c in proc.children(recursive=True):
                try: rss+=c.memory_info().rss
                except psutil.Error: pass
            peak=max(peak,rss)
        except psutil.Error: pass
        time.sleep(0.01)
    out,err=p.communicate()
    dt=time.perf_counter()-t0
    print(json.dumps({"returncode":p.returncode,"elapsed_seconds":dt,"peak_rss_bytes":peak,"peak_rss_MiB":peak/1048576,"stdout":out.strip(),"stderr_tail":err.strip()[-500:]},sort_keys=True))
    return p.returncode
if __name__=="__main__": raise SystemExit(main())
