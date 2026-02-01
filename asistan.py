import discord, os, datetime, pytz, asyncio
from discord.ext import commands
import google.generativeai as genai

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-lite")

KRITIK_TARIHLER = {
    "Vietnam Vizesi": "2026-05-15",
    "Kiz Arkadasimin Dogum Gunu": "2026-08-20"
}

intents = discord.Intents.default()
intents.message_content = True # Mesajları okuyabilmesi için şart
bot = commands.Bot(command_prefix="!", intents=intents)

# Bilge Hayati'nin karakter tanımı
PERSONALITY = (
    "Sen Mert abinin sadık asistanı Hayati'sin. "
    "Karakterin: Binlerce yıllık Türk-İslam geleneğinden süzülüp gelen bir bilge, bir alim. "
    "Üslubun: Vakur, nazik, hikmetli ve saygılı. Cümlelerinde 'Mert abi' hitabını eksik etme. "
    "Bilgi birikimin: Hem modern teknolojiye hem de kadim doğu ilimlerine hakimsin."
)

@bot.event
async def on_ready():
    print("Bilge Hayati (2.5 Flash Lite) 2026 seferine hazır!")
    await bot.tree.sync()

async def hayati_cevap_ver(soru, context_type="mesaj"):
    try:
        bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
        full_prompt = f"{PERSONALITY}\nBugünün tarihi: {bugun}.\nMert abi sana şunu sordu: {soru}"
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: ai_model.generate_content(full_prompt))
        return response.text
    except Exception as e:
        return f"Mert abi, lisanım yetmedi, bir hata hasıl oldu: {e}"

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Eğer botun adı geçerse veya birisi ona bir şey yazarsa otomatik cevap verir
    if "hayati" in message.content.lower() or bot.user.mentioned_in(message):
        async with message.channel.typing():
            cevap = await hayati_cevap_ver(message.content)
            await message.reply(cevap)

@bot.tree.command(name="hayati", description="Bilge Hayati'ye danış")
async def hayati_slash(interaction: discord.Interaction, soru: str):
    await interaction.response.defer(thinking=True)
    cevap = await hayati_cevap_ver(soru)
    await interaction.followup.send(cevap)

@bot.tree.command(name="sayac", description="Kalan günleri hesapla")
async def sayac(interaction: discord.Interaction):
    bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).date()
    mesaj = "📜 **Mert Abi, Takvim-i Şerif Durumu:**\n"
    for isim, tarih_str in KRITIK_TARIHLER.items():
        tarih = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()
        kalan = (tarih - bugun).days
        mesaj += f"- {isim}: {kalan} gün kalmıştır.\n"
    await interaction.response.send_message(mesaj)

bot.run(TOKEN)
