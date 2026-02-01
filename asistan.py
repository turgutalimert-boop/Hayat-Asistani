import discord, os, datetime, requests, pytz
from discord.ext import tasks, commands
import google.generativeai as genai

TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CITY = 'Nha Trang'
HEDEF_KANAL_ADI = 'genel'

KRITIK_TARIHLER = {
    "Vietnam Vizesi": "2026-05-15",
    "Kiz Arkadasimin Dogum Gunu": "2026-08-20",
    "Pasaport Yenileme": "2027-10-10"
}

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class HayatiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        self.sabah_raporu_dongusu.start()

    async def on_ready(self):
        print(f'Hayati aktif!')

bot = HayatiBot()

async def ai_rapor_olustur():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=tr"
        w = requests.get(url).json()
        hava = f"{w['main']['temp']}C, {w['weather'][0]['description']}"
        bugun = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).date()
        tarih_listesi = ""
        for b, t in KRITIK_TARIHLER.items():
            kalan = (datetime.datetime.strptime(t, "%Y-%m-%d").date() - bugun).days
            tarih_listesi += f"- {b}: {kalan} gun kaldi.\n"
        prompt = f"Sen Mert'in asistani Hayati'sin. Mert'e samimi bir sabah raporu yaz. Hava: {hava}. Takvim: {tarih_listesi}. Mert abi diye hitap et."
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Rapor hatasi abi: {e}"

@bot.tree.command(name="rapor", description="AI raporu al")
async def rapor(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await ai_rapor_olustur()
    await interaction.followup.send(msg)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if bot.user.mentioned_in(message) or "hayati" in message.content.lower():
        async with message.channel.typing():
            p = f"Sen Mert'in asistani Hayati'sin. Mert: '{message.content}'. Kisa ve samimi cevap ver."
            res = ai_model.generate_content(p)
            await message.reply(res.text)

@tasks.loop(minutes=1)
async def sabah_raporu_dongusu():
    simdi = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    if simdi.hour == 9 and simdi.minute == 0:
        kanal = discord.utils.get(bot.get_all_channels(), name=HEDEF_KANAL_ADI)
        if kanal:
            await kanal.send(await ai_rapor_olustur())

bot.run(TOKEN)
