from pathlib import Path
from collections import defaultdict
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build"
}


LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".sql": "SQL",
    ".java": "Java",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C"
}


def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except Exception:
        return 0


def find_readme(repo):

    candidates = [
        "README.md",
        "readme.md",
        "Readme.md",
        "README.MD",
        "README.md.md"
    ]

    for candidate in candidates:
        path = repo / candidate
        if path.exists():
            return path

    return None


def extract_readme_sections(readme_path):

    result = {
        "overview": "",
        "technologies": [],
        "features": []
    }

    if not readme_path:
        return result

    try:
        text = readme_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        return result

    lines = text.splitlines()

    current_section = None

    overview_lines = []
    technologies = []
    features = []

    for line in lines:

        stripped = line.strip()

        lower = stripped.lower()

        if lower == "## overview":
            current_section = "overview"
            continue

        if lower == "## technologies":
            current_section = "technologies"
            continue

        if lower == "## features":
            current_section = "features"
            continue

        if stripped.startswith("## "):
            current_section = None
            continue

        if current_section == "overview":

            if stripped:
                overview_lines.append(stripped)

        elif current_section == "technologies":

            if stripped.startswith("-"):
                technologies.append(
                    stripped.lstrip("- ").strip()
                )

        elif current_section == "features":

            if stripped.startswith("-"):
                features.append(
                    stripped.lstrip("- ").strip()
                )

    result["overview"] = "\n".join(overview_lines)
    result["technologies"] = technologies
    result["features"] = features

    return result


def analyse_repository(repo_path):

    repo = Path(repo_path)

    total_files = 0
    total_folders = 0
    total_lines = 0

    language_counts = defaultdict(int)

    for item in repo.rglob("*"):

        if any(part in IGNORE_DIRS for part in item.parts):
            continue

        if item.is_dir():
            total_folders += 1
            continue

        total_files += 1

        suffix = item.suffix.lower()

        if suffix in LANGUAGE_MAP:
            language_counts[LANGUAGE_MAP[suffix]] += 1

        total_lines += count_lines(item)

    readme = find_readme(repo)

    readme_sections = extract_readme_sections(readme)

    return {
        "repo_name": repo.name,
        "readme": readme,
        "readme_sections": readme_sections,
        "files": total_files,
        "folders": total_folders,
        "lines": total_lines,
        "languages": dict(language_counts)
    }


def generate_report(data):

    report = []

    report.append("# Evidence Report")
    report.append("")
    report.append(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    report.append("")
    report.append(f"# {data['repo_name']}")
    report.append("")

    if data["readme"]:
        report.append(
            f"README Found: {data['readme'].name}"
        )
    else:
        report.append(
            "README Found: None"
        )

    report.append("")

    overview = data["readme_sections"]["overview"]
    technologies = data["readme_sections"]["technologies"]
    features = data["readme_sections"]["features"]

    if overview:

        report.append("## Project Purpose")
        report.append("")
        report.append(overview)
        report.append("")

    if technologies:

        report.append("## Technologies")
        report.append("")

        for tech in technologies:
            report.append(f"- {tech}")

        report.append("")

    if features:

        report.append("## Features")
        report.append("")

        for feature in features:
            report.append(f"- {feature}")

        report.append("")

    report.append("## Repository Statistics")
    report.append("")
    report.append(f"- Files: {data['files']}")
    report.append(f"- Folders: {data['folders']}")
    report.append(f"- Lines: {data['lines']}")
    report.append("")

    report.append("## Languages")

    for language, count in sorted(
        data["languages"].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        report.append(f"- {language}: {count}")

    report.append("")

    report.append("## Evidence Summary")
    report.append("")
    report.append(
        "Repository analysed successfully by Elucidator."
    )

    return "\n".join(report)


class ElucidatorGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("Elucidator")

        self.root.geometry("1000x750")

        self.repo_path = ""

        tk.Label(
            root,
            text="Repository Path"
        ).pack(pady=5)

        self.path_var = tk.StringVar()

        tk.Entry(
            root,
            textvariable=self.path_var,
            width=120
        ).pack(pady=5)

        tk.Button(
            root,
            text="Browse Repository",
            command=self.select_repository
        ).pack(pady=5)

        tk.Button(
            root,
            text="Analyse Repository",
            command=self.analyse
        ).pack(pady=5)

        self.output = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD
        )

        self.output.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

    def select_repository(self):

        path = filedialog.askdirectory()

        if path:
            self.repo_path = path
            self.path_var.set(path)

    def analyse(self):

        if not self.repo_path:

            messagebox.showwarning(
                "No Repository",
                "Select a repository first."
            )

            return

        try:

            data = analyse_repository(
                self.repo_path
            )

            report = generate_report(
                data
            )

            evidence_file = (
                Path(self.repo_path)
                / "EVIDENCE.md"
            )

            evidence_file.write_text(
                report,
                encoding="utf-8"
            )

            self.output.delete(
                "1.0",
                tk.END
            )

            self.output.insert(
                tk.END,
                report
            )

            messagebox.showinfo(
                "Success",
                f"EVIDENCE.md saved to\n\n{evidence_file}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )


def main():

    root = tk.Tk()

    ElucidatorGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()