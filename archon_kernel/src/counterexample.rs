//! Bounded model search producing transparent counterexample certificates.
//!
//! Faithful port of `4leibniz/counterexample.py` (with `Claim`/`Premise`
//! from `4leibniz/ucalculus.py` and the relation parser from
//! `4leibniz/proof_engine.py::_relation`).
//!
//! Fidelity notes, mirroring the Python module docstring: this is a
//! *falsifier* for the relational fragment, not a complete theorem
//! prover. A witness is decisive for the searched integer model; no
//! witness is inconclusive (the Python "no-witness" outcome states this
//! explicitly: "the claim is not proved").
//!
//! In SAMO terms (spec §6.4) a `refuted` result is an `[X]`
//! counterexample certificate: `fingerprint` is the witness hash,
//! `assignment` is the minimal failing input, and `violated_conclusion`
//! names the falsified claim — with zero private operator data.

use std::collections::BTreeMap;

use crate::jsoncanon::{dumps_default, sha256_hex, JVal};

/// A single premise of a claim. Mirrors `ucalculus.Premise`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Premise {
    pub text: String,
    /// Display-normalized form (the Python parser replaces `>=` with
    /// ` ≥ ` and `->` with ` → `). Carried for structural parity with
    /// `ucalculus.Premise`; the search itself uses `text`, exactly as
    /// `counterexample.py` does (`p.text`).
    pub normalized: String,
}

impl Premise {
    pub fn new(text: impl Into<String>) -> Self {
        let text = text.into();
        let normalized = text.replace(">=", " \u{2265} ").replace("->", " \u{2192} ");
        Premise { text, normalized }
    }
}

/// A universal-calculus claim. Mirrors `ucalculus.Claim`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Claim {
    pub name: String,
    pub premises: Vec<Premise>,
    pub conclusion: String,
    pub source: Option<String>,
    /// One of the five epistemic status names (see
    /// [`crate::epistemic::Status`]).
    pub status: String,
    pub tags: Vec<String>,
}

impl Claim {
    pub fn new(
        name: impl Into<String>,
        premises: Vec<Premise>,
        conclusion: impl Into<String>,
    ) -> Self {
        Claim {
            name: name.into(),
            premises,
            conclusion: conclusion.into(),
            source: None,
            status: "open".into(),
            tags: Vec::new(),
        }
    }
}

/// The counterexample certificate. Mirrors `counterexample.Counterexample`
/// field-for-field.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Counterexample {
    /// `"refuted"` or `"no-witness"`.
    pub outcome: String,
    /// Always `"integers"` in the Python implementation.
    pub model: String,
    pub bound: i64,
    pub assignment: BTreeMap<String, i64>,
    pub satisfied_premises: Vec<String>,
    pub violated_conclusion: String,
    /// SHA-256 witness hash of the certificate payload; empty for
    /// `"no-witness"`, exactly as in Python.
    pub fingerprint: String,
    pub explanation: String,
}

/// Port of `proof_engine._relation`:
/// `re.fullmatch(r"(.+?)\s*(>=|<=|=|>|<)\s*(.+)", text)` with each group
/// stripped. Returns `(left, op, right)`.
fn relation(text: &str) -> Option<(String, String, String)> {
    const OPS: [&str; 5] = [">=", "<=", "=", ">", "<"];
    let chars: Vec<(usize, char)> = text.char_indices().collect();
    // The lazy left group tries the shortest left-hand side first.
    for start in 1..=chars.len() {
        let byte_idx = if start == chars.len() {
            text.len()
        } else {
            chars[start].0
        };
        let left = &text[..byte_idx];
        let rest = text[byte_idx..].trim_start();
        for op in OPS {
            if let Some(tail) = rest.strip_prefix(op) {
                let right = tail.trim_start();
                if !right.is_empty() {
                    return Some((
                        left.trim().to_string(),
                        op.to_string(),
                        right.trim().to_string(),
                    ));
                }
            }
        }
    }
    None
}

/// Mirrors the Python check `re.fullmatch(r"-?\d+", term)`.
fn is_integer_literal(term: &str) -> bool {
    let digits = term.strip_prefix('-').unwrap_or(term);
    !digits.is_empty() && digits.bytes().all(|b| b.is_ascii_digit())
}

/// Port of `counterexample._terms`: the non-literal symbols of a
/// relational text.
fn terms(text: &str) -> Vec<String> {
    match relation(text) {
        None => Vec::new(),
        Some((left, _, right)) => [left, right]
            .into_iter()
            .filter(|x| !is_integer_literal(x))
            .collect(),
    }
}

/// Port of `counterexample._value`.
fn value(term: &str, assignment: &BTreeMap<String, i64>) -> i64 {
    if is_integer_literal(term) {
        term.parse::<i64>()
            .expect("integer literal checked by is_integer_literal")
    } else {
        assignment[term]
    }
}

/// Port of `counterexample._holds`: `None` when the text is not a
/// relation over the supported operators.
fn holds(text: &str, assignment: &BTreeMap<String, i64>) -> Option<bool> {
    let (left, op, right) = relation(text)?;
    let a = value(&left, assignment);
    let b = value(&right, assignment);
    Some(match op.as_str() {
        ">=" => a >= b,
        "<=" => a <= b,
        ">" => a > b,
        "<" => a < b,
        "=" => a == b,
        _ => unreachable!("relation only yields the five operators"),
    })
}

/// Port of `counterexample._certify`.
fn certify(
    claim: &Claim,
    bound: i64,
    assignment: &BTreeMap<String, i64>,
) -> Option<Counterexample> {
    let premises: Vec<String> = claim.premises.iter().map(|p| p.text.clone()).collect();
    if premises.iter().any(|p| holds(p, assignment) != Some(true)) {
        return None;
    }
    if holds(&claim.conclusion, assignment) != Some(false) {
        return None;
    }
    // Payload identical to the Python:
    // json.dumps({"bound": bound, "assignment": assignment,
    //             "claim": claim.conclusion}, sort_keys=True)
    let assignment_val = JVal::Map(
        assignment
            .iter()
            .map(|(k, v)| (k.clone(), JVal::Int(*v)))
            .collect(),
    );
    let payload = JVal::Map(vec![
        ("assignment".into(), assignment_val),
        ("bound".into(), JVal::Int(bound)),
        ("claim".into(), JVal::Str(claim.conclusion.clone())),
    ]);
    Some(Counterexample {
        outcome: "refuted".into(),
        model: "integers".into(),
        bound,
        assignment: assignment.clone(),
        satisfied_premises: premises,
        violated_conclusion: claim.conclusion.clone(),
        fingerprint: sha256_hex(&dumps_default(&payload)),
        explanation:
            "All declared premises hold, but the conclusion fails in the bounded integer model."
                .into(),
    })
}

/// Port of `counterexample.find`: escalating bounded search over integer
/// assignments. `itertools.product` order is preserved (the last symbol
/// cycles fastest), so the first witness found is the same witness the
/// Python returns.
pub fn find(claim: &Claim, max_bound: i64) -> Counterexample {
    let mut symbol_set: Vec<String> = Vec::new();
    for premise in &claim.premises {
        for t in terms(&premise.text) {
            if !symbol_set.contains(&t) {
                symbol_set.push(t);
            }
        }
    }
    for t in terms(&claim.conclusion) {
        if !symbol_set.contains(&t) {
            symbol_set.push(t);
        }
    }
    symbol_set.sort();
    let symbols = symbol_set;

    for bound in 0..=max_bound {
        let range: Vec<i64> = (-bound..=bound).collect();
        let n = symbols.len();
        // Odometer over range^n with the last position cycling fastest,
        // matching itertools.product(range, repeat=n). n == 0 yields a
        // single empty assignment, as in Python.
        let mut indices = vec![0usize; n];
        loop {
            let assignment: BTreeMap<String, i64> = symbols
                .iter()
                .cloned()
                .zip(indices.iter().map(|&i| range[i]))
                .collect();
            if let Some(witness) = certify(claim, bound, &assignment) {
                return witness;
            }
            // Advance the odometer.
            let mut pos = n;
            loop {
                if pos == 0 {
                    break;
                }
                pos -= 1;
                indices[pos] += 1;
                if indices[pos] < range.len() {
                    break;
                }
                indices[pos] = 0;
                if pos == 0 {
                    // Wrapped around: this bound is exhausted.
                    pos = usize::MAX;
                    break;
                }
            }
            if pos == usize::MAX || n == 0 {
                break;
            }
        }
    }
    Counterexample {
        outcome: "no-witness".into(),
        model: "integers".into(),
        bound: max_bound,
        assignment: BTreeMap::new(),
        satisfied_premises: claim.premises.iter().map(|p| p.text.clone()).collect(),
        violated_conclusion: claim.conclusion.clone(),
        fingerprint: String::new(),
        explanation: "No counterexample was found within the declared bounded integer model; the claim is not proved.".into(),
    }
}

/// Port of `counterexample.find_for_claim` with the Python default
/// `max_bound = 3`. (Python returns `asdict(...)`; the Rust port returns
/// the struct itself.)
pub fn find_for_claim(claim: &Claim) -> Counterexample {
    find(claim, 3)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn claim(premises: &[&str], conclusion: &str) -> Claim {
        Claim::new(
            "Test",
            premises.iter().map(|p| Premise::new(*p)).collect(),
            conclusion,
        )
    }

    #[test]
    fn refutes_at_bound_zero_with_python_fingerprint() {
        // Golden generated by running the Python reference:
        // claim "x >= y |- x > y" is refuted by x = y = 0 at bound 0.
        let result = find(&claim(&["x >= y"], "x > y"), 3);
        assert_eq!(result.outcome, "refuted");
        assert_eq!(result.bound, 0);
        assert_eq!(result.assignment.get("x"), Some(&0));
        assert_eq!(result.assignment.get("y"), Some(&0));
        assert_eq!(
            result.fingerprint,
            "87cf2473ebb40c8ce85a43321ef9100035aad16e8610628b6b60649b1f7a01e8"
        );
        assert_eq!(result.violated_conclusion, "x > y");
    }

    #[test]
    fn no_witness_is_inconclusive_not_a_proof() {
        // Transitivity of >= has no integer counterexample.
        let result = find(&claim(&["x >= y", "y >= z"], "x >= z"), 3);
        assert_eq!(result.outcome, "no-witness");
        assert_eq!(result.bound, 3);
        assert!(result.assignment.is_empty());
        assert_eq!(result.fingerprint, "");
        assert!(result.explanation.contains("not proved"));
    }

    #[test]
    fn literal_terms_are_not_symbols() {
        // "x >= 5 |- x >= 3" holds for all integers; "x >= 5 |- x > 5"
        // is refuted at x = 5 (bound must reach 5).
        let ok = find(&claim(&["x >= 5"], "x >= 3"), 3);
        assert_eq!(ok.outcome, "no-witness");
        let bad = find(&claim(&["x >= 5"], "x > 5"), 5);
        assert_eq!(bad.outcome, "refuted");
        assert_eq!(bad.assignment.get("x"), Some(&5));
        assert_eq!(bad.bound, 5);
    }

    #[test]
    fn non_relational_premise_blocks_certification() {
        // A premise that is not a relation never holds (Python None),
        // so no certificate can be issued.
        let result = find(&claim(&["some prose premise"], "x > y"), 2);
        assert_eq!(result.outcome, "no-witness");
    }
}
