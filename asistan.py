import discord, os, datetime, pytz
from discord.ext import commands
import google.generativeai as genai

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Senin verdigin listedeki en guncel model: Gemini 3 Flash
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-3-flash")

KRITIK_TARIHLER = {
    "Vietnam Vizesi": "2026-05-15",
    "Kiz Arkadasimin Dogum Gunu": "2026-08-20"
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Hayati 2026 model (Gemini 3 Flash) aktif!")
    await bot.tree.sync()

@bot.tree.command(name="hayati", description="Hayatiye bir sey sor")
async def hayati(interaction: discord.Interaction, soru: str):
    await interaction.response.defer()
    try:
        bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
        # Botun 1 Subat 2026 farkindaligini sagliyoruz
        context = f"Bugun {bugun}. Sen Mertin sadik asistani Hayatisin. Cevaplarini kisa, samimi ve Mert abi diyerek ver. Soru: {soru}"
        response = ai_model.generate_content(context)
        await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Hata: {e}")

@bot.tree.command(name="sayac", description="Kalan gunler")
async def sayac(interaction: discord.Interaction):
    bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).date()
    mesaj = "📅 **Mert Abi, 1 Şubat 2026 itibariyle durum:**
"
    for isim, tarih_str in KRITIK_TARIHLER.items():
        tarih = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()
        kalan = (tarih - bugun).days
        mesaj += f"- {isim}: {kalan} gun kaldi.
"
    await interaction.response.send_message(mesaj)

bot.run(TOKEN)