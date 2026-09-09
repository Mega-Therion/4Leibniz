"""HTR engine for Leibniz folio transcription, with explicit provenance.

The central rule of this module: **synthetic text is never allowed to look like
a transcription.** A caller must ask for simulation, and every artifact derived
from simulated output carries a marker saying so.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from PIL import Image

from .latin_morphology import expand_abbreviations


class Provenance(str, Enum):
    """Where a piece of text came from. Travels with the text everywhere."""

    TRANSCRIBED = "transcribed"
    """Produced by a real HTR model reading real pixels."""

    SIMULATED = "simulated"
    """Fixture text. Not evidence. Never promotable to the corpus."""


class HTRModelUnavailable(RuntimeError):
    """Raised when a real transcription was requested and no model could load.

    This is deliberately fatal. The previous design caught the load failure and
    silently set `force_simulation = True`, so a caller asking for a real
    transcription received fabricated Latin at 0.93 confidence with nothing
    anywhere recording the substitution. Measured: five BLANK WHITE images
    produced five sentences of scholarly Latin and the quality audit returned
    PASSED at 0.866 average confidence.

    A pipeline that cannot transcribe must say so, not invent.
    """


@dataclass
class LineTranscription:
    text: str
    confidence: float
    provenance: Provenance

    @property
    def is_evidence(self) -> bool:
        return self.provenance is Provenance.TRANSCRIBED


# Fixture sentences for tests and demos. Real Leibnizian Latin, but NOT read
# from any image -- see Provenance.SIMULATED.
_SIMULATION_CORPUS = [
    "In corporibus praeter extensionem inest conatus omnis motum incipiens.",
    "Hinc patet vim vivam a vi mortua toto caelo differre.",
    "Monas est substantia simplex quae aggregatione constat in unum composita.",
    "Calculus ratiocinator regulas demonstrationis tradit infallibiles.",
    "Actionis quantitas semper in collisione corporum conservari reperitur.",
]


class LeibnizHTREngine:
    def __init__(
        self,
        checkpoint: str = "microsoft/trocr-large-stage1",
        device: Optional[str] = None,
        batch_size: int = 8,
        simulate: bool = False,
    ) -> None:
        """Build an engine.

        `simulate=True` is an explicit request for fixture output. When it is
        False and the model cannot be loaded, this raises `HTRModelUnavailable`
        rather than quietly degrading.
        """
        self.device = device or "cpu"
        self.batch_size = batch_size
        self.simulate = simulate
        self.model = None
        self.processor = None

        if simulate:
            return

        try:
            import torch
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        except ImportError as exc:
            raise HTRModelUnavailable(
                "torch/transformers are not installed, so no transcription is "
                "possible. Install them, or pass simulate=True to request "
                "clearly-marked fixture output."
            ) from exc

        try:
            self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
            self.processor = TrOCRProcessor.from_pretrained(checkpoint)
            self.model = VisionEncoderDecoderModel.from_pretrained(checkpoint).to(self.device)
            self.model.eval()
        except Exception as exc:
            raise HTRModelUnavailable(
                f"failed to load HTR checkpoint {checkpoint!r}: {exc}"
            ) from exc

    def transcribe(self, line_images: List[Image.Image]) -> List[LineTranscription]:
        if not line_images:
            return []
        if self.simulate:
            return [
                LineTranscription(
                    text=expand_abbreviations(_SIMULATION_CORPUS[i % len(_SIMULATION_CORPUS)]),
                    confidence=0.93 if i != 3 else 0.61,
                    provenance=Provenance.SIMULATED,
                )
                for i, _ in enumerate(line_images)
            ]
        return self._transcribe_real(line_images)

    def _transcribe_real(self, line_images: List[Image.Image]) -> List[LineTranscription]:
        import torch

        indexed = sorted(enumerate(line_images), key=lambda x: x[1].size[0] / max(x[1].size[1], 1))
        sorted_indices, sorted_crops = zip(*indexed)
        results: List[Optional[LineTranscription]] = [None] * len(line_images)

        for i in range(0, len(sorted_crops), self.batch_size):
            chunk = list(sorted_crops[i : i + self.batch_size])
            pixel_values = self.processor(chunk, return_tensors="pt").pixel_values.to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    pixel_values, max_new_tokens=96, num_beams=2,
                    return_dict_in_generate=True, output_scores=True, early_stopping=True,
                )
            transition_scores = self.model.compute_transition_scores(
                outputs.sequences, outputs.scores, outputs.beam_indices, normalize_logits=True
            )
            batch_texts = self.processor.batch_decode(outputs.sequences, skip_special_tokens=True)
            for j, (text, trans_score) in enumerate(zip(batch_texts, transition_scores)):
                valid = trans_score[trans_score != -float("inf")]
                conf = torch.exp(valid.mean()).item() if valid.numel() > 0 else 0.0
                results[sorted_indices[i + j]] = LineTranscription(
                    text=expand_abbreviations(text),
                    confidence=round(conf, 4),
                    provenance=Provenance.TRANSCRIBED,
                )
        return [r for r in results if r is not None]
