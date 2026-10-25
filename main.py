__version__ = "1.0.0"

import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView

APP_NAME = "StudyAI"
OWNER_NAME = "cg"

# Configure this only after deploying your own secure AI backend.
# Do NOT put a private AI-provider API key inside a mobile app.
AI_BACKEND_URL = ""


def styled_button(text, callback, height=48):
    b = Button(text=text, size_hint_y=None, height=dp(height))
    b.bind(on_release=callback)
    return b


class StudyAIApp(App):
    title = "StudyAI"

    def build(self):
        self.notes = ""
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(9))

        heading = Label(
            text="[b]StudyAI[/b]\nCreated by cg",
            markup=True, font_size="25sp", size_hint_y=None, height=dp(78)
        )
        root.add_widget(heading)

        self.status = Label(
            text="आपका AI Study Assistant\nनीचे से कोई फीचर चुनें।",
            size_hint_y=None, height=dp(54), halign="center", valign="middle"
        )
        self.status.bind(size=lambda *_: setattr(self.status, "text_size", self.status.size))
        root.add_widget(self.status)

        root.add_widget(styled_button("📷 फोटो से नोट्स / OCR", self.pick_image))
        root.add_widget(styled_button("🤖 AI से प्रश्न पूछें", self.ask_ai))
        root.add_widget(styled_button("📝 MCQ टेस्ट", self.start_quiz))
        root.add_widget(styled_button("📄 नोट्स को PDF में सेव करें", self.save_pdf))
        root.add_widget(styled_button("📚 अपने नोट्स देखें / लिखें", self.edit_notes))
        root.add_widget(styled_button("ℹ️ ऐप के बारे में", self.about))

        self.output = TextInput(
            text="यहाँ निकाले गए टेक्स्ट और उत्तर दिखाई देंगे।",
            readonly=True, multiline=True, size_hint_y=1
        )
        root.add_widget(self.output)
        return root

    def show_message(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        scroll = ScrollView()
        label = Label(text=message, size_hint_y=None, halign="left", valign="top")
        label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        label.bind(texture_size=lambda inst, size: setattr(inst, "height", size[1] + dp(10)))
        scroll.add_widget(label)
        content.add_widget(scroll)
        content.add_widget(styled_button("ठीक है", lambda *_: popup.dismiss()))
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.75))
        popup.open()

    def pick_image(self, *_):
        chooser = FileChooserListView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"],
            path=os.path.expanduser("~")
        )
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        layout.add_widget(chooser)
        popup = Popup(title="पढ़ाई की फोटो चुनें", content=layout, size_hint=(0.95, 0.9))
        def process(*args):
            if chooser.selection:
                selected = chooser.selection[0]
                popup.dismiss()
                self.ocr_image(selected)
        layout.add_widget(styled_button("फोटो चुनें", process))
        layout.add_widget(styled_button("रद्द करें", lambda *_: popup.dismiss()))
        popup.open()

    def ocr_image(self, path):
        # OCR works on desktop after installing Tesseract + pytesseract.
        # Android builds need a compatible bundled OCR engine/backend.
        try:
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(path), lang="eng")
            if not text.strip():
                text = "कोई टेक्स्ट नहीं मिला। साफ़ और सीधी फोटो आज़माएँ।"
            self.notes = text
            self.output.text = text
            self.status.text = "फोटो से टेक्स्ट निकालने की कोशिश पूरी हुई।"
        except ImportError:
            self.show_message(
                "OCR सेटअप चाहिए",
                "फोटो से टेक्स्ट निकालने के लिए इस कंप्यूटर पर Pillow, pytesseract और Tesseract OCR इंस्टॉल करें। "
                "Android APK में OCR इंजन अलग से जोड़ना होगा। अभी यह शुरुआती प्रोजेक्ट है।"
            )
        except Exception as exc:
            self.show_message("फोटो पढ़ने में समस्या", str(exc))

    def ask_ai(self, *_):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        question = TextInput(
            hint_text="अपना पढ़ाई से जुड़ा प्रश्न लिखें…",
            multiline=True, size_hint_y=0.45
        )
        answer = Label(
            text="AI उत्तर पाने के लिए सुरक्षित backend जोड़ना होगा।",
            size_hint_y=0.45, halign="left", valign="top"
        )
        answer.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(question)
        content.add_widget(answer)
        popup = Popup(title="AI प्रश्नोत्तर", content=content, size_hint=(0.92, 0.72))
        def submit(*args):
            if not question.text.strip():
                answer.text = "पहले अपना प्रश्न लिखें।"
            elif not AI_BACKEND_URL:
                answer.text = (
                    "प्रश्न तैयार है:\n" + question.text.strip() +
                    "\n\nAI सेवा अभी कनेक्ट नहीं है। असली AI उत्तर के लिए एक सुरक्षित server/backend "
                    "और provider API configuration चाहिए। API key सीधे APK में न रखें।"
                )
                self.output.text = answer.text
            else:
                answer.text = "Backend endpoint configured है, लेकिन उसके API format के अनुसार integration code जोड़ना बाकी है।"
        content.add_widget(styled_button("उत्तर प्राप्त करें", submit))
        content.add_widget(styled_button("बंद करें", lambda *_: popup.dismiss()))
        popup.open()

    def start_quiz(self, *_):
        questions = [
            ("पौधों में भोजन बनाने की प्रक्रिया क्या कहलाती है?",
             ["प्रकाश संश्लेषण", "वाष्पीकरण", "संघनन"], 0),
            ("पानी का रासायनिक सूत्र क्या है?",
             ["CO2", "H2O", "O2"], 1),
            ("सौरमंडल का तारा कौन है?",
             ["चंद्रमा", "पृथ्वी", "सूर्य"], 2),
        ]
        state = {"index": 0, "score": 0}
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        prompt = Label(text="", size_hint_y=None, height=dp(90), halign="left", valign="middle")
        prompt.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        box.add_widget(prompt)
        buttons = []
        for _ in range(3):
            btn = Button(text="", size_hint_y=None, height=dp(48))
            box.add_widget(btn)
            buttons.append(btn)
        footer = Label(text="", size_hint_y=None, height=dp(35))
        box.add_widget(footer)
        popup = Popup(title="MCQ टेस्ट", content=box, size_hint=(0.9, 0.75))

        def render():
            i = state["index"]
            if i >= len(questions):
                prompt.text = f"टेस्ट पूरा!\nस्कोर: {state['score']} / {len(questions)}"
                for b in buttons:
                    b.disabled = True
                    b.text = ""
                footer.text = "बंद करने के लिए नीचे बटन दबाएँ।"
                return
            q, opts, correct = questions[i]
            prompt.text = f"प्रश्न {i+1}/{len(questions)}\n{q}"
            footer.text = f"स्कोर: {state['score']}"
            for j, b in enumerate(buttons):
                b.disabled = False
                b.text = opts[j]
                b.background_color = (1, 1, 1, 1)
                def choose(instance, choice=j):
                    if choice == questions[state["index"]][2]:
                        state["score"] += 1
                        footer.text = "सही जवाब!"
                    else:
                        footer.text = "गलत जवाब। सही उत्तर: " + questions[state["index"]][1][questions[state["index"]][2]]
                    state["index"] += 1
                    render()
                b.unbind(on_release=None)
                b.bind(on_release=choose)
        box.add_widget(styled_button("बंद करें", lambda *_: popup.dismiss()))
        render()
        popup.open()

    def edit_notes(self, *_):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        editor = TextInput(text=self.notes, hint_text="यहाँ अपने नोट्स लिखें…", multiline=True)
        box.add_widget(editor)
        popup = Popup(title="मेरे नोट्स", content=box, size_hint=(0.92, 0.85))
        def save(*args):
            self.notes = editor.text
            self.output.text = self.notes or "अभी कोई नोट्स नहीं हैं।"
            self.status.text = "नोट्स इस सत्र में अपडेट हुए।"
            popup.dismiss()
        box.add_widget(styled_button("नोट्स सेव करें", save))
        box.add_widget(styled_button("बंद करें", lambda *_: popup.dismiss()))
        popup.open()

    def save_pdf(self, *_):
        text = self.notes or self.output.text
        if not text.strip():
            self.show_message("नोट्स खाली हैं", "पहले कुछ नोट्स लिखें या फोटो से टेक्स्ट निकालें।")
            return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            out_dir = App.get_running_app().user_data_dir
            os.makedirs(out_dir, exist_ok=True)
            filename = os.path.join(out_dir, "StudyAI_Notes.pdf")
            pdf = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            pdf.setTitle("StudyAI Notes")
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(48, height - 50, "StudyAI Notes")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(48, height - 68, f"Created by {OWNER_NAME} • {datetime.now().strftime('%Y-%m-%d')}")
            y = height - 100
            for line in text.splitlines():
                # Built-in Helvetica does not support Devanagari; use English or add a Unicode font.
                while len(line) > 95:
                    pdf.drawString(48, y, line[:95])
                    line = line[95:]
                    y -= 14
                    if y < 50:
                        pdf.showPage()
                        pdf.setFont("Helvetica", 10)
                        y = height - 50
                pdf.drawString(48, y, line)
                y -= 14
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = height - 50
            pdf.save()
            self.show_message("PDF सेव हो गया", f"PDF का स्थान:\n{filename}\n\nध्यान दें: हिंदी अक्षरों के लिए PDF में Unicode फ़ॉन्ट जोड़ना होगा।")
        except ImportError:
            self.show_message("PDF लाइब्रेरी चाहिए", "PDF बनाने के लिए reportlab इंस्टॉल करें।")
        except Exception as exc:
            self.show_message("PDF बनाने में समस्या", str(exc))

    def about(self, *_):
        self.show_message(
            "StudyAI के बारे में",
            "StudyAI\nCreated by cg\n\nफीचर्स: फोटो OCR (सेटअप आवश्यक), AI प्रश्नोत्तर (backend आवश्यक), "
            "MCQ अभ्यास, नोट्स और PDF export.\n\nयह शुरुआती प्रोजेक्ट है; AI और Android-native फोटो/OCR integration "
            "को प्रकाशित करने से पहले पूरा करना और टेस्ट करना होगा।"
        )


if __name__ == "__main__":
    StudyAIApp().run()
