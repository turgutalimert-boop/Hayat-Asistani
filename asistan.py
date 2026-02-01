import discord, os, datetime, pytz, asyncio
from discord.ext import commands
import google.generativeai as genai

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 2.5 Flash Lite Ayarı
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-lite")

KRITIK_TARIHLER = {
    "Vietnam Vizesi": "2026-05-15",
    "Kiz Arkadasimin Dogum Gunu": "2026-08-20"
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Hayati 2026 (Gemini 2.5 Flash Lite) Gorev Basinda!")
    await bot.tree.sync()

@bot.tree.command(name="hayati", description="Hayatiye bir sey sor")
async def hayati(interaction: discord.Interaction, soru: str):
    await interaction.response.defer(thinking=True)
    try:
        bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
        context = f"Bugun {bugun}. Sen Mert abinin sadik asistani Hayatisin. Mert abi diyerek samimi cevap ver. Soru: {soru}"
        
        # Yanıtı asenkron alarak Discord bağlantısını canlı tutuyoruz
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: ai_model.generate_content(context))
        
        await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Hata kanka: {e}")

@bot.tree.command(name="sayac", description="Kalan gunler")
async def sayac(interaction: discord.Interaction):
    bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).date()
    mesaj = "📅 Mert Abi, 1 Subat 2026 Takvimi:\n"
    for isim, tarih_str in KRITIK_TARIHLER.items():
        tarih = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()
        kalan = (tarih - bugun).days
        mesaj += f"- {isim}: {kalan} gun kaldi.\n"
    await interaction.response.send_message(mesaj)

bot.run(TOKEN)
