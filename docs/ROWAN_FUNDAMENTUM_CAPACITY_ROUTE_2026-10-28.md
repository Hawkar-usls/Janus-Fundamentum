# Rowan capacity for JANUS Fundamentum: feasibility and typed routing (2026-10-28)

## Decision

**Do not repurpose Rowan as an arbitrary CPU/GPU worker.** The public Rowan API exposes specialized computational chemistry, molecular-physics, materials and protein-ligand workflows, not an advertised user-supplied Python/container/SAT job execution endpoint. Enterprise pricing mentions **custom workflow development**, which is not an already granted general-purpose execution capability.

Sources:
- [Rowan agentic scientific execution](https://www.rowansci.com/solutions/agentic-science)
- [Rowan official workflows](https://docs.rowansci.com/workflows)
- [Rowan Python v3 API](https://docs.rowansci.com/api/python/v3/)
- [Rowan plans and custom workflow development](https://rowansci.com/pricing)

The source of truth for Rowan task submission lives in [\`Hawkar-usls/Janus/integrations/rowan/\`](https://github.com/Hawkar-usls/Janus/tree/main/integrations/rowan). That bridge currently implements **SMILES-only microscopic pKa**; no Fundamentum provider calls are implemented here. Tranception/BBC1 history remains a separate, not-to-be-repurposed source-of-truth. No Rowan secrets or budgets are copied into Fundamentum.

## Two distinct JANUS pathways

1. **Formal/Exact-One search:** Fundamentum + GitHub Actions/authorized general-purpose runner. A \`SolveLinearCubicXSAT\` query cannot be submitted through the public Rowan scientific workflow API. Maintain exact SAT/UNSAT, unknown resource limit, provenance and independent proof checking.
2. **Genuine physical and chemical experiments:** Fundamentum proposes a chemically meaningful, falsifiable scientific hypothesis; a typed Rowan adapter in the gateway plans one authorized molecular job, TOPA reviews assumptions and external controls, and Meta Registry archives scoped observations. No claim that chemical simulation proves a theorem or validates a mathematical solution.

An exploratory **physical constraint-satisfaction analogue** is research-only. Before a single Rowan job intended as evidence for combinatorial search, explicitly provide (i) a uniform size-bounded reduction from arbitrary Exact-One instances to physically realizable supported molecular structures, (ii) faithful energy ordering and an independently checkable readout, (iii) a robust error/temperature/precision margin and its scaling, (iv) actual all-input polynomial resource bounds, and (v) independently preregistered adversarial SAT and UNSAT tests. None of these preconditions is established by this PR.

## Offline routing command

\`\`\`bash
python tools/rowan_fundamentum_router.py --self-test
python tools/rowan_fundamentum_router.py --request /path/to/request.json
\`\`\`

A request is only a pinned metadata proposal, never a provider job. Its schema is \`janus.fundamentum.rowan_request.v1\`, with \`task_id\`, \`task_class\`, \`execute=false\`, \`max_credits=0\`, \`source_repo\`, exact \`source_commit\`, \`input_sha256\`, \`scientific_goal\`. Any unexpected fields (including code payloads), unpinned source, or nonzero budget fail closed.

Decision types:
- \`GENERAL_COMPUTE\`, \`EXACT_ONE_SAT\`, \`PROOF_VERIFICATION\`: \`NOT_ROUTABLE_TO_ROWAN\`.
- \`PHYSICAL_CSP_ANALOG\`: \`RESEARCH_HOLD_NO_PHYSICAL_OR_FORMAL_EQUIVALENCE\`.
- \`MOLECULAR_OTHER\`: documented Rowan workflows exist, but a dedicated local adapter is still missing.
- \`MOLECULAR_PKA\`: \`PLAN_ONLY_EXISTING_ADAPTER_NO_REMOTE_CALL\`, which authorizes **nothing** in Rowan.

## Next implementation gate

For scientific chemistry work, build an explicit gateway-side read-only protocol to map a Fundamentum research case to the existing typed adapter, then verify a real independently sourced target, API availability and free/purchased credit separation before **any** user-authorized execution. Do not perform this through a Draft PR or untrusted code.

For general algorithmic work, use a true general-purpose compute runner rather than trying to disguise mathematical tasks as molecular simulations. Current scientific claim: \`P_VS_NP=OPEN\`; no new polynomial solver demonstrated.
