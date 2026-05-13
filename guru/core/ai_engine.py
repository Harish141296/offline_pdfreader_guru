"""
guru/core/ai_engine.py

Ollama integration with streaming, background QThread worker.
"""

from __future__ import annotations
import ollama
from PyQt6.QtCore import QThread, pyqtSignal
from guru.core.prompt_templates import build_explanation_prompt, build_followup_prompt
from guru.core.extractor import ExtractionResult


class ExplainWorker(QThread):
    token_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model: str, prompt: str, parent=None):
        super().__init__(parent)
        self._model = model
        self._prompt = prompt
        self._stopped = False

    def stop(self):
        self._stopped = True

    def run(self):
        full_response = ""
        try:
            stream = ollama.generate(model=self._model, prompt=self._prompt, stream=True)
            for chunk in stream:
                if self._stopped:
                    break
                if hasattr(chunk, "response"):
                    token = chunk.response or ""
                elif isinstance(chunk, dict):
                    token = chunk.get("response", "")
                else:
                    token = ""
                if token:
                    full_response += token
                    self.token_received.emit(token)
            if not self._stopped:
                self.finished.emit(full_response)
        except ollama.ResponseError as e:
            self.error.emit(
                f"Ollama model error: {e.error}\n\n"
                f"Make sure '{self._model}' is installed:\n"
                f"  ollama pull {self._model}"
            )
        except Exception as e:
            err_str = str(e)
            if "Connection refused" in err_str or "connect" in err_str.lower():
                self.error.emit(
                    "Cannot connect to Ollama.\n\nStart it in your terminal:\n  ollama serve"
                )
            else:
                self.error.emit(f"Unexpected error: {err_str}")


class AIEngine:
    def __init__(self):
        self._model = "mistral"
        self._worker: ExplainWorker | None = None

    def set_model(self, model_name: str):
        self._model = model_name

    @property
    def current_model(self):
        return self._model

    def explain(self, result: ExtractionResult, on_token, on_done, on_error):
        self._cancel_current()
        prompt = build_explanation_prompt(result.text, result.display_page)
        self._start_worker(prompt, on_token, on_done, on_error)

    def ask(self, result: ExtractionResult, question: str, prior_explanation: str,
            on_token, on_done, on_error):
        self._cancel_current()
        prompt = build_followup_prompt(result.text, result.display_page, question, prior_explanation)
        self._start_worker(prompt, on_token, on_done, on_error)

    def cancel(self):
        self._cancel_current()

    def _start_worker(self, prompt, on_token, on_done, on_error):
        self._worker = ExplainWorker(model=self._model, prompt=prompt)
        self._worker.token_received.connect(on_token)
        self._worker.finished.connect(on_done)
        self._worker.error.connect(on_error)
        self._worker.start()

    def _cancel_current(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(2000)


def fetch_available_models() -> list[str]:
    try:
        result = ollama.list()
        if hasattr(result, "models"):
            models = result.models
            return [m.model for m in models if hasattr(m, "model")]
        else:
            models = result.get("models", [])
            return [m.get("name") or m.get("model") for m in models
                    if m.get("name") or m.get("model")]
    except Exception as e:
        print(f"[fetch_models] {e}")
        return []


def is_ollama_running() -> bool:
    try:
        ollama.list()
        return True
    except Exception:
        return False
