#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

LEFT='LEFT_HRAIN'
RIGHT='RIGHT_INAIHR'
ROLES={LEFT:'STRUCTURAL_CONTEXT', RIGHT:'ASSOCIATIVE_CONTEXT'}
REPOS={LEFT:'Hawkar-usls/Hrain', RIGHT:'Hawkar-usls/iNaiHR'}
PACKET_SCHEMAS={'janus.demihead.hemisphere_packet.v1','janus.demihead.hemisphere_packet.v3'}
MESSAGE_CLASSES={
 'ATTENTION_POINTER','CONTEXT_REQUEST','CONTEXT_RETURN','HYPOTHESIS_CANDIDATE',
 'CONTRADICTION_OR_DISAGREEMENT','AMBIGUITY_SET','PROVENANCE_POINTER','DEBT_POINTER'
}

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')

def sha256_obj(x): return hashlib.sha256(canon(x)).hexdigest()

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def validate_packet(p, expected):
    if p.get('schema') not in PACKET_SCHEMAS: raise ValueError('unsupported hemisphere packet schema')
    if p.get('hemisphere') != expected: raise ValueError('hemisphere mismatch')
    if p.get('role') != ROLES[expected]: raise ValueError('role mismatch')
    source=p.get('source') or {}
    if source.get('repository') != REPOS[expected]: raise ValueError('repository mismatch')
    ctl=p.get('control') or {}
    if ctl.get('read_only_transfer') is not True: raise ValueError('read_only_transfer required')
    if ctl.get('direct_cross_hemisphere_mutation') is not False: raise ValueError('direct mutation forbidden')
    if ctl.get('authority_delta') != 0 or ctl.get('mass_effect_budget_delta') != 0: raise ValueError('authority delta forbidden')
    return p

def exchange(source_packet,target,message_class,payload,previous=None,ordinal=1):
    source=source_packet['hemisphere']
    if target not in ROLES or target==source: raise ValueError('invalid target')
    if message_class not in MESSAGE_CLASSES: raise ValueError('invalid message class')
    base={
      'schema':'janus.physarius.hemispheric_exchange.v1',
      'exchange_id':f'{source.lower()}-to-{target.lower()}-{ordinal:04d}',
      'source_hemisphere':source,
      'target_hemisphere':target,
      'source_packet_sha256':sha256_obj(source_packet),
      'message_class':message_class,
      'payload':payload,
      'previous_exchange_sha256':previous,
      'control':{
        'read_only_transfer':True,
        'direct_cross_hemisphere_mutation':False,
        'authority_delta':0,
        'mass_effect_budget_delta':0,
        'scientific_claim_promotion':False,
        'proof_authority':False
      }
    }
    base['exchange_sha256']=sha256_obj(base)
    return base

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--left',required=True); ap.add_argument('--right',required=True); ap.add_argument('--out',required=True)
    args=ap.parse_args()
    left=validate_packet(load(args.left),LEFT); right=validate_packet(load(args.right),RIGHT)
    l2r=exchange(left,RIGHT,'ATTENTION_POINTER',{
      'kind':'STRUCTURAL_TO_ASSOCIATIVE_QUERY',
      'source_graph_nodes':len((left.get('graph') or {}).get('nodes') or []),
      'request':'Generate associative alternatives without mutating or overwriting LEFT_HRAIN structural state.'
    },None,1)
    r2l=exchange(right,LEFT,'HYPOTHESIS_CANDIDATE',{
      'kind':'ASSOCIATIVE_TO_STRUCTURAL_CANDIDATE',
      'source_graph_nodes':len((right.get('graph') or {}).get('nodes') or []),
      'request':'Return candidate associations for structural verification; preserve ambiguity and disagreement.'
    },l2r['exchange_sha256'],2)
    receipt={
      'schema':'janus.physarius.hemispheric_commissure_receipt.v1',
      'status':'COMMISSURE_DUPLEX_PASS',
      'contract':'PHYSARIUS_HEMISPHERIC_COMMISSURE_V1',
      'left_packet_sha256':sha256_obj(left),
      'right_packet_sha256':sha256_obj(right),
      'lanes':{'LEFT_TO_RIGHT':l2r,'RIGHT_TO_LEFT':r2l},
      'disagreement_policy':'PRESERVE_UNTIL_SEPARATE_RECEIPT_RESOLVES',
      'authority':'READ_ONLY_CONTEXT_TRANSFER',
      'scientific_claim_promoted':False,
      'proof_promoted':False,
      'independent_replication_claimed':False
    }
    receipt['receipt_sha256']=sha256_obj(receipt)
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['status','receipt_sha256','left_packet_sha256','right_packet_sha256']},indent=2))

if __name__=='__main__': main()
