"""
Extremstellen bestimmen - f(x) = x^3 - 3x + 1
Handy-Format (9:16), Manim Community Edition + manim-voiceover

Installation:
    pip install manim
    pip install "manim-voiceover[gtts]"      # kostenlos, braucht Internet

Rendern:
    manim -qh extremstellen_voiceover.py Extremstellen
    manim -ql extremstellen_voiceover.py Extremstellen    # schnelle Vorschau

Sprachdienst wechseln: siehe Block "SPRACHDIENST" in construct().
Hinweis: Der erzeugte Ton wird in media/voiceovers/ gecacht. Ändert sich ein
Text, wird nur dieser Abschnitt neu erzeugt.
"""
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
# Alternativen (jeweils passendes Extra installieren):
# from manim_voiceover.services.azure import AzureService            # [azure]
# from manim_voiceover.services.elevenlabs import ElevenLabsService  # [elevenlabs]
# from manim_voiceover.services.coqui import CoquiService            # [coqui], offline

# ---------- Hochformat 1080 x 1920 ----------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0

# ---------- Farben (minimalistisch) ----------
BG = "#0F1115"
FG = "#F2F2F2"
GRAPH = "#E8E8E8"
ACCENT = "#FFD166"
HIGH = "#FF6B6B"
LOW = "#4DABF7"
GOOD = "#6BCB77"


def f(x):
    return x**3 - 3 * x + 1


def fit(mob, max_width=8.2):
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


class Extremstellen(VoiceoverScene):
    def construct(self):
        self.camera.background_color = BG

        # ================= SPRACHDIENST =================
        self.set_speech_service(GTTSService(lang="de", tld="de"))
        # Azure (natürlichere Stimme):
        # self.set_speech_service(AzureService(voice="de-DE-ConradNeural", style="friendly"))
        # ElevenLabs:
        # self.set_speech_service(ElevenLabsService(voice_name="...", model="eleven_multilingual_v2"))
        # Coqui (offline):
        # self.set_speech_service(CoquiService(model_name="tts_models/de/thorsten/tacotron2-DDC"))
        # ================================================

        # =====================================================
        # INTRO
        # =====================================================
        hook = Text("Wo geht's hoch,\nwo geht's runter?", font_size=56, color=FG, line_spacing=1.1)
        hook.move_to(UP * 3.2)
        fx_intro = MathTex(r"f(x)=x^3-3x+1", font_size=72, color=ACCENT)
        fx_intro.move_to(UP * 0.2)
        sub = Text("Hoch- und Tiefpunkt in 4 Schritten", font_size=34, color=GREY_B)
        sub.move_to(DOWN * 2.2)

        with self.voiceover(
            text="Wo geht's bergauf, und wo bergab? Schauen wir uns die Funktion "
                 "f von x gleich x hoch drei minus drei x plus eins an. "
                 "Hoch- und Tiefpunkt findest du in nur vier Schritten."
        ):
            self.play(FadeIn(hook, shift=UP * 0.3), run_time=1)
            self.play(Write(fx_intro), run_time=1.5)
            self.play(FadeIn(sub, shift=UP * 0.2))
        self.play(FadeOut(hook), FadeOut(sub), FadeOut(fx_intro))

        # =====================================================
        # GRAPH
        # =====================================================
        title = MathTex(r"f(x)=x^3-3x+1", font_size=52, color=FG).move_to(UP * 7.1)

        axes = Axes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2, 4, 1],
            x_length=8,
            y_length=5.4,
            axis_config={"color": GREY_B, "stroke_width": 3, "include_tip": False,
                         "font_size": 24},
            x_axis_config={"include_numbers": True},
            y_axis_config={"include_numbers": True},
        ).move_to(UP * 3.6)

        graph = axes.plot(f, x_range=[-2.1, 2.1], color=GRAPH, stroke_width=6)

        with self.voiceover(
            text="Das ist der Graph. Man sieht schon: Es gibt einen Hügel und ein Tal. "
                 "Aber wo genau liegen sie?"
        ):
            self.play(FadeIn(title, shift=DOWN * 0.2), Create(axes), run_time=1.2)
            self.play(Create(graph), run_time=2)

        # =====================================================
        # SCHRITT 1: Notwendige Bedingung
        # =====================================================
        label1 = Text("1   Notwendige Bedingung", font_size=40, color=ACCENT)
        label1.move_to(DOWN * 0.1)
        idea = Text("Im Extrempunkt ist die Tangente waagerecht.", font_size=30, color=GREY_B)
        idea.next_to(label1, DOWN, buff=0.4)

        t = ValueTracker(-2.0)
        dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), f(t.get_value())),
                                         color=ACCENT, radius=0.12))

        def tangent():
            x0 = t.get_value()
            y0 = f(x0)
            m = 3 * x0**2 - 3
            d = 0.7
            return Line(axes.c2p(x0 - d, y0 - m * d),
                        axes.c2p(x0 + d, y0 + m * d),
                        color=ACCENT, stroke_width=5)

        tan_line = always_redraw(tangent)

        slope_text = MathTex(r"f'(x)=", font_size=48, color=FG)
        slope_num = DecimalNumber(9, num_decimal_places=1, font_size=48, color=ACCENT)
        slope_num.add_updater(lambda m: m.set_value(3 * t.get_value()**2 - 3))
        readout = VGroup(slope_text, slope_num).arrange(RIGHT, buff=0.2)
        readout.move_to(DOWN * 2.6)

        with self.voiceover(
            text="Schritt eins: die notwendige Bedingung. "
                 "In einem Extrempunkt verläuft die Tangente waagerecht. "
                 "Ihre Steigung ist dort null."
        ):
            self.play(FadeIn(label1, shift=UP * 0.2))
            self.play(FadeIn(idea))
            self.play(FadeIn(dot), FadeIn(tan_line), FadeIn(readout))

        with self.voiceover(
            text="Beobachte die Steigung, während die Tangente über den Graphen wandert. "
                 "Bei minus eins ist sie null. Und bei eins wieder."
        ):
            self.play(t.animate.set_value(-1), run_time=2.5, rate_func=smooth)
            self.wait(0.8)
            self.play(t.animate.set_value(1), run_time=3, rate_func=smooth)
            self.wait(0.5)
            self.play(t.animate.set_value(2), run_time=1.5)

        slope_num.clear_updaters()
        self.play(FadeOut(readout), FadeOut(idea))
        self.remove(dot, tan_line)

        s1_1 = MathTex(r"f'(x)=3x^2-3", font_size=52)
        s1_2 = MathTex(r"3x^2-3=0", font_size=52)
        s1_3 = MathTex(r"x^2=1", font_size=52)
        s1_4 = MathTex(r"x=-1\quad\text{oder}\quad x=1", font_size=52, color=ACCENT)
        step1 = VGroup(s1_1, s1_2, s1_3, s1_4).arrange(DOWN, buff=0.45)
        step1.next_to(label1, DOWN, buff=0.6)

        with self.voiceover(
            text="Also leiten wir ab: f Strich von x gleich drei x Quadrat minus drei. "
                 "Das setzen wir null. Wir teilen durch drei, und es bleibt: "
                 "x Quadrat gleich eins. Also x gleich minus eins oder x gleich eins."
        ):
            self.play(Write(s1_1), run_time=1.5)
            self.play(Write(s1_2), run_time=1.2)
            self.play(Write(s1_3), run_time=1.2)
            self.play(Write(s1_4), run_time=1.5)

        cand_lines = VGroup(*[
            DashedLine(axes.c2p(x, -2), axes.c2p(x, 4), color=ACCENT,
                       stroke_width=3, dash_length=0.12)
            for x in (-1, 1)
        ])
        cand_hint = Text("Das sind nur die Kandidaten!", font_size=34, color=GREY_B)
        cand_hint.next_to(step1, DOWN, buff=0.5)

        with self.voiceover(
            text="Aber Vorsicht: Das sind erst die Kandidaten. "
                 "Ob dort wirklich ein Hoch- oder Tiefpunkt liegt, prüfen wir im nächsten Schritt."
        ):
            self.play(Create(cand_lines), FadeIn(cand_hint))

        self.play(FadeOut(label1), FadeOut(step1), FadeOut(cand_hint))

        # =====================================================
        # SCHRITT 2: Hinreichende Bedingung
        # =====================================================
        label2 = Text("2   Hinreichende Bedingung", font_size=40, color=ACCENT)
        label2.move_to(DOWN * 0.1)
        idea2 = Text("Die 2. Ableitung verrät: Hoch oder Tief?", font_size=30, color=GREY_B)
        idea2.next_to(label2, DOWN, buff=0.4)

        s2_1 = MathTex(r"f''(x)=6x", font_size=52)
        s2_2 = MathTex(r"f''(-1)=-6<0", r"\;\Rightarrow\;", r"\text{Hochpunkt}", font_size=48)
        s2_2[2].set_color(HIGH)
        s2_3 = MathTex(r"f''(1)=6>0", r"\;\Rightarrow\;", r"\text{Tiefpunkt}", font_size=48)
        s2_3[2].set_color(LOW)
        step2 = VGroup(s2_1, s2_2, s2_3).arrange(DOWN, buff=0.6)
        for m in step2:
            fit(m)
        step2.next_to(idea2, DOWN, buff=0.7)

        mem = Text("Negativ = Rechtskurve = Hochpunkt\nPositiv = Linkskurve = Tiefpunkt",
                   font_size=30, color=GREY_B, line_spacing=1.2)
        mem.next_to(step2, DOWN, buff=0.7)

        with self.voiceover(
            text="Schritt zwei: die hinreichende Bedingung. "
                 "Die zweite Ableitung verrät uns, ob wir einen Hoch- oder einen Tiefpunkt haben. "
                 "Sie lautet: f zwei Strich von x gleich sechs x."
        ):
            self.play(FadeIn(label2, shift=UP * 0.2), FadeIn(idea2))
            self.play(Write(s2_1), run_time=1.5)

        with self.voiceover(
            text="Bei minus eins kommt minus sechs heraus. Das ist kleiner als null, "
                 "die Kurve ist also eine Rechtskurve. Das bedeutet: Hochpunkt."
        ):
            self.play(Write(s2_2), run_time=2)

        with self.voiceover(
            text="Bei eins kommt sechs heraus. Das ist größer als null, "
                 "also eine Linkskurve. Das bedeutet: Tiefpunkt."
        ):
            self.play(Write(s2_3), run_time=2)

        with self.voiceover(
            text="Merk dir: Negativ ist Hochpunkt, positiv ist Tiefpunkt."
        ):
            self.play(FadeIn(mem))

        self.play(FadeOut(label2), FadeOut(idea2), FadeOut(step2), FadeOut(mem))

        # =====================================================
        # SCHRITT 3: y-Werte
        # =====================================================
        label3 = Text("3   Zugehörige y-Werte", font_size=40, color=ACCENT)
        label3.move_to(DOWN * 0.1)

        s3_1 = MathTex(r"f(-1)=(-1)^3-3\cdot(-1)+1", font_size=44)
        s3_1b = MathTex(r"=-1+3+1=", r"3", font_size=50)
        s3_1b[1].set_color(HIGH)
        s3_2 = MathTex(r"f(1)=1^3-3\cdot 1+1", font_size=44)
        s3_2b = MathTex(r"=1-3+1=", r"-1", font_size=50)
        s3_2b[1].set_color(LOW)

        block_a = VGroup(s3_1, s3_1b).arrange(DOWN, buff=0.25)
        block_b = VGroup(s3_2, s3_2b).arrange(DOWN, buff=0.25)
        step3 = VGroup(block_a, block_b).arrange(DOWN, buff=0.9)
        fit(step3)
        step3.next_to(label3, DOWN, buff=0.7)

        dot_h = Dot(axes.c2p(-1, 3), color=HIGH, radius=0.14)
        dot_t = Dot(axes.c2p(1, -1), color=LOW, radius=0.14)

        with self.voiceover(
            text="Schritt drei: Wir brauchen noch die y-Werte. "
                 "Dazu setzen wir minus eins in die Funktion ein. "
                 "Minus eins plus drei plus eins ergibt drei."
        ):
            self.play(FadeIn(label3, shift=UP * 0.2))
            self.play(Write(s3_1), run_time=1.5)
            self.play(Write(s3_1b), run_time=1.2)
            self.play(GrowFromCenter(dot_h))
            self.play(Indicate(dot_h, color=HIGH, scale_factor=1.8))

        with self.voiceover(
            text="Und für x gleich eins: eins minus drei plus eins ergibt minus eins."
        ):
            self.play(Write(s3_2), run_time=1.5)
            self.play(Write(s3_2b), run_time=1.2)
            self.play(GrowFromCenter(dot_t))
            self.play(Indicate(dot_t, color=LOW, scale_factor=1.8))

        self.play(FadeOut(label3), FadeOut(step3), FadeOut(cand_lines))

        # =====================================================
        # SCHRITT 4: Ergebnis
        # =====================================================
        label4 = Text("4   Ergebnis", font_size=40, color=ACCENT)
        label4.move_to(DOWN * 0.1)

        res_h = MathTex(r"H(-1\mid 3)", font_size=72, color=HIGH)
        res_t = MathTex(r"T(1\mid -1)", font_size=72, color=LOW)
        results = VGroup(res_h, res_t).arrange(DOWN, buff=0.7)
        results.next_to(label4, DOWN, buff=0.9)

        tag_h = MathTex(r"H", font_size=40, color=HIGH).next_to(dot_h, UR, buff=0.15)
        tag_t = MathTex(r"T", font_size=40, color=LOW).next_to(dot_t, DOWN, buff=0.2)
        box = SurroundingRectangle(results, color=GOOD, buff=0.4, corner_radius=0.2, stroke_width=4)

        with self.voiceover(
            text="Schritt vier: das Ergebnis. Der Hochpunkt liegt bei minus eins, drei. "
                 "Und der Tiefpunkt bei eins, minus eins."
        ):
            self.play(FadeIn(label4, shift=UP * 0.2))
            self.play(Write(res_h), FadeIn(tag_h), run_time=1.3)
            self.play(Write(res_t), FadeIn(tag_t), run_time=1.3)
            self.play(Create(box))

        # =====================================================
        # OUTRO
        # =====================================================
        self.play(FadeOut(label4), FadeOut(results), FadeOut(box))

        recap_title = Text("Dein Rezept für jede Extremstelle", font_size=38, color=ACCENT)
        recap_title.move_to(DOWN * 0.1)
        steps = VGroup(
            Text("1.  f'(x) = 0 lösen", font_size=40, color=FG),
            Text("2.  f''(x) prüfen", font_size=40, color=FG),
            Text("3.  y-Wert berechnen", font_size=40, color=FG),
            Text("4.  Punkt angeben", font_size=40, color=FG),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        steps.next_to(recap_title, DOWN, buff=0.7)
        closing = Text("Du kannst das!", font_size=60, color=GOOD)
        closing.next_to(steps, DOWN, buff=0.9)

        with self.voiceover(
            text="Das ist dein Rezept für jede Extremstelle: "
                 "Erste Ableitung gleich null setzen. "
                 "Mit der zweiten Ableitung prüfen. "
                 "Den y-Wert berechnen. "
                 "Und den Punkt angeben."
        ):
            self.play(FadeIn(recap_title, shift=UP * 0.2))
            for s in steps:
                self.play(FadeIn(s, shift=RIGHT * 0.3), run_time=0.7)

        with self.voiceover(text="Damit findest du jeden Hoch- und Tiefpunkt. Du kannst das!"):
            self.play(Write(closing), run_time=1.2)

        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.5)
