/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                      LEIBNIZ: DYADICA                                ║
  ║  De Progressione Dyadica (1679) — Binary Genesis & Tension          ║
  ╚═══════════════════════════════════════════════════════════════════════╝

  PILLAR 2: The dual states in tension. IO (Void→Unity) and OI (Unity→Void)
  are the two directed channels of information flow. Their balanced tension
  is the entropy conservation condition.
-/

import Leibniz.Characteristica

namespace Leibniz.Dyadica

open Leibniz.Characteristica

/--
  DIRECTIO: The two fundamental directions of information tension.
  - IO: Void-to-Unity (Nihil → Ens) — ascending, generative
  - OI: Unity-to-Void (Ens → Nihil) — descending, dissipative
-/
inductive Directio where
  | IO : Directio  -- Void → Unity
  | OI : Directio  -- Unity → Void
  deriving DecidableEq, Repr

/-- The directed transition: which pair of states this direction connects. -/
def transitio (d : Directio) : Dyas × Dyas :=
  match d with
  | Directio.IO => (Dyas.Nihil, Dyas.Ens)
  | Directio.OI => (Dyas.Ens,   Dyas.Nihil)

/-- The tension carried by a directed transition. -/
def tensio_directa (d : Directio) : Nat :=
  match d with
  | Directio.IO => tensio Dyas.Nihil Dyas.Ens
  | Directio.OI => tensio Dyas.Ens   Dyas.Nihil

/-- [P] Both directions carry equal tension — the fundamental dual balance. -/
theorem dual_tension_balance : tensio_directa Directio.IO = tensio_directa Directio.OI := by
  rfl

/-- [P] IO and OI are structural inverses: the target of one is the source of the other. -/
theorem transitio_inverse :
    (transitio Directio.IO).2 = (transitio Directio.OI).1 ∧
    (transitio Directio.IO).1 = (transitio Directio.OI).2 := by
  constructor <;> rfl

/-- Total tension of a dual-state pair (symmetric in both orders). -/
def tensio_totalis (d₁ d₂ : Dyas) : Nat :=
  tensio d₁ d₂ + tensio d₂ d₁

/-- [P] Total tension is symmetric. -/
theorem tensio_totalis_symm (d₁ d₂ : Dyas) : tensio_totalis d₁ d₂ = tensio_totalis d₂ d₁ := by
  unfold tensio_totalis
  rw [Nat.add_comm]

/-- [P] Entropy balance: a state in tension with itself carries no information. -/
theorem entropy_balance (d : Dyas) : tensio_totalis d d = 0 := by
  unfold tensio_totalis
  rw [tensio_self]

/-- [P] Entropy exchange: distinct states carry exactly 2 units of total tension. -/
theorem entropy_exchange (d₁ d₂ : Dyas) (h : d₁ ≠ d₂) : tensio_totalis d₁ d₂ = 2 := by
  unfold tensio_totalis
  cases d₁ <;> cases d₂ <;> first | contradiction | rfl

/--
  Discrete information projection: counts coherent (Ens) states in a system.
  This is the discrete analog of projecting the binary field onto a boundary.
-/
def informatio_projectio : List Dyas → Nat
  | [] => 0
  | Dyas.Ens :: rest => 1 + informatio_projectio rest
  | Dyas.Nihil :: rest => informatio_projectio rest

/-- [P] Information projection is non-negative. -/
theorem informatio_nonneg (states : List Dyas) : informatio_projectio states ≥ 0 := by
  exact Nat.zero_le _

/-- [P] Pure void carries no information. -/
theorem informatio_pura_nihil : informatio_projectio [Dyas.Nihil] = 0 := by
  rfl

/-- [P] A single Ens state carries one unit of information. -/
theorem informatio_unum_ens : informatio_projectio [Dyas.Ens] = 1 := by
  rfl

end Leibniz.Dyadica
