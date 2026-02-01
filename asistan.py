import discord, os, datetime, requests, pytz
from discord.ext import tasks, commands
from discord import app_commands
import google.generativeai as genai

# --- AYARLAR ---
TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CITY = 'Nha Trang'
HEDEF_KANAL_ADI = 'genel'

# --- ÖNEMLİ TARİHLER ---
KRITIK_TARIHLER = {
    "Vietnam Vizesi": "2026-05-15",
    "Kız Arkadaşımın Doğum Günü": "2026-08-20",
    "Pasaport Yenileme": "2027-10-10"
}

# AI Ayarı
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class HayatiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        self.gunluk_rapor_gorevi.start()

    async def on_ready(self):
        print(f'✅ Hayatî aktif!')

bot = HayatiBot()

async def ai_rapor_olustur():
    try:
        # Hava Durumu
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=tr"
        w = requests.get(url).json()
        hava = f"{w['main']['temp']}°C, {w['weather'][0]['description']}"

        # Tarihler
        bugun = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).date()
        tarih_listesi = ""
        for baslik, t_str in KRITIK_TARIHLER.items():
            kalan = (datetime.datetime.strptime(t_str, "%Y-%m-%d").date() - bugun).days
            tarih_listesi += f"- {baslik}: {kalan} gün kaldı.\n"

        prompt = f"Sen Mert'in asistanı Hayatî'sin. Mert'e samimi bir sabah raporu yaz. Hava: {hava}. Önemli tarihler: {tarih_listesi}. Mert abi diye hitap et, tavsiye ver."
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Rapor hazırlanamadı abi, ama ben buradayım! Hata: {e}"

@bot.tree.command(name="rapor", description="Hayati'den AI raporu al")
async def rapor(interaction: discord.Interaction):
    await interaction.response.defer()
    mesaj = await ai_rapor_olustur()
    await interaction.followup.send(mesaj)

@tasks.loop(minutes=1)
async def gunluk_rapor_gorevi():
    simdi = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    if simdi.hour == 9 and simdi.minute == 0:
        kanal = discord.utils.get(bot.get_all_channels(), name=HEDEF_KANAL_ADI)
        if kanal:
            await kanal.send(await ai_rapor_olustur())

bot.run(TOKEN)


