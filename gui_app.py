import json
import logging
import os
import queue
import re
import threading
import tkinter as tk
import traceback
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk

from src.config_loader import load_config
from src.logging_config import setup_logging
from src.pipelines.rss_pipeline import run_rss_pipeline


DEFAULT_CONFIG_PATH = "config/config.json"
LOGGER = logging.getLogger(__name__)
ARTICLE_HEADING_PATTERN = re.compile(r"^## ", re.MULTILINE)


class SmartCatchGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart-Catch")
        self.root.geometry("900x600")

        self.config_path_var = tk.StringVar(value=DEFAULT_CONFIG_PATH)
        self.exploration_path_var = tk.StringVar(value="")
        self.monitoring_path_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Status: Ready")
        self._worker_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._pipeline_thread: threading.Thread | None = None

        self._build_notebook()
        self._append_result("INFO", "Smart-Catch local GUI is ready.")
        self._load_keywords()
        self.root.after(100, self._check_ollama_on_startup)

    def _build_notebook(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        main_frame = tk.Frame(self.notebook)
        self.notebook.add(main_frame, text="メイン")

        keyword_frame = tk.Frame(self.notebook)
        self.notebook.add(keyword_frame, text="キーワード管理")

        self._build_main_tab(main_frame)
        self._build_keyword_tab(keyword_frame)

    def _build_main_tab(self, frame: tk.Frame) -> None:
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

        tk.Label(frame, text="Config Path").grid(
            row=0, column=0, padx=12, pady=12, sticky="w"
        )
        tk.Entry(frame, textvariable=self.config_path_var).grid(
            row=0, column=1, padx=12, pady=12, sticky="ew"
        )
        tk.Button(frame, text="Browse", command=self.browse_config).grid(
            row=0, column=2, padx=12, pady=12, sticky="ew"
        )

        self.run_button = tk.Button(frame, text="Run", command=self.run_pipeline)
        self.run_button.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
        tk.Label(frame, textvariable=self.status_var, anchor="w").grid(
            row=1, column=1, columnspan=2, padx=12, pady=4, sticky="ew"
        )

        tk.Label(frame, text="Exploration Output").grid(
            row=2, column=0, padx=12, pady=4, sticky="w"
        )
        tk.Label(frame, textvariable=self.exploration_path_var, anchor="w").grid(
            row=2, column=1, padx=12, pady=4, sticky="ew"
        )
        self.open_exploration_button = tk.Button(
            frame,
            text="Open",
            command=lambda: self.open_output_file(self.exploration_path_var.get()),
            state=tk.DISABLED,
        )
        self.open_exploration_button.grid(
            row=2, column=2, padx=12, pady=4, sticky="ew"
        )

        tk.Label(frame, text="Monitoring Output").grid(
            row=3, column=0, padx=12, pady=4, sticky="w"
        )
        tk.Label(frame, textvariable=self.monitoring_path_var, anchor="w").grid(
            row=3, column=1, padx=12, pady=4, sticky="ew"
        )
        self.open_monitoring_button = tk.Button(
            frame,
            text="Open",
            command=lambda: self.open_output_file(self.monitoring_path_var.get()),
            state=tk.DISABLED,
        )
        self.open_monitoring_button.grid(
            row=3, column=2, padx=12, pady=4, sticky="ew"
        )

        self.result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.result_text.grid(
            row=4, column=0, columnspan=3, padx=12, pady=12, sticky="nsew"
        )
        self.result_text.configure(state=tk.DISABLED)

    def _build_keyword_tab(self, frame: tk.Frame) -> None:
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        # --- Listbox + Scrollbar ---
        list_frame = tk.Frame(frame)
        list_frame.grid(row=0, column=0, columnspan=3, padx=12, pady=12, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.keyword_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.keyword_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.keyword_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.keyword_listbox.configure(yscrollcommand=scrollbar.set)
        self.keyword_listbox.bind("<<ListboxSelect>>", self._on_keyword_select)

        # --- 追加エリア ---
        tk.Label(frame, text="追加:").grid(row=1, column=0, padx=12, pady=4, sticky="w")
        self.keyword_entry = tk.Entry(frame)
        self.keyword_entry.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        tk.Button(frame, text="追加", command=self._add_keyword).grid(
            row=1, column=2, padx=12, pady=4, sticky="ew"
        )

        # --- 削除・保存ボタン ---
        self.delete_keyword_button = tk.Button(
            frame, text="選択したキーワードを削除", command=self._delete_keyword, state=tk.DISABLED
        )
        self.delete_keyword_button.grid(row=2, column=0, columnspan=2, padx=12, pady=8, sticky="ew")
        tk.Button(frame, text="保存", command=self._save_keywords).grid(
            row=2, column=2, padx=12, pady=8, sticky="ew"
        )

    def _on_keyword_select(self, event: tk.Event) -> None:
        selected = self.keyword_listbox.curselection()
        self.delete_keyword_button.configure(
            state=tk.NORMAL if selected else tk.DISABLED
        )

    def _check_ollama_on_startup(self) -> None:
        from src.utils.ollama_health import ensure_ollama_running, is_ollama_running

        if is_ollama_running():
            self._append_result("INFO", "Ollama: 起動確認済み")
            return

        self._append_result("WARNING", "Ollama未起動。自動起動を試みています...")
        success = ensure_ollama_running()
        if success:
            self._append_result("INFO", "Ollama: 自動起動成功")
        else:
            self._append_result("WARNING", "Ollama起動失敗。要約・翻訳はフォールバックになります")

    def _load_keywords(self) -> None:
        self.keyword_listbox.delete(0, tk.END)
        config_path = Path(self.config_path_var.get())
        if not config_path.exists():
            self._append_result("ERROR", f"キーワード読み込み失敗: ファイルが見つかりません: {config_path}")
            return
        try:
            with config_path.open(encoding="utf-8") as f:
                config = json.load(f)
            keywords = config.get("monitoring", {}).get("keywords")
            if keywords is None:
                self._append_result("ERROR", "キーワード読み込み失敗: monitoring.keywords キーが見つかりません")
                return
            for kw in keywords:
                self.keyword_listbox.insert(tk.END, kw)
        except Exception as exc:
            self._append_result("ERROR", f"キーワード読み込み失敗: {exc}")

    def _add_keyword(self) -> None:
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            return
        existing = list(self.keyword_listbox.get(0, tk.END))
        if keyword in existing:
            return
        self.keyword_listbox.insert(tk.END, keyword)
        self.keyword_entry.delete(0, tk.END)

    def _delete_keyword(self) -> None:
        selected = self.keyword_listbox.curselection()
        if not selected:
            return
        self.keyword_listbox.delete(selected[0])
        self.delete_keyword_button.configure(state=tk.DISABLED)

    def _save_keywords(self) -> None:
        config_path = Path(self.config_path_var.get())
        tmp_path = config_path.with_suffix(".tmp")
        try:
            with config_path.open(encoding="utf-8") as f:
                config = json.load(f)
            keywords = list(self.keyword_listbox.get(0, tk.END))
            config.setdefault("monitoring", {})["keywords"] = keywords
            tmp_path.write_text(
                json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            tmp_path.replace(config_path)
            self._append_result("INFO", f"キーワードを保存しました ({len(keywords)} 件): {config_path}")
        except Exception as exc:
            self._append_result("ERROR", f"キーワード保存失敗: {exc}")
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    def browse_config(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="Select config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(DEFAULT_CONFIG_PATH).parent),
        )
        if selected_path:
            self.config_path_var.set(selected_path)
            self._append_result("INFO", f"Config path selected: {selected_path}")
            self._load_keywords()

    def run_pipeline(self) -> None:
        config_path = self.config_path_var.get().strip() or DEFAULT_CONFIG_PATH
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            if not config_file.is_file():
                raise FileNotFoundError(f"Config path is not a file: {config_path}")

            # Run時チェック：起動時の自動起動とは別に状態を確認してWARNINGを出す
            # （自動起動は起動時に試み済みのため、ここでは is_running チェックのみ）
            from src.utils.ollama_health import is_ollama_running
            if not is_ollama_running():
                self._append_result("WARNING", "Ollama未起動。要約・翻訳はフォールバックで処理します")
            config = load_config(config_path)
            output_config = config.get("output", {})
            exploration_dir = output_config.get("exploration_dir", "")
            monitoring_dir = output_config.get("monitoring_dir", "")
            self.exploration_path_var.set(
                str(Path(exploration_dir) / "collected_articles.md")
                if exploration_dir
                else ""
            )
            self.monitoring_path_var.set(
                str(Path(monitoring_dir) / "archive" / "monitored_articles.md")
                if monitoring_dir
                else ""
            )
        except Exception as exc:
            self.status_var.set("Status: Failed")
            self._append_result("ERROR", f"Execution failed for config: {config_path}")
            self._append_result("ERROR", str(exc))
            LOGGER.exception("GUI execution failed")
            self._set_running_state(False)
            self.root.update_idletasks()
            return

        self._set_running_state(True)
        self._append_result("INFO", "----------------------------------------")
        self._append_result("INFO", f"Run started: {config_path}")
        self.root.update_idletasks()

        self._pipeline_thread = threading.Thread(
            target=self._run_pipeline_worker,
            args=(config_path,),
            name="smart-catch-pipeline",
            daemon=True,
        )
        self._pipeline_thread.start()
        self.root.after(100, self._process_worker_queue)

    def _run_pipeline_worker(self, config_path: str) -> None:
        try:
            setup_logging()
            config = load_config(config_path)
            setup_logging(config.get("logging", {}))
            LOGGER.info("GUI execution started with config: %s", config_path)

            result = run_rss_pipeline(
                config_path,
                progress_callback=self._publish_progress,
            )
            if not isinstance(result, tuple) or len(result) != 2:
                raise ValueError(
                    "run_rss_pipeline() must return a 2-item tuple: (markdown, purged_files)"
                )

            markdown, purged_files = result
            if not isinstance(markdown, str):
                raise TypeError("run_rss_pipeline()[0] must be a string markdown")
            if not isinstance(purged_files, list):
                raise TypeError("run_rss_pipeline()[1] must be a list of purged files")

            self._worker_queue.put(("success", (markdown, purged_files)))
        except Exception as exc:
            error_message = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )
            self._worker_queue.put(("error", error_message))

    def _publish_progress(self, level: str, message: str) -> None:
        self._worker_queue.put(("progress", (level, message)))

    def _process_worker_queue(self) -> None:
        keep_polling = True

        while True:
            try:
                event_type, payload = self._worker_queue.get_nowait()
            except queue.Empty:
                break

            if event_type == "progress":
                level, message = payload
                self._append_result(level, message)
                continue

            if event_type == "success":
                markdown, purged_files = payload
                article_count = len(ARTICLE_HEADING_PATTERN.findall(markdown))
                self.status_var.set("Status: Success")
                self._append_result("SUCCESS", "Execution completed successfully.")
                self._append_result(
                    "INFO", f"Exploration output: {self.exploration_path_var.get()}"
                )
                self._append_result(
                    "INFO", f"Monitoring output: {self.monitoring_path_var.get()}"
                )
                self._append_result("INFO", f"Exploration article count: {article_count}")
                if purged_files:
                    self._append_result("INFO", f"Purged {len(purged_files)} old file(s):")
                    for pf in purged_files:
                        self._append_result("INFO", f"  Purged: {Path(pf).name}")
                self._refresh_open_buttons()
                self._set_running_state(False)
                LOGGER.info("GUI execution completed successfully")
                keep_polling = False
                continue

            if event_type == "error":
                self.status_var.set("Status: Failed")
                self._append_result(
                    "ERROR",
                    f"Execution failed for config: {self.config_path_var.get().strip() or DEFAULT_CONFIG_PATH}",
                )
                self._append_result("ERROR", str(payload).strip())
                LOGGER.error("GUI execution failed:\n%s", payload)
                self._set_running_state(False)
                keep_polling = False

        if keep_polling and self._pipeline_thread and self._pipeline_thread.is_alive():
            self.root.after(100, self._process_worker_queue)
        elif keep_polling:
            self._set_running_state(False)

    def open_output_file(self, file_path: str) -> None:
        if not file_path:
            self._append_result("ERROR", "Output path is not available yet.")
            return

        path = Path(file_path)
        if not path.exists():
            self._append_result("ERROR", f"Output file not found: {file_path}")
            return

        try:
            os.startfile(path)  # type: ignore[attr-defined]
            self._append_result("INFO", f"Opened output file: {file_path}")
        except Exception as exc:
            self._append_result("ERROR", f"Failed to open file: {exc}")

    def _set_running_state(self, is_running: bool) -> None:
        self.run_button.configure(state=tk.DISABLED if is_running else tk.NORMAL)
        self.status_var.set("Status: Running" if is_running else self.status_var.get())

    def _refresh_open_buttons(self) -> None:
        self.open_exploration_button.configure(
            state=tk.NORMAL if Path(self.exploration_path_var.get()).exists() else tk.DISABLED
        )
        self.open_monitoring_button.configure(
            state=tk.NORMAL if Path(self.monitoring_path_var.get()).exists() else tk.DISABLED
        )

    def _append_result(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.result_text.see(tk.END)
        self.result_text.configure(state=tk.DISABLED)


def main() -> None:
    root = tk.Tk()
    SmartCatchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
