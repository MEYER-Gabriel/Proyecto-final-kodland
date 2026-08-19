import discord
from discord.ext import commands
from api import gemini
import json
from ui import QuizView
import db

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print("Bot en linea ve a discord ")


@bot.command()
async def fact(ctx):
    fact_data = gemini(prompt="Dame un dato sobre el cambio climatico de forma breve (máximo 40 palabras)")
    await ctx.send(f"{fact_data}")


@bot.command()
async def desmiente(ctx, *, noticia: str):
    # Armamos un prompt inteligente que le dice a Gemini cómo comportarse
    prompt_con_instrucciones = f"""
    Eres un divulgador científico amigable y directo sobre cambio climático.
    Analiza la siguiente afirmación planteada por un usuario y desmiéntela si es un mito o greenwashing:

    Afirmación a analizar: "{noticia}"

    Por favor responde de forma breve (máximo 150 palabras) y con el siguiente formato:
    - **Veredicto**: (Escribe si es Falso, Engañoso o Mito en 1 sola frase corta).
    - **Explicación**: (Breve explicación científica pero fácil de entender).
    - **Dato clave / Fuente**: (Un dato relevante o mención a organismos como IPCC o NASA).
    """
    respuesta_gemini = gemini(prompt=prompt_con_instrucciones)
    await ctx.send(respuesta_gemini)


@bot.command()
async def quiz(ctx, dificultad: str = "medio"):
    dificultad = dificultad.lower()
    dificultades_validas = ["facil", "medio", "dificil"]

    if dificultad not in dificultades_validas:
        await ctx.send("⚠️ Dificultad no válida. Usa: `facil`, `medio` o `dificil`.")
        return

    msg_espera = await ctx.send("🎲 *Generando pregunta con Gemini...*")

    prompt_quiz = f"""
    Crea 1 pregunta de trivia sobre cambio climático con nivel de dificultad '{dificultad}'.

    Responde ÚNICAMENTE con un objeto JSON válido (sin bloques ```json ni texto adicional):
    {{
        "pregunta": "Texto de la pregunta aquí",
        "opciones": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
        "correcta": "A",
        "explicacion": "Explicación breve de 1 frase"
    }}
    """

    respuesta_raw = gemini(prompt=prompt_quiz)

    # 1. Imprimimos en consola para depurar si Gemini devuelve algo raro o vacío
    print("--- RESPUESTA RAW DE GEMINI ---")
    print(repr(respuesta_raw))
    print("-------------------------------")

    try:
        # 2. Verificamos que la respuesta no sea None o vacía
        if not respuesta_raw or not respuesta_raw.strip():
            raise ValueError("Gemini devolvió una respuesta vacía.")

        # 3. Limpiamos las etiquetas de bloques de código Markdown
        texto_limpio = respuesta_raw.strip()
        if texto_limpio.startswith("```json"):
            texto_limpio = texto_limpio[7:]
        if texto_limpio.startswith("```"):
            texto_limpio = texto_limpio[3:]
        if texto_limpio.endswith("```"):
            texto_limpio = texto_limpio[:-3]

        texto_limpio = texto_limpio.strip()

        # 4. Convertimos a JSON
        datos = json.loads(texto_limpio)

        mensaje_pregunta = f"🎲 **QUIZ CLIMÁTICO (Nivel: {dificultad.capitalize()})**\n\n"
        mensaje_pregunta += f"❓ **{datos['pregunta']}**\n\n"

        letras = ["A", "B", "C", "D"]
        for i, opcion in enumerate(datos["opciones"]):
            mensaje_pregunta += f"**{letras[i]})** {opcion}\n"

        vista_botones = QuizView(
            respuesta_correcta=datos["correcta"],
            explicacion=datos["explicacion"]
        )

        await msg_espera.delete()
        await ctx.send(content=mensaje_pregunta, view=vista_botones)

    except Exception as e:
        await msg_espera.edit(content=f"⚠️ Ocurrió un error al generar la pregunta. Inténtalo de nuevo. (`Error: {e}`)")


@bot.command()
async def rank(ctx, usuario: discord.Member = None):
    """Muestra el perfil, puntos y rango del usuario."""
    target = usuario or ctx.author
    str_id = str(target.id)

    perfiles = db.cargar_perfiles()

    if str_id not in perfiles:
        await ctx.send(f"🌱 {target.mention} aún no tiene puntos. ¡Responde un `!quiz` para comenzar!")
        return

    datos = perfiles[str_id]
    puntos = datos["puntos"]
    rango_info = db.obtener_rango_por_puntos(puntos)

    mensaje = f"📊 **PERFIL DE COMPROMISO CLIMÁTICO**\n\n"
    mensaje += f"👤 **Usuario:** {target.mention}\n"
    mensaje += f"🏆 **Rango:** {rango_info['emoji']} **{rango_info['nombre']}**\n"
    mensaje += f"⭐ **Puntos:** {puntos} pts\n"
    mensaje += f"🎯 **Quizzes acertados:** {datos['quizzes_correctos']}"

    await ctx.send(mensaje)


@bot.command()
async def leaderboard(ctx):
    """Muestra el Top 10 de usuarios con más puntos en el servidor."""
    ranking = db.obtener_leaderboard()

    if not ranking:
        await ctx.send("🌍 Aún no hay nadie en la tabla de clasificación. ¡Usa `!quiz` para sumar puntos!")
        return

    mensaje = "🏆 **TABLA DE CLASIFICACIÓN CLIMÁTICA** 🌍\n\n"
    medallas = ["🥇", "🥈", "🥉"]

    for i, (user_id, datos) in enumerate(ranking[:10]):  # Top 10
        puesto = medallas[i] if i < 3 else f"**#{i+1}**"
        rango_info = db.obtener_rango_por_puntos(datos["puntos"])

        # Intentamos obtener el nombre del usuario en el servidor
        member = ctx.guild.get_member(int(user_id)) if ctx.guild else None
        nombre = member.display_name if member else f"Usuario ({user_id[-4:]})"

        mensaje += f"{puesto} **{nombre}** — {datos['puntos']} pts {rango_info['emoji']}\n"

    await ctx.send(mensaje)

bot.remove_command('help')  # Elimina el help por defecto de Discord


@bot.command()
async def help(ctx):
    """Muestra la lista de comandos disponibles."""
    mensaje = "🤖 **COMANDOS DEL BOT CLIMÁTICO** 🌍\n\n"

    mensaje += "🌍 **Información & Concientización**\n"
    mensaje += "• `!fact` — Recibe un dato curioso y breve sobre el cambio climático.\n"
    mensaje += "• `!desmiente <texto>` — Analiza una afirmación o mito y te dice si es falso.\n\n"

    mensaje += "🎲 **Juegos & Gamificación**\n"
    mensaje += "• `!quiz <facil|medio|dificil>` — Responde preguntas de trivia y gana puntos.\n"
    mensaje += "• `!rank` (o `!rank @usuario`) — Consulta tu nivel, rango actual y puntos.\n"
    mensaje += "• `!leaderboard` — Muestra el Top 10 de usuarios con más puntos.\n\n"

    mensaje += "🛠️ **Pruebas**\n"
    mensaje += "• `!dar_xp` — Otorga 100 XP instantáneos a tu perfil para probar niveles.\n"

    await ctx.send(mensaje)


@bot.command()
async def dar_xp(ctx):
    """Otorga 100 XP al usuario para probar el sistema de niveles."""
    # Sumamos 100 puntos usando el módulo db
    resultado = db.sumar_puntos_usuario(ctx.author.id, puntos_ganados=100)

    puntos_totales = resultado["puntos_totales"]
    subio_nivel = resultado["subio_de_nivel"]
    rango_nuevo = resultado["rango_nuevo"]

    mensaje = f"⚡ **¡Se te han otorgado +100 XP de prueba, {ctx.author.mention}!**\n"
    mensaje += f"📊 **Puntos totales:** {puntos_totales} pts"

    # Verificamos si con este regalo subió de nivel y le damos el rol
    if subio_nivel:
        mensaje += f"\n\n🎊 **¡SUBISTE DE NIVEL!** Ahora eres {rango_nuevo['emoji']} **{rango_nuevo['nombre']}**"
        if ctx.guild:
            rol = discord.utils.get(ctx.guild.roles, name=rango_nuevo['nombre'])
            if rol:
                try:
                    await ctx.author.add_roles(rol)
                    mensaje += f" *(Rol '{rol.name}' asignado en el servidor)*"
                except discord.Forbidden:
                    mensaje += "\n⚠️ *(No tengo permisos para asignarte el rol automáticamente)*"

    await ctx.send(mensaje)


bot.run("")
