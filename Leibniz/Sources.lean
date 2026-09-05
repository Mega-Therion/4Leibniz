import Mathlib

namespace Leibniz.Sources

structure HistoricalSource where
  id : String
  title : String
  date : String
  citation : String
  folio : Option String := none
  corpusPath : Option String := none
  rank : Nat := 0
  status : String := "verified"
  deriving Repr, Inhabited

def concordance : List HistoricalSource := [
  { id := "analysis-situs-1679", title := "Analysis situs", date := "1679",
    citation := "Leibniz-Archiv Hannover, LH XXXV, 1, 9; Gerhardt, Die mathematischen Schriften, vol. 5",
    folio := some "LH XXXV, 1, 9", corpusPath := some "corpus/latin/analysis_situs_1679.la.md",
    rank := 1, status := "source-identified-transcription-needed" },
  { id := "initia-rerum-mathematicarum-metaphysica-1715",
    title := "Initia rerum mathematicarum metaphysica", date := "1715",
    citation := "Leibniz-Archiv Hannover, LH XXXV, 1, 15; Akademie-Ausgabe, series VII where applicable",
    folio := some "LH XXXV, 1, 15", corpusPath := some "corpus/latin/initia_rerum_1715.la.md",
    rank := 1, status := "source-identified-transcription-needed" },
  { id := "de-progressione-dyadica-1679", title := "De progressione dyadica", date := "1679",
    citation := "Leibniz-Archiv Hannover, LH XXXV, 3, 2; Gerhardt, Die mathematischen Schriften, vol. 5",
    folio := some "LH XXXV, 3, 2", corpusPath := some "corpus/latin/de_progressione_dyadica_1679.la.md",
    rank := 2, status := "source-identified-transcription-needed" },
  { id := "characteristica", title := "De Arte Combinatoria", date := "1666",
    citation := "Universal characteristic and combinatorics", rank := 0 },
  { id := "vis-viva", title := "Specimen Dynamicum", date := "1695",
    citation := "Living force and dynamics", rank := 0 },
  { id := "monadologia", title := "Monadologia", date := "1714",
    citation := "Monads and relational space", rank := 0 },
  { id := "clarke", title := "Leibniz–Clarke Correspondence", date := "1715–1716",
    citation := "Relational account of space and time", rank := 0 }
]

def sourceFor (id : String) : Option HistoricalSource := concordance.find? (·.id = id)

end Leibniz.Sources
