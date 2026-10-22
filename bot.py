import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from parser import parse_transaction
from sheets_handler import SheetsHandler
from obsidian_handler import ObsidianHandler
from advisor import get_smart_feedback

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

# Inisialisasi Handlers
sheets_client = SheetsHandler(GOOGLE_SCRIPT_URL)
obsidian_client = ObsidianHandler(
    local_notes_dir="obsidian_vault",
    github_token=GITHUB_TOKEN,
    github_repo=GITHUB_REPO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Halo Guswi! Saya adalah **Smart Cashflow Assistant** kamu.\n\n"
        "Cukup kirimkan pesan pengeluaran atau pemasukan dengan bahasa natural, misalnya:\n"
        "• `Beli nasi padang 25rb`\n"
        "• `Isi bensin 35k`\n"
        "• `Dapat kiriman uang saku 500rb`\n"
        "• `Top up kuota 100000`\n\n"
        "Setiap transaksi akan langsung otomatis dicatat ke **Google Spreadsheet** dan **Obsidian Note** kamu! 🚀"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💡 **Panduan Penggunaan:**\n\n"
        "1. **Mencatat Transaksi:** Cukup ketik apa yang kamu beli/terima beserta nominalnya.\n"
        "2. **Format Angka:** Mendukung `k`, `rb`, `ribu`, `jt`, maupun angka penuh seperti `50.000`.\n"
        "3. **Kategori Otomatis:** Sistem mendeteksi otomatis kategori seperti Makanan, Transportasi, Kuliah, Hiburan, dll.\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    # 1. Parse Transaksi
    data = parse_transaction(text)

    # Validasi apakah ada nominal yang terdeteksi
    if data["nominal"] <= 0:
        await update.message.reply_text(
            "⚠️ Nominal tidak terdeteksi. Silakan sertakan nominalnya ya.\nContoh: `Makan siang 25rb` atau `Beli bensin 30k`."
        )
        return

    # 2. Catat ke Google Spreadsheet (Apps Script)
    res_sheet = sheets_client.send_transaction(data)
    sheet_status_text = "✅ Berhasil dicatat ke Google Sheets" if res_sheet.get("status") == "success" else f"⚠️ Gagal catat ke Sheets: {res_sheet.get('message')}"

    # 3. Catat ke Obsidian (Markdown)
    local_note_path = obsidian_client.append_to_daily_note(data)
    obsidian_status_text = f"✅ Dicatat ke Obsidian ({os.path.basename(local_note_path)})"

    # 4. Ambil Saran / Insight Finansial Cerdas
    feedback = get_smart_feedback(data)

    # 5. Format Balasan Chat
    formatted_nominal = f"Rp {data['nominal']:,}".replace(",", ".")
    tipe_emoji = "📉" if data["tipe"] == "Pengeluaran" else "📈"

    reply_msg = (
        f"{tipe_emoji} **Transaksi Tercatat!**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📅 **Tanggal:** `{data['tanggal']}`\n"
        f"🏷️ **Tipe:** `{data['tipe']}`\n"
        f"📂 **Kategori:** `{data['kategori']}`\n"
        f"💵 **Nominal:** `{formatted_nominal}`\n"
        f"📝 **Keterangan:** {data['keterangan']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{sheet_status_text}\n"
        f"{obsidian_status_text}\n\n"
        f"💡 *Catatan AI:* {feedback}"
    )

    await update.message.reply_text(reply_msg, parse_mode="Markdown")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN tidak ditemukan di environment variable!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot Cashflow berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
