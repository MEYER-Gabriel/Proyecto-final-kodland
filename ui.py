import discord
import db  # Importamos nuestro módulo de base de datos


class QuizView(discord.ui.View):
    def __init__(self, respuesta_correcta: str, explicacion: str):
        super().__init__(timeout=60)
        self.respuesta_correcta = respuesta_correcta.upper().strip()
        self.explicacion = explicacion

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary, custom_id="A")
    async def boton_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_respuesta(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary, custom_id="B")
    async def boton_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_respuesta(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary, custom_id="C")
    async def boton_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_respuesta(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary, custom_id="D")
    async def boton_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_respuesta(interaction, "D")

    async def procesar_respuesta(self, interaction: discord.Interaction, eleccion: str):
        # Deshabilitar botones para que no vuelvan a presionar
        for child in self.children:
            child.disabled = True

        await interaction.message.edit(view=self)

        if eleccion == self.respuesta_correcta:
            # 1. Sumamos puntos con db.py
            resultado = db.sumar_puntos_usuario(interaction.user.id, puntos_ganados=100)

            puntos_totales = resultado["puntos_totales"]
            subio_nivel = resultado["subio_de_nivel"]
            rango_nuevo = resultado["rango_nuevo"]

            resultado_msg = (
                f"🎉 **¡CORRECTO, {interaction.user.mention}!** Elegiste la **{eleccion}** (+100 pts).\n"
                f"📊 **Puntos totales:** {puntos_totales}\n\n"
                f"💡 **Explicación:** {self.explicacion}"
            )

            # 2. Asignar rol si subió de nivel
            if subio_nivel:
                resultado_msg += f"\n\n🎊 **¡SUBISTE DE NIVEL!** Ahora eres {rango_nuevo['emoji']} **{rango_nuevo['nombre']}**"
                if interaction.guild:
                    rol = discord.utils.get(interaction.guild.roles, name=rango_nuevo['nombre'])
                    if rol:
                        try:
                            await interaction.user.add_roles(rol)
                        except discord.Forbidden:
                            resultado_msg += " *(no tengo permisos para darte el rol)*"

        else:
            resultado_msg = (
                f"❌ **¡Incorrecto, {interaction.user.mention}!** Elegiste la **{eleccion}**, "
                f"pero la correcta era la **{self.respuesta_correcta}**.\n\n"
                f"💡 **Explicación:** {self.explicacion}"
            )

        # Enviar el nuevo mensaje en el chat
        await interaction.response.send_message(resultado_msg)