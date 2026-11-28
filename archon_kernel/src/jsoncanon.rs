//! Canonical JSON serialization byte-compatible with the CPython `json.dumps`
//! calls used by the 4Leibniz Python reference modules.
//!
//! The Python modules hash canonical JSON payloads with SHA-256
//! (`counterexample.py`, `bft.py`, `multiprover.py`), so hash parity requires
//! reproducing CPython's serialization exactly for the payload shapes
//! involved:
//!
//! * keys sorted lexicographically (`sort_keys=True`),
//! * either compact separators `(",", ":")` (`bft.py::_hash`) or CPython's
//!   default separators `(", ", ": ")` (`counterexample.py`,
//!   `multiprover.py`),
//! * string escaping with `ensure_ascii=True` (the CPython default): only
//!   printable ASCII `0x20..=0x7E` passes through unescaped (except `"` and
//!   `\`); everything else becomes `\uXXXX`, with astral characters emitted
//!   as UTF-16 surrogate pairs.
//!
//! This module implements the minimal JSON value model those payloads need.
//! It is *not* a general-purpose JSON library; `serde_json` is used where
//! arbitrary caller-supplied JSON must be parsed or measured (see
//! [`crate::zk_verify`]).

use sha2::{Digest, Sha256};

/// Minimal JSON value model covering the payload shapes hashed by the
/// Python reference modules.
#[derive(Debug, Clone, PartialEq)]
pub enum JVal {
    Str(String),
    Int(i64),
    Bool(bool),
    List(Vec<JVal>),
    /// Key/value pairs; serializers sort by key, mirroring
    /// `json.dumps(..., sort_keys=True)`.
    Map(Vec<(String, JVal)>),
}

/// Escape a string exactly as CPython `json.dumps(..., ensure_ascii=True)`
/// would (including the surrounding quotes).
pub fn escape_json_string(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    out.push('"');
    for ch in s.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0C}' => out.push_str("\\f"),
            c if ('\u{20}'..='\u{7E}').contains(&c) => out.push(c),
            c if (c as u32) <= 0xFFFF => {
                out.push_str(&format!("\\u{:04x}", c as u32));
            }
            c => {
                // Astral plane: CPython emits a UTF-16 surrogate pair.
                let v = (c as u32) - 0x1_0000;
                let hi = 0xD800 + (v >> 10);
                let lo = 0xDC00 + (v & 0x3FF);
                out.push_str(&format!("\\u{:04x}\\u{:04x}", hi, lo));
            }
        }
    }
    out.push('"');
    out
}

fn write_sorted_map(pairs: &[(String, JVal)], item_sep: &str, kv_sep: &str, out: &mut String) {
    let mut sorted: Vec<&(String, JVal)> = pairs.iter().collect();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));
    out.push('{');
    for (i, (k, v)) in sorted.iter().enumerate() {
        if i > 0 {
            out.push_str(item_sep);
        }
        out.push_str(&escape_json_string(k));
        out.push_str(kv_sep);
        write_val(v, item_sep, kv_sep, out);
    }
    out.push('}');
}

fn write_val(v: &JVal, item_sep: &str, kv_sep: &str, out: &mut String) {
    match v {
        JVal::Str(s) => out.push_str(&escape_json_string(s)),
        JVal::Int(n) => out.push_str(&n.to_string()),
        JVal::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        JVal::List(items) => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push_str(item_sep);
                }
                write_val(item, item_sep, kv_sep, out);
            }
            out.push(']');
        }
        JVal::Map(pairs) => write_sorted_map(pairs, item_sep, kv_sep, out),
    }
}

/// Serialize with CPython's default separators `(", ", ": ")`, as produced by
/// `json.dumps(value, sort_keys=True)`.
pub fn dumps_default(v: &JVal) -> String {
    let mut out = String::new();
    write_val(v, ", ", ": ", &mut out);
    out
}

/// Serialize with compact separators `(",", ":")`, as produced by
/// `json.dumps(value, sort_keys=True, separators=(",", ":"))`.
pub fn dumps_compact(v: &JVal) -> String {
    let mut out = String::new();
    write_val(v, ",", ":", &mut out);
    out
}

/// SHA-256 of the UTF-8 encoding, lowercase hex — mirrors
/// `hashlib.sha256(payload.encode()).hexdigest()`.
pub fn sha256_hex(data: &str) -> String {
    let digest = Sha256::digest(data.as_bytes());
    let mut out = String::with_capacity(64);
    for byte in digest {
        out.push_str(&format!("{:02x}", byte));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compact_payload_matches_cpython_bft_hash_input() {
        // Golden string produced by CPython json.dumps for the BFT votes
        // payload of tests/test_phase7.py's honest-quorum scenario.
        let vote = |node: &str| {
            JVal::Map(vec![
                ("node_id".into(), JVal::Str(node.into())),
                ("nonce".into(), JVal::Str(String::new())),
                ("proposal_hash".into(), JVal::Str("p".into())),
                ("round".into(), JVal::Int(0)),
                ("status".into(), JVal::Str("proven".into())),
            ])
        };
        let payload = JVal::Map(vec![(
            "votes".into(),
            JVal::List(vec![vote("n0"), vote("n1"), vote("n2"), vote("n3")]),
        )]);
        assert_eq!(
            dumps_compact(&payload),
            r#"{"votes":[{"node_id":"n0","nonce":"","proposal_hash":"p","round":0,"status":"proven"},{"node_id":"n1","nonce":"","proposal_hash":"p","round":0,"status":"proven"},{"node_id":"n2","nonce":"","proposal_hash":"p","round":0,"status":"proven"},{"node_id":"n3","nonce":"","proposal_hash":"p","round":0,"status":"proven"}]}"#
        );
        assert_eq!(
            sha256_hex(&dumps_compact(&payload)),
            "7dd7aa715f08d4751f67f18d546835edbc34babbc5322810d329a0a2fbabe8da"
        );
    }

    #[test]
    fn default_payload_matches_cpython_counterexample_fingerprint_input() {
        // Golden string produced by CPython json.dumps (default separators)
        // for the counterexample fingerprint payload.
        let payload = JVal::Map(vec![
            (
                "assignment".into(),
                JVal::Map(vec![("x".into(), JVal::Int(0)), ("y".into(), JVal::Int(0))]),
            ),
            ("bound".into(), JVal::Int(0)),
            ("claim".into(), JVal::Str("x > y".into())),
        ]);
        assert_eq!(
            dumps_default(&payload),
            r#"{"assignment": {"x": 0, "y": 0}, "bound": 0, "claim": "x > y"}"#
        );
        assert_eq!(
            sha256_hex(&dumps_default(&payload)),
            "87cf2473ebb40c8ce85a43321ef9100035aad16e8610628b6b60649b1f7a01e8"
        );
    }

    #[test]
    fn escaping_matches_ensure_ascii() {
        assert_eq!(escape_json_string("a\"b\\c\nd"), r#""a\"b\\c\nd""#);
        assert_eq!(escape_json_string("café"), r#""caf\u00e9""#);
        assert_eq!(escape_json_string("\u{1F600}"), r#""\ud83d\ude00""#);
        assert_eq!(escape_json_string("\u{7F}"), r#""\u007f""#);
    }
}
