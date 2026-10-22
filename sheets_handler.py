import requests
import json
import logging

logger = logging.getLogger(__name__)

class SheetsHandler:
    def __init__(self, script_url: str):
        self.script_url = script_url

    def send_transaction(self, data: dict) -> dict:
        """
        Kirim payload transaksi ke Google Apps Script Web App
        data: {tanggal, tipe, kategori, nominal, keterangan}
        """
        if not self.script_url or "script.google.com" not in self.script_url:
            return {"status": "error", "message": "GOOGLE_SCRIPT_URL belum disetel dengan benar"}

        payload = {
            "tanggal": data.get("tanggal"),
            "tipe": data.get("tipe"),
            "kategori": data.get("kategori"),
            "nominal": data.get("nominal"),
            "keterangan": data.get("keterangan")
        }

        try:
            # Apps Script Web App melakukan redirect 302, allow_redirects=True sangat penting
            response = requests.post(
                self.script_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                allow_redirects=True,
                timeout=15
            )
            return {"status": "success", "http_code": response.status_code, "text": response.text}
        except Exception as e:
            logger.error(f"Error mengirim ke Google Sheets: {e}")
            return {"status": "error", "message": str(e)}
