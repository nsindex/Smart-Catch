import json
import logging
import os
import re
import tkinter as tk
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

        self._build_notebook()
        self._append_result("INFO", "Smart-Catch local GUI is ready.")
        self._load_keywords()

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

    def browse_config(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="Select config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(DEFAULT_CONFIG_PATH).parent),
        )
        if selected_path:
            self.config_path_var.set(selected_path)
            self._append_result("INFO", f"Config path selected: {selected_path}")

    def run_pipeline(self) -> None:
        config_path = self.config_path_var.get().strip() or DEFAULT_CONFIG_PATH
        self._set_running_state(True)
        self._append_result("INFO", "----------------------------------------")
        self._append_result("INFO", f"Run started: {config_path}")
        self.root.update_idletasks()

        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            if not config_file.is_file():
                raise FileNotFoundError(f"Config path is not a file: {config_path}")

            setup_logging()
            config = load_config(config_path)
            setup_logging(config.get("logging", {}))
            LOGGER.info("GUI execution started with config: %s", config_path)

            output_config = config.get("output", {})
            exploration_dir = output_config.get("exploration_dir", "")
            monitoring_dir = output_config.get("monitoring_dir", "")
            self.exploration_path_var.set(
                str(Path(exploration_dir) / "collected_articles.md")
                if exploration_dir
                else ""
            )
            self.monitoring_path_var.set(
                str(Path(monitoring_dir) / "monitored_articles.md")
                if monitoring_dir
                else ""
            )

            markdown = run_rss_pipeline(config_path)
            article_count = len(ARTICLE_HEADING_PATTERN.findall(markdown))
            self.status_var.set("Status: Success")
            self._append_result("SUCCESS", "Execution completed successfully.")
            self._append_result("INFO", f"Exploration output: {self.exploration_path_var.get()}")
            self._append_result("INFO", f"Monitoring output: {self.monitoring_path_var.get()}")
            self._append_result("INFO", f"Exploration article count: {article_count}")
            self._refresh_open_buttons()
            LOGGER.info("GUI execution completed successfully")
        except Exception as exc:
            self.status_var.set("Status: Failed")
            self._append_result("ERROR", f"Execution failed for config: {config_path}")
            self._append_result("ERROR", str(exc))
            LOGGER.exception("GUI execution failed")
        finally:
            self._set_running_state(False)
            self.root.update_idletasks()

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
