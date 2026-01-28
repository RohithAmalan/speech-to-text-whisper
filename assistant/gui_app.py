import tkinter as tk
from tkinter import font
import threading
import time

class ChatBubble:
    def __init__(self, canvas, text, is_user=True, y_pos=0):
        self.canvas = canvas
        self.text = text
        self.is_user = is_user
        
        # Style
        self.bg_color = "#007AFF" if is_user else "#333333"
        self.text_color = "white"
        self.pad_x = 15
        self.pad_y = 10
        self.font = font.Font(family="Helvetica", size=13)
        self.max_width = 250
        
        # Calculate Dimensions
        self.text_id = canvas.create_text(
            0, 0, text=text, font=self.font, width=self.max_width, anchor="nw"
        )
        bbox = canvas.bbox(self.text_id)
        width = bbox[2] - bbox[0] + (self.pad_x * 2)
        height = bbox[3] - bbox[1] + (self.pad_y * 2)
        canvas.delete(self.text_id) # Cleanup temp text
        
        # Position
        canvas_width = int(canvas.cget("width"))
        if is_user:
            x1 = canvas_width - width - 20
        else:
            x1 = 20
            
        y1 = y_pos + 10
        x2 = x1 + width
        y2 = y1 + height
        
        # Draw Bubble (Rounded Rectangle Sim)
        radius = 15
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius,
            x2, y2, x2-radius, y2,
            x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        self.bubble = canvas.create_polygon(points, smooth=True, fill=self.bg_color)
        
        # Draw Text
        text_x = x1 + self.pad_x
        text_y = y1 + self.pad_y
        self.text_obj = canvas.create_text(
            text_x, text_y, text=text, fill=self.text_color, font=self.font, anchor="nw", width=self.max_width
        )
        
        self.height = height + 10 # Total height used

class VoiceAssistantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Assistant")
        self.root.geometry("400x700")
        self.root.configure(bg="#1E1E1E")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#252526", height=60)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(header_frame, text="Assistant", font=("Helvetica", 18, "bold"), bg="#252526", fg="white")
        lbl_title.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Frame(self.root, bg="#333333", height=1).pack(fill="x") # Divider
        
        # Chat Canvas (Scrollable)
        self.chat_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.chat_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.chat_frame, bg="#1E1E1E", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.current_y = 10
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.config(width=380) # Initial width hint
        
        # Footer
        self.footer = tk.Frame(self.root, bg="#252526", height=120)
        self.footer.pack(fill="x", side="bottom")
        
        # Status
        self.status = tk.Label(self.footer, text="Tap to Speak", font=("Helvetica", 11), bg="#252526", fg="#AAAAAA")
        self.status.pack(pady=(10, 5))
        
        # Mic Button (Canvas for Circle)
        self.btn_canvas = tk.Canvas(self.footer, width=80, height=80, bg="#252526", highlightthickness=0)
        self.btn_canvas.pack()
        
        # Draw Circle Button
        self.btn_circle = self.btn_canvas.create_oval(5, 5, 75, 75, fill="#007AFF", outline="")
        self.btn_icon = self.btn_canvas.create_text(40, 40, text="🎙️", font=("Arial", 30))
        
        # Click bindings
        self.btn_canvas.tag_bind(self.btn_circle, "<Button-1>", self.toggle_recording)
        self.btn_canvas.tag_bind(self.btn_icon, "<Button-1>", self.toggle_recording)
        
        self.is_recording = False
        self.add_message("Hello! I am your AI assistant.", is_user=False)
        self.add_message("How can I help you today?", is_user=False)

    def add_message(self, text, is_user=True):
        bubble = ChatBubble(self.canvas, text, is_user, self.current_y)
        self.current_y += bubble.height
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)
        
    def toggle_recording(self, event=None):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.btn_canvas.itemconfig(self.btn_circle, fill="#FF3B30") # Red
        self.status.config(text="Listening...", fg="#FF3B30")
        
        # Pulsing effect (simple)
        self.pulse_state = 0
        self._pulse()
        
        self.root.after(2000, self.simulate_response)

    def _pulse(self):
        if not self.is_recording: return
        colors = ["#FF3B30", "#FF6B60"]
        self.btn_canvas.itemconfig(self.btn_circle, fill=colors[self.pulse_state])
        self.pulse_state = 1 - self.pulse_state
        self.root.after(500, self._pulse)

    def stop_recording(self):
        self.is_recording = False
        self.btn_canvas.itemconfig(self.btn_circle, fill="#007AFF") # Blue
        self.status.config(text="Tap to Speak", fg="gray")

    def simulate_response(self):
        if self.is_recording:
            self.stop_recording()
            self.add_message("This feels like a native app now.", is_user=True)
            self.root.after(1000, lambda: self.add_message("Yes, this is much cleaner and smoother.", is_user=False))

    def run(self):
        # Force top
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.after_idle(self.root.attributes,'-topmost',False)
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Polished GUI...")
    app = VoiceAssistantGUI()
    app.run()
