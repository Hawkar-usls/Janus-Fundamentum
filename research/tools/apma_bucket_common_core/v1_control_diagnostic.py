from __future__ import annotations
import json
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as v1
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded

def slim(x):
    return {
      'status':x.get('status'),
      'global_basis_status':x.get('global_basis_status'),
      'parent_status':x.get('parent_status'),
      'components':x.get('components'),
      'failed_variable':x.get('carrier',{}).get('failed_bucket',{}).get('variable'),
      'failed_zero':x.get('carrier',{}).get('resource_receipt',{}).get('failed_bucket_combinations_enumerated'),
      'total_before_open':x.get('carrier',{}).get('resource_receipt',{}).get('total_combinations_enumerated_before_open')
    }

def main():
    positive=v1.positive_aligned_overbudget_control(); sticky=v1.filtered_still_overbudget_control(); hostile=guarded.overbudget_control()
    out={
      'artifact_id':'JANUS-TRUMP-BUCKET-COMMON-CORE-SEMIJOIN-V1-CONTROL-DIAGNOSTIC-2026-09-15',
      'authority':'DIAGNOSTIC_ONLY__V1_UNCHANGED',
      'positive_guarded':slim(guarded.explain(positive)),
      'positive_first_failed':{k:v for k,v in v1.first_failed_original_bucket(positive).items() if k in {'status','failed_variable','common_core','component'}},
      'sticky_guarded':slim(guarded.explain(sticky)),
      'sticky_first_failed':{k:v for k,v in v1.first_failed_original_bucket(sticky).items() if k in {'status','failed_variable','common_core','component'}},
      'hostile_guarded':slim(guarded.explain(hostile)),
      'hostile_first_failed':{k:v for k,v in v1.first_failed_original_bucket(hostile).items() if k in {'status','failed_variable','common_core','component'}},
      'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_EFFECTIVE_BUCKET_COMPRESSION':'NOT_PROVED'}
    }
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()
