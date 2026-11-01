# TIME-SAT-004B · original evidence preserved; fix future SIGXCPU receipt

Research child branch of draft PR #578, base af21a4c2c8b522e41810c117dea2ec6b9d2e39da. No original `screen.original.json`, Actions ZIP, scientific interpretation, CNF or P-center proof was changed.

The previous baseline executor grouped all nonzero child return codes as `ENGINE_ERROR_OR_RESOURCE_LIMIT`. On Ubuntu/Linux a return code of -24 is `SIGXCPU`, consistent with the 16-second soft CPU resource limit. The immutable scientific interpretation had already identified all 16 such terminations in eight benchmark cases.

Future runs distinguish `UNKNOWN_CPU_LIMIT_SIGXCPU`, `UNKNOWN_PROCESS_SIGNAL`, `ENGINE_NONZERO_EXIT`, and `UNKNOWN_WALL_TIMEOUT`. Other signals (particularly SIGKILL) are not falsely attributed to a particular resource limit. Neither process failure nor timeout ever implies SAT or UNSAT.

Added offline unit tests and lightweight 3-minute CI requiring no paid services, no competition-CNF download and no solver execution. This is an engineering receipt change only. C023/main is unchanged, PRs remain draft; no net-speedup is claimed.
