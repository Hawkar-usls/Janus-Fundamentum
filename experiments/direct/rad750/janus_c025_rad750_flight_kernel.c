/*
 * JANUS C025 — RAD750-class deterministic flight kernel (reference C11)
 *
 * Target philosophy:
 *   - 32-bit PowerPC 750 / RAD750-friendly data model
 *   - integer-only semantic verification
 *   - no heap allocation
 *   - no recursion
 *   - no floating point
 *   - explicit bounds and fail-closed status codes
 *   - identical semantics on x86/ARM/PowerPC when fed canonical bytes
 *
 * This file is NOT a SAT solver and is NOT evidence for P=NP.  It is the
 * smallest hardware-facing verification substrate on which future C025 proof
 * certificates can be replayed.  P_VS_NP remains OPEN.
 */

#include <stddef.h>
#include <stdint.h>
#include <limits.h>

#if defined(__STDC_IEC_559__)
/* IEC-559 availability is irrelevant: this kernel deliberately uses no FP. */
#endif

typedef enum janus_c025_status {
    JANUS_C025_OK = 0,
    JANUS_C025_REJECT = 1,
    JANUS_C025_OPEN_BUDGET = 2,
    JANUS_C025_SAFE_ERROR = 3
} janus_c025_status;

typedef struct janus_c025_budget {
    uint64_t work_limit;
    uint64_t work_used;
} janus_c025_budget;

typedef struct janus_c025_cnf_view {
    const int32_t *literals;
    const uint32_t *clause_offsets; /* length = clause_count + 1 */
    uint32_t clause_count;
    uint32_t literal_count;
    uint32_t variable_count;
} janus_c025_cnf_view;

static janus_c025_status janus_charge(janus_c025_budget *budget, uint64_t amount)
{
    if (budget == NULL) {
        return JANUS_C025_SAFE_ERROR;
    }
    if (UINT64_MAX - budget->work_used < amount) {
        return JANUS_C025_SAFE_ERROR;
    }
    if (budget->work_used + amount > budget->work_limit) {
        return JANUS_C025_OPEN_BUDGET;
    }
    budget->work_used += amount;
    return JANUS_C025_OK;
}

static janus_c025_status janus_validate_cnf_view(const janus_c025_cnf_view *cnf)
{
    uint32_t i;

    if (cnf == NULL || cnf->clause_offsets == NULL) {
        return JANUS_C025_SAFE_ERROR;
    }
    if (cnf->literal_count != 0U && cnf->literals == NULL) {
        return JANUS_C025_SAFE_ERROR;
    }
    if (cnf->clause_offsets[0] != 0U) {
        return JANUS_C025_SAFE_ERROR;
    }
    if (cnf->clause_offsets[cnf->clause_count] != cnf->literal_count) {
        return JANUS_C025_SAFE_ERROR;
    }
    for (i = 0U; i < cnf->clause_count; ++i) {
        if (cnf->clause_offsets[i] > cnf->clause_offsets[i + 1U]) {
            return JANUS_C025_SAFE_ERROR;
        }
    }
    return JANUS_C025_OK;
}

/*
 * Verify one complete Boolean assignment against a CNF.
 * assignment[var-1] must be exactly 0 or 1.  Literal 0 is invalid.
 * Empty clause => verified REJECT (formula false under every assignment).
 * Any malformed input => SAFE_ERROR, never a guessed truth value.
 */
janus_c025_status janus_c025_verify_sat_witness(
    const janus_c025_cnf_view *cnf,
    const uint8_t *assignment,
    uint32_t assignment_count,
    janus_c025_budget *budget)
{
    uint32_t c;
    janus_c025_status status;

    status = janus_validate_cnf_view(cnf);
    if (status != JANUS_C025_OK) {
        return status;
    }
    if (assignment == NULL || assignment_count < cnf->variable_count) {
        return JANUS_C025_SAFE_ERROR;
    }

    for (c = 0U; c < cnf->variable_count; ++c) {
        status = janus_charge(budget, 1U);
        if (status != JANUS_C025_OK) {
            return status;
        }
        if (assignment[c] > 1U) {
            return JANUS_C025_SAFE_ERROR;
        }
    }

    for (c = 0U; c < cnf->clause_count; ++c) {
        uint32_t j;
        uint8_t clause_true = 0U;
        const uint32_t begin = cnf->clause_offsets[c];
        const uint32_t end = cnf->clause_offsets[c + 1U];

        status = janus_charge(budget, 1U);
        if (status != JANUS_C025_OK) {
            return status;
        }

        if (begin == end) {
            return JANUS_C025_REJECT;
        }

        for (j = begin; j < end; ++j) {
            const int32_t lit = cnf->literals[j];
            uint32_t var;
            uint8_t value;

            status = janus_charge(budget, 1U);
            if (status != JANUS_C025_OK) {
                return status;
            }
            if (lit == 0 || lit == INT32_MIN) {
                return JANUS_C025_SAFE_ERROR;
            }
            var = (uint32_t)(lit < 0 ? -lit : lit);
            if (var == 0U || var > cnf->variable_count) {
                return JANUS_C025_SAFE_ERROR;
            }
            value = assignment[var - 1U];
            if ((lit > 0 && value == 1U) || (lit < 0 && value == 0U)) {
                clause_true = 1U;
                break;
            }
        }
        if (clause_true == 0U) {
            return JANUS_C025_REJECT;
        }
    }
    return JANUS_C025_OK;
}

/* Exact resource accounting used by the Python C025 engine:
 * state_units = 1 + clause_count + literal_count.
 */
janus_c025_status janus_c025_state_units(
    const janus_c025_cnf_view *cnf,
    uint64_t *out_units)
{
    janus_c025_status status = janus_validate_cnf_view(cnf);
    if (status != JANUS_C025_OK || out_units == NULL) {
        return JANUS_C025_SAFE_ERROR;
    }
    *out_units = 1ULL + (uint64_t)cnf->clause_count + (uint64_t)cnf->literal_count;
    return JANUS_C025_OK;
}

#ifdef JANUS_C025_SELFTEST
#include <stdio.h>

static int expect_status(const char *name, janus_c025_status got, janus_c025_status expected)
{
    if (got != expected) {
        fprintf(stderr, "%s: got=%d expected=%d\n", name, (int)got, (int)expected);
        return 1;
    }
    return 0;
}

int main(void)
{
    /* (x1 OR x2) AND (!x1 OR x3) */
    static const int32_t lits[] = { 1, 2, -1, 3 };
    static const uint32_t offsets[] = { 0, 2, 4 };
    static const uint8_t sat_assignment[] = { 1, 0, 1 };
    static const uint8_t bad_assignment[] = { 0, 0, 1 };
    static const uint8_t malformed_assignment[] = { 2, 0, 1 };
    const janus_c025_cnf_view cnf = { lits, offsets, 2U, 4U, 3U };
    janus_c025_budget budget;
    uint64_t units = 0ULL;
    int failed = 0;

    budget.work_limit = 64ULL;
    budget.work_used = 0ULL;
    failed |= expect_status("sat", janus_c025_verify_sat_witness(&cnf, sat_assignment, 3U, &budget), JANUS_C025_OK);

    budget.work_limit = 64ULL;
    budget.work_used = 0ULL;
    failed |= expect_status("reject", janus_c025_verify_sat_witness(&cnf, bad_assignment, 3U, &budget), JANUS_C025_REJECT);

    budget.work_limit = 64ULL;
    budget.work_used = 0ULL;
    failed |= expect_status("malformed", janus_c025_verify_sat_witness(&cnf, malformed_assignment, 3U, &budget), JANUS_C025_SAFE_ERROR);

    budget.work_limit = 1ULL;
    budget.work_used = 0ULL;
    failed |= expect_status("budget", janus_c025_verify_sat_witness(&cnf, sat_assignment, 3U, &budget), JANUS_C025_OPEN_BUDGET);

    failed |= expect_status("units", janus_c025_state_units(&cnf, &units), JANUS_C025_OK);
    if (units != 7ULL) {
        fprintf(stderr, "units: got=%llu expected=7\n", (unsigned long long)units);
        failed = 1;
    }

    if (failed != 0) {
        return 1;
    }
    puts("JANUS_C025_RAD750_FLIGHT_KERNEL_SELFTEST=PASS");
    puts("P_VS_NP=OPEN");
    return 0;
}
#endif
