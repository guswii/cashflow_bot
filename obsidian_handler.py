import os
from datetime import datetime
import base64
import requests
import logging

logger = logging.getLogger(__name__)

class ObsidianHandler:
    def __init__(self, local_notes_dir: str = "notes", github_token: str = None, github_repo: str = None, github_branch: str = "main"):
        self.local_notes_dir = local_notes_dir
        self.github_token = github_token
        self.github_repo = github_repo
        self.github_branch = github_branch
        os.makedirs(self.local_notes_dir, exist_ok=True)

    def append_to_daily_note(self, data: dict) -> str:
        """
        Catat transaksi ke file Markdown format Obsidian.
        Juga mendukung sinkronisasi ke GitHub repo jika token diset.
        """
        now = datetime.now()
        date_filename = now.strftime("%Y-%m-%d") + ".md"
        local_filepath = os.path.join(self.local_notes_dir, date_filename)

        # Header awal jika file baru dibuat
        if not os.path.exists(local_filepath):
            with open(local_filepath, "w", encoding="utf-8") as f:
                f.write(f"# 📅 Catatan Keuangan - {now.strftime('%d %B %Y')}\n\n")
                f.write("## 📝 Daftar Transaksi\n")
                f.write("| Waktu | Tipe | Kategori | Nominal | Keterangan |\n")
                f.write("|---|---|---|---|---|\n")

        # Baris Markdown baru
        time_str = now.strftime("%H:%M")
        nominal_formatted = f"Rp {data['nominal']:,}".replace(",", ".")
        row = f"| {time_str} | {data['tipe']} | {data['kategori']} | {nominal_formatted} | {data['keterangan']} |\n"

        with open(local_filepath, "a", encoding="utf-8") as f:
            f.write(row)

        # Sinkronisasi ke GitHub jika tersedia kredensial
        if self.github_token and self.github_repo:
            self._sync_to_github(date_filename, local_filepath)

        return local_filepath

    def _sync_to_github(self, filename: str, filepath: str):
        """Kirim commit ke repo GitHub Obsidian"""
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{filename}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        # Ambil SHA file jika sudah ada
        sha = None
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sha = r.json().get("sha")

        payload = {
            "message": f"Update cashflow {filename}",
            "content": content_b64,
            "branch": self.github_branch
        }
        if sha:
            payload["sha"] = sha

        requests.put(url, headers=headers, json=payload)
