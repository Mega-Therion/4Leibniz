import Mathlib

namespace Leibniz.Sources

structure HistoricalSource where
  id : String
  title : String
  date : String
  citation : String
  folio : Option String := none
  deriving Repr, Inhabited

def concordance : List HistoricalSource := [
  { id := "characteristica", title := "De Arte Combinatoria", date := "1666", citation := "Universal characteristic and combinatorics" },
  { id := "vis-viva", title := "Specimen Dynamicum", date := "1695", citation := "Living force and dynamics" },
  { id := "monadologia", title := "Monadologia", date := "1714", citation := "Monads and relational space" },
  { id := "clarke", title := "Leibniz–Clarke Correspondence", date := "1715–1716", citation := "Relational account of space and time" }
]

def sourceFor (id : String) : Option HistoricalSource := concordance.find? (·.id = id)

end Leibniz.Sources
