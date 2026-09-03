import Lake
open Lake DSL

package «Leibniz» where
  moreLeanArgs := #["-DwarningAsError=false"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "master"

@[default_target]
lean_lib «Leibniz» where
  roots := #[`Leibniz]
