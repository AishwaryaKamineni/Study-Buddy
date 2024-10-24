import os
import random
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, colorchooser
import sounddevice as sd
import wavio
from PIL import Image, ImageTk, ImageDraw
import threading
import json

class StudyBuddy:
    #initializations
    def __init__(self):
        self.results = {
            "Visual Learner": 0,
            "Auditory Learner": 0,
            "Reading/Writing Learner": 0,
            "Kinesthetic Learner": 0
        }
        self.top_styles = []
        self.the_flashcards = []
        self.currently_showing_definition = False
        self.current_flashcard_index = 0
        self.app_folder = os.path.dirname(os.path.abspath(__file__))
        self.is_recording = False
        self.recording_thread = None
        self.current_color = 'black'
        self.brush_size = 5
        self.recording_duration = 20
        os.makedirs(self.app_folder, exist_ok=True)
        self.main = tk.Tk()
        self.main.title("StudyBuddy")
        self.main.geometry("600x600")
        self.main.configure(bg='#e3f2fd')
        self.shapes = []
        self.current_shape = None
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.create_shape_buttons()
        self.shape_color = 'black'
        self.delete_mode = False
        self.the_notes = {}
        self.run()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#---------------------------------------------------------------------Quiz Code----------------------------------------------------------------------

    def quiz(self):
        self.questions = [
            {
                "question": "1. When you're trying to remember something, what's most helpful?",
                "options": ["Pictures or videos", "Listening to music or discussions", "Reading texts or notes", "Trying it out myself"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "2. In class, how do you take notes?",
                "options": ["Draw diagrams", "Listen and summarize", "Write everything down", "Participate in discussions"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "3. How do you like to study?",
                "options": ["Watch videos", "Discuss with friends", "Read textbooks", "Practice with exercises"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "4. What helps you understand new concepts best?",
                "options": ["Seeing a demonstration", "Listening to explanations", "Reading descriptions", "Hands-on experience"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "5. In group projects, you usually:",
                "options": ["Create visual aids", "Lead discussions", "Write reports", "Handle tasks physically"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "6. When learning a new skill, you like to:",
                "options": ["Watch a tutorial", "Listen to someone explain", "Read the manual", "Try it yourself"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "7. During a presentation, what do you pay most attention to?",
                "options": ["Slides and images", "The speaker's voice", "The written handouts", "The practical demonstration"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "8. To memorize a list, you like:",
                "options": ["Visualizing it", "Reciting it out loud", "Writing it down", "Practicing with it"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "9. In a classroom, you prefer:",
                "options": ["Visual aids and charts", "Listening to lectures", "Taking detailed notes", "Participating in activities"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
            {
                "question": "10. After learning something new, you like to:",
                "options": ["Create a visual summary", "Discuss what you've learned", "Write a summary", "Demonstrate the skill"],
                "answers": ["Visual Learner", "Auditory Learner", "Reading/Writing Learner", "Kinesthetic Learner"]
            },
        ]


        self.results = {
            "Visual Learner": 0,
            "Auditory Learner": 0,
            "Reading/Writing Learner": 0,
            "Kinesthetic Learner": 0,
        }


        self.current_question = 0
        self.load_question()


    def load_question(self):
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            question_window = tk.Toplevel(self.main)
            question_window.title(f"Quiz Question ({self.current_question + 1}/{len(self.questions)})")
            question_window.configure(bg='#e3f2fd')
            question_window.geometry("500x300")


            tk.Label(question_window, text=q['question'], font=('Helvetica', 12), bg='#e3f2fd').pack(pady=10)


            options_with_answers = list(zip(q["options"], q["answers"]))
            random.shuffle(options_with_answers)


            lettered_options = {chr(65 + i): option for i, (option, _) in enumerate(options_with_answers)}
            answer_mapping = {chr(65 + i): ans for i, (_, ans) in enumerate(options_with_answers)}


            button_style = {
                'bg': '#64b5f6',
                'fg': 'white',
                'font': ('Helvetica', 12),
                'padx': 8,
                'pady': 4,
                'activebackground': '#42a5f5'
            }


            def on_button_click(ans, window):
                self.process_answer(ans)
                window.destroy()
                self.current_question += 1
                self.load_question()


            for letter in "ABCD":
                option_text = lettered_options.get(letter, "")
                if option_text:
                    tk.Button(question_window, text=f"{letter}) {option_text}",
                              command=lambda ans=answer_mapping[letter]: on_button_click(ans, question_window), **button_style).pack(pady=5)


            question_window.transient(self.main)
            question_window.grab_set()
            question_window.protocol("WM_DELETE_WINDOW", question_window.destroy)
        else:
            self.show_results()


    def process_answer(self, answer):
            self.results[answer] += 1


    def show_results(self):
        result_window = tk.Toplevel(self.main)
        result_window.title("Quiz Results")
        result_window.configure(bg='#e3f2fd')
        tk.Label(result_window, text="Your Learning Style Results:", font=('Helvetica', 16), bg='#e3f2fd').pack(pady=10)


        for style, score in self.results.items():
            tk.Label(result_window, text=f"{style}: {score}", font=('Helvetica', 12), bg='#e3f2fd').pack()

        self.show_recommendations(result_window)


        tk.Button(result_window, text="Close", command=result_window.destroy, bg='#64b5f6', fg='white', font=('Helvetica', 12), padx=8, pady=4).pack(pady=10)


    def show_results(self):
        result_window = tk.Toplevel(self.main)
        result_window.title("Quiz Results")
        result_window.configure(bg='#e3f2fd')
        tk.Label(result_window, text="Your Learning Style Results:", font=('Helvetica', 16), bg='#e3f2fd').pack(pady=10)


        for style, score in self.results.items():
            tk.Label(result_window, text=f"{style}: {score}", font=('Helvetica', 12), bg='#e3f2fd').pack()


        self.show_recommendations(result_window)


        tk.Button(result_window, text="Close", command=result_window.destroy, bg='#64b5f6', fg='white', font=('Helvetica', 12), padx=8, pady=4).pack(pady=10)


    def show_recommendations(self, result_window):
        sorted_styles = sorted(self.results.items(), key=lambda item: item[1], reverse=True)
        top_styles = sorted_styles[:2]

        recommendations = {
            "Visual Learner": "Flashcards, Drawing Board",
            "Auditory Learner": "Audio Notes",
            "Reading/Writing Learner": "Flashcards, Notes",
            "Kinesthetic Learner": "Modeling, Drawing Board",
        }

        tk.Label(result_window, text="Recommended Tools:", font=('Helvetica', 14), bg='#e3f2fd').pack(pady=10)

        for style, score in top_styles:
            rec_text = recommendations.get(style, "No recommendations available.")
            tk.Label(result_window, text=f"{style}: {rec_text}", font=('Helvetica', 12), bg='#e3f2fd').pack()


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------Flashcards Code----------------------------------------------------------------

    def flashcards(self):
        self.flashcard_window = tk.Toplevel(self.main)
        self.flashcard_window.title("Flashcard Menu")
        self.flashcard_window.geometry("300x400")
        self.flashcard_window.configure(bg='#e3f2fd')

        tk.Button(self.flashcard_window, text="Create Flashcard", command=self.flashcard_creator, bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.flashcard_window, text="Review Flashcards", command=self.flashcard_review, bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.flashcard_window, text="Edit Flashcard", command=self.edit_flashcard, bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.flashcard_window, text="Delete Flashcard", command=self.delete_flashcard, bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.flashcard_window, text="Export Flashcards", command=self.export_flashcards, bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.flashcard_window, text="Import Flashcards", command=self.import_flashcards, bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.flashcard_window, text="Close", command=self.flashcard_window.destroy, bg='#e57373', fg='white').pack(pady=10)

    def flashcard_creator(self):
        while True:
            choice = simpledialog.askstring("Flashcard Creator", "Would you like to enter a 'word' or 'image'? (type 'word' or 'image')")


            if choice == 'word':
                term = simpledialog.askstring("Flashcard Creator", "Enter the term for this flashcard:")
                definition = simpledialog.askstring("Flashcard Creator", "Enter the definition for this flashcard:")
                if term and definition:
                    self.the_flashcards.append({"image": None, "definition": definition, "term": term})
                    messagebox.showinfo("Flashcard Created", f"Flashcard created with term: {term} and definition: {definition}")
                else:
                    messagebox.showwarning("Missing Input", "Both term and definition must be provided.")


            elif choice == 'image':
                image_path = filedialog.askopenfilename(title="Select an Image File", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
                if image_path:
                    definition = simpledialog.askstring("Flashcard Creator", "Enter the definition for this flashcard:")
                    if definition:
                        self.the_flashcards.append({"image": image_path, "definition": definition})
                        messagebox.showinfo("Flashcard Created", f"Flashcard created with image and definition: {definition}")
                    else:
                        messagebox.showwarning("No Definition Entered", "Please enter a definition for the flashcard.")
                else:
                    messagebox.showwarning("No Image Selected", "Please select an image file.")


            else:
                messagebox.showwarning("Invalid Choice", "Please type 'word' or 'image'.")


            continue_choice = simpledialog.askstring("Continue?", "Do you want to create another flashcard? (yes/no)")
            if not continue_choice or not continue_choice.lower().startswith('y'):
                break


        print("Your flashcards:", self.the_flashcards)


    def flashcard_review(self):
        if not self.the_flashcards:
            messagebox.showinfo("Flashcards", "No flashcards available.")
            return
        self.show_flashcard_review()

    def show_flashcard_review(self):
        self.review_window = tk.Toplevel(self.flashcard_window)
        self.review_window.title("Flashcard Review")
        self.review_window.geometry("400x500")
        self.review_window.configure(bg='#e3f2fd')

        content_frame = tk.Frame(self.review_window, bg='#e3f2fd')
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.flashcard_label = tk.Label(content_frame, text="", bg='#e3f2fd', font=("Arial", 14), wraplength=350)
        self.flashcard_label.pack(pady=10)

        self.flashcard_term = tk.Label(content_frame, text="", bg='#e3f2fd', font=("Arial", 14), wraplength=350)
        self.flashcard_term.pack(pady=10)

        self.img_label = tk.Label(content_frame, bg='#e3f2fd')
        self.img_label.pack(pady=10)

        nav_frame = tk.Frame(self.review_window, bg='#e3f2fd')
        nav_frame.pack(pady=10)

        self.prev_button = tk.Button(nav_frame, text="Previous", command=self.show_previous_flashcard, bg='#64b5f6', fg='white')
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(nav_frame, text="Next", command=self.show_next_flashcard, bg='#64b5f6', fg='white')
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.close_button = tk.Button(nav_frame, text="Close", command=self.close_flashcard_review, bg='#e57373', fg='white')
        self.close_button.pack(side=tk.LEFT, padx=10)

        self.toggle_button = tk.Button(content_frame, text="Show Definition", command=self.toggle_flashcard, bg="#64b5f6", fg="white")
        self.toggle_button.pack()

        self.display_flashcard()

    def display_flashcard(self):
        card = self.the_flashcards[self.current_flashcard_index]
        
        if 'image' in card and card['image']:
            self.flashcard_label.config(image="")
            image = Image.open(card['image'])
            image.thumbnail((350, 350))
            self.img = ImageTk.PhotoImage(image)
            self.img_label.config(image=self.img)
            self.img_label.image = self.img
            self.flashcard_label.config(text="")
        elif 'term' in card:
            self.flashcard_label.config(text=card['term'])
            self.img_label.config(image='')
        else:
            self.flashcard_label.config(text="No term or definition available.")
            self.img_label.config(image='')

    def toggle_flashcard(self):
        card = self.the_flashcards[self.current_flashcard_index]
        
        if 'term' in card and card['image':""]:
            if self.currently_showing_definition:
                self.flashcard_label.config(text=card['term'])
                self.img_label.config(image='')
            else:
                self.flashcard_label.config(text=card['definition'])
                self.img_label.config(image='')
                self.toggle_button.config(text="Show Term")
            
            self.currently_showing_definition = not self.currently_showing_definition
        
        elif 'image' in card and card['image']:
            if self.currently_showing_definition:
                self.flashcard_label.config(text=card['definition'])
                self.img_label.config(image='')
                self.toggle_button.config(text="Show Image")
            else:
                self.flashcard_label.config(text="")
                image = Image.open(card['image'])
                image.thumbnail((350, 350))
                self.img = ImageTk.PhotoImage(image)
                self.img_label.config(image=self.img)
                self.img_label.image = self.img
                self.toggle_button.config(text="Show Definition")


            self.currently_showing_definition = not self.currently_showing_definition


    def show_previous_flashcard(self):
        if self.current_flashcard_index > 0:
            self.current_flashcard_index -= 1
            self.display_flashcard()

    def show_next_flashcard(self):
        if self.current_flashcard_index < len(self.the_flashcards) - 1:
            self.current_flashcard_index += 1
            self.display_flashcard()

    def close_flashcard_review(self):
        self.review_window.destroy()

    def edit_flashcard(self):
        if not self.flashcards:
            messagebox.showinfo("Flashcards", "No flashcards available.")
            return
        index = simpledialog.askinteger("Edit Flashcard", "Enter the index of the flashcard to edit (0 to {}):".format(len(self.the_flashcards) - 1))
        if index is not None and 0 <= index < len(self.the_flashcards):
            card = self.the_flashcards[index]
            new_definition = simpledialog.askstring("Edit Flashcard", "Enter the new definition:", initialvalue=card['definition'])
            if new_definition:
                self.the_flashcards[index]['definition'] = new_definition
                messagebox.showinfo("Flashcard Updated", f"Flashcard updated: {new_definition}")
        else:
            messagebox.showwarning("Invalid Input", "Invalid index.")

    def delete_flashcard(self):
        if not self.the_flashcards:
            messagebox.showinfo("Flashcards", "No flashcards available.")
            return
        index = simpledialog.askinteger("Delete Flashcard", "Enter the index of the flashcard to delete (0 to {}):".format(len(self.the_flashcards) - 1))
        if index is not None and 0 <= index < len(self.the_flashcards):
            deleted_card = self.the_flashcards.pop(index)
            messagebox.showinfo("Flashcard Deleted", f"Flashcard deleted: {deleted_card['definition']}")
        else:
            messagebox.showwarning("Invalid Input", "Invalid index.")

    def export_flashcards(self):
        if not self.the_flashcards:
            messagebox.showinfo("Flashcards", "No flashcards available to export.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "w") as f:
                json.dump(self.the_flashcards, f)
            messagebox.showinfo("Export Successful", f"Flashcards exported to {filename}.")

    def import_flashcards(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "r") as f:
                self.the_flashcards = json.load(f)
            self.the_flashcards = [
                card for card in self.the_flashcards
                if card['definition'] not in ["Hi", "also hi"]
            ]
            messagebox.showinfo("Import Successful", f"Flashcards imported from {filename}.")

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#------------------------------------------------------------------------Drawing Board Code-------------------------------------------------------

    def drawing_board(self):
        self.drawing_window = tk.Toplevel(self.main)
        self.drawing_window.title("Drawing Board")
        self.drawing_window.configure(bg='#e3f2fd')
        self.canvas = tk.Canvas(self.drawing_window, bg='white', width=400, height=400)
        self.canvas.pack()

        color_frame = tk.Frame(self.drawing_window, bg='#e3f2fd')
        color_frame.pack(pady=10)
        tk.Label(color_frame, text="Select Color:", bg='#e3f2fd').pack(side=tk.LEFT)
        tk.Button(color_frame, bg='red', command=lambda: self.set_color('red')).pack(side=tk.LEFT)
        tk.Button(color_frame, bg='green', command=lambda: self.set_color('green')).pack(side=tk.LEFT)
        tk.Button(color_frame, bg='blue', command=lambda: self.set_color('blue')).pack(side=tk.LEFT)
        tk.Button(color_frame, bg='black', command=lambda: self.set_color('black')).pack(side=tk.LEFT)

        size_frame = tk.Frame(self.drawing_window, bg='#e3f2fd')
        size_frame.pack(pady=10)
        tk.Label(size_frame, text="Brush Size:", bg='#e3f2fd').pack(side=tk.LEFT)
        self.brush_size_entry = tk.Entry(size_frame, width=5)
        self.brush_size_entry.pack(side=tk.LEFT)
        self.brush_size_entry.insert(0, "5")
        tk.Button(size_frame, text="Set Size", command=self.set_brush_size).pack(side=tk.LEFT)

        tk.Button(self.drawing_window, text="Save Drawing", command=self.save_drawing, bg='#42a5f5', fg='white').pack(pady=5)
        tk.Button(self.drawing_window, text="Clear Canvas", command=self.clear_canvas, bg='#e57373', fg='white').pack(pady=5)

        self.canvas.bind("<B1-Motion>", self.paint)

    def change_background_color(self):
        color = simpledialog.askstring("Background Color", "Enter a color name (e.g., 'white', 'red'):")
        if color:
            self.canvas.configure(bg=color)
            messagebox.showinfo("Background Color Changed", f"Background color changed to {color}")

    def set_color(self, color):
        self.current_color = color
        messagebox.showinfo("Color Selected", f"Brush color set to {color}")

    def set_brush_size(self):
        try:
            size = int(self.brush_size_entry.get())
            if size > 0:
                self.brush_size = size
                messagebox.showinfo("Brush Size Set", f"Brush size set to {size}")
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Size", "Please enter a positive integer.")

    def paint(self, event):
        x, y = event.x, event.y
        self.canvas.create_oval(x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size, fill=self.current_color, outline=self.current_color)

    def save_drawing(self):
        image = Image.new('RGB', (400, 400), color='white')
        draw = ImageDraw.Draw(image)

        for item in self.canvas.find_all():
            coords = self.canvas.coords(item)
            if self.canvas.type(item) == "rectangle":
                fill_color = self.canvas.itemcget(item, "fill")
                outline_color = self.canvas.itemcget(item, "outline")
                draw.rectangle(coords, fill=fill_color, outline=outline_color)
            elif self.canvas.type(item) == "oval":
                fill_color = self.canvas.itemcget(item, "fill")
                outline_color = self.canvas.itemcget(item, "outline")
                draw.ellipse(coords, fill=fill_color, outline=outline_color)

        png_file_path = os.path.join(self.app_folder, 'drawing.png')
        image.save(png_file_path, 'PNG')

        print("Drawing saved as drawing.png.")

    def clear_canvas(self):
        self.canvas.delete("all")
        messagebox.showinfo("Canvas Cleared", "Canvas has been cleared.")


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#------------------------------------------------------------Audio Notes Code---------------------------------------------------------------------

    def audio_notes(self):
        print("Starting recorder...")
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()

        while True:
            command = simpledialog.askstring("Recorder", "Type 'stop' to stop recording:")
            if command and command.lower() == 'stop':
                self.stop_recording()
                break

    def record_audio(self):
        fs = 44100
        recording = sd.rec(int(self.recording_duration * fs), samplerate=fs, channels=2)
        sd.wait()
        wavio.write("output.wav", recording, fs, sampwidth=3)
        self.the_notes.append("output.wav")
        messagebox.showinfo("Recording Saved", "Recording saved as output.wav.")

    def play_recording(self):
        try:
            os.system("start output.wav")
            messagebox.showinfo("Playback", "Playing recording...")
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))

    def stop_recording(self):
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#----------------------------------------------------------------Modeling Tool Code---------------------------------------------------------------

    def create_shape_buttons(self):
        button_frame = tk.Frame(self.main, bg='#e3f2fd')
        button_frame.pack(pady=10)

    def modeling_tool(self):
        self.drawing_window = tk.Toplevel(self.main)
        self.drawing_window.title("Modeling Tool")
        self.drawing_window.configure(bg='#e3f2fd')


        self.canvas = tk.Canvas(self.drawing_window, bg='white', width=400, height=400, highlightthickness=2, highlightbackground="#64b5f6")
        self.canvas.pack(pady=10)


        shape_frame = tk.Frame(self.drawing_window, bg='#e3f2fd')
        shape_frame.pack(pady=10)


        button_style = {'bg': '#64b5f6', 'fg': 'white', 'relief': 'raised', 'padx': 10, 'pady': 5}
        tk.Button(shape_frame, text="Square", command=lambda: self.create_shape("square"), **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Circle", command=lambda: self.create_shape("circle"), **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Triangle", command=lambda: self.create_shape("triangle"), **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Rectangle", command=lambda: self.create_shape("rectangle"), **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Change Color", command=self.change_color, **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Delete Shape", command=self.toggle_delete_mode, **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Clear Canvas", command=self.clear_canvas, **button_style).pack(side=tk.LEFT)
        tk.Button(shape_frame, text="Save as Image", command=self.save_as_image, **button_style).pack(side=tk.LEFT)


        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)


        self.instructions_label = tk.Label(self.drawing_window, text="Click on buttons to create shapes, and click and drag them to create your model!", bg='#e3f2fd', font=("Arial", 12))
        self.instructions_label.pack(pady=5)


    def create_shape(self, shape_type):
        x, y = random.randint(50, 350), random.randint(50, 350)
        size = 50


        if shape_type == "square":
            coords = (x, y, x + size, y + size)
            shape_id = self.canvas.create_rectangle(coords, fill=self.current_color, outline='black')
        elif shape_type == "circle":
            coords = (x, y, x + size, y + size)
            shape_id = self.canvas.create_oval(coords, fill=self.current_color, outline='black')
        elif shape_type == "triangle":
            coords = (x, y + size, x + size / 2, y, x + size, y + size)
            shape_id = self.canvas.create_polygon(coords, fill=self.current_color, outline='black')
        elif shape_type == "rectangle":
            coords = (x, y, x + size * 1.5, y + size)
            shape_id = self.canvas.create_rectangle(coords, fill=self.current_color, outline='black')


        self.shapes.append((shape_id, shape_type, coords, self.current_color))


    def change_color(self):
        color = colorchooser.askcolor(title="Choose Shape Color")
        if color[1]:
            self.current_color = color[1]


    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            messagebox.showinfo("Delete Mode", "Click on a shape to delete it. Click again to exit delete mode.")


    def on_click(self, event):
        if self.delete_mode:
            shape = self.canvas.find_closest(event.x, event.y)
            if shape:
                self.canvas.delete(shape)
                self.shapes = [s for s in self.shapes if s[0] != shape]
        else:
            self.current_shape = self.canvas.find_closest(event.x, event.y)
            if self.current_shape:
                self.dragging = True
                self.offset_x = event.x - self.canvas.coords(self.current_shape)[0]
                self.offset_y = event.y - self.canvas.coords(self.current_shape)[1]


    def on_drag(self, event):
        if self.dragging and self.current_shape:
            self.canvas.move(self.current_shape, event.x - self.offset_x - self.canvas.coords(self.current_shape)[0],
                            event.y - self.offset_y - self.canvas.coords(self.current_shape)[1])


    def on_release(self, event):
        self.dragging = False


    def clear_canvas(self):
        self.canvas.delete("all")
        self.shapes.clear()


    def save_as_image(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        image = Image.new("RGB", (canvas_width, canvas_height), "white")
        draw = ImageDraw.Draw(image)

        for shape in self.shapes:
            shape_id, shape_type, _, color = shape
            
            coords = self.canvas.coords(shape_id)


            if shape_type == "rectangle":
                draw.rectangle(coords, fill=color, outline='black')
            elif shape_type == "circle":
                draw.ellipse(coords, fill=color, outline='black')
            elif shape_type == "triangle":
                draw.polygon(coords, fill=color, outline='black')


        app_folder = os.path.dirname(__file__)
        file_path = os.path.join(app_folder, 'model.png')


        image.save(file_path)
        print(f"Image saved as {file_path}")

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------Notes Code---------------------------------------------------------------------

    def prompt_add_note(self):
        while True:
            note = simpledialog.askstring("Add Note", "Enter your note:")
            if note:
                self.add_note(note)
                self.display_notes()
                break
            else:
                if messagebox.askyesno("Empty Note", "You entered an empty note. Would you like to try again?"):
                    continue
                break


    def prompt_edit_note(self):
        while True:
            note_id = simpledialog.askinteger("Edit Note", "Enter note ID to edit:")
            if note_id:
                new_note = simpledialog.askstring("Edit Note", "Enter new note text:")
                if new_note:
                    self.edit_note(note_id, new_note)
                    self.display_notes()
                    break
                else:
                    if messagebox.askyesno("Empty Note", "You entered an empty note. Would you like to try again?"):
                        continue
                    break
            else:
                if messagebox.askyesno("Invalid ID", "No ID entered. Would you like to try again?"):
                    continue
                break


    def display_notes(self):
        if not self.the_notes:
            messagebox.showinfo("Notes", "No notes available.")
            return
        notes_str = "\n".join(f"{id}: {note}" for id, note in self.the_notes.items())
        messagebox.showinfo("Notes", notes_str)

    def prompt_delete_note(self):
        if not self.notes:
            messagebox.showinfo("Notes", "No notes available.")
            return
        notes_str = "\n".join(f"{id}: {note}" for id, note in self.the_notes_items())
        messagebox.showinfo("Notes", notes_str)


    def add_note(self):
        note = simpledialog.askstring("Add Note", "Enter your note:")
        if note:
            note_id = len(self.the_notes) + 1
            self.the_notes[note_id] = note
            messagebox.showinfo("Success", f"Note added with ID: {note_id}")
            self.display_notes()
        else:
            messagebox.showwarning("Error", "No note entered.")


    def edit_note(self):
        note_id = simpledialog.askinteger("Edit Note", "Enter note ID:")
        if note_id is not None and note_id in self.the_notes:
            new_note = simpledialog.askstring("Edit Note","Enter new note text:")
            if new_note:
                self.the_notes[note_id] = new_note
                messagebox.showinfo("Success", f"Note {note_id} updated.")
                self.display_notes()
            else:
                messagebox.showwarning("Warning", "No new note entered.")
        else:
            messagebox.showerror("Error", "Note ID not found.")


    def delete_note(self):
        note_id = simpledialog.askinteger("Delete Note", "Enter note ID to delete:")
        if note_id is not None and note_id in self.the_notes:
            del self.the_notes[note_id]
            messagebox.showinfo("Success", f"Note {note_id} deleted.")
            self.display_notes()
        else:
            messagebox.showerror("Error", "Note ID not found.")

    def notes(self):
        self.notes_window = tk.Toplevel(self.main)
        self.notes_window.title("Notes Menu")
        self.notes_window.geometry("300x300")
        self.notes_window.configure(bg='#e3f2fd')


        tk.Button(self.notes_window, text="Add Note", command=lambda: self.add_note(), bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.notes_window, text="Edit Note", command=lambda: self.edit_note(), bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.notes_window, text="Delete Note", command=lambda: self.delete_note(), bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.notes_window, text="View Notes", command=lambda: self.display_notes(), bg='#64b5f6', fg='white').pack(pady=10)
        tk.Button(self.notes_window, text="Close", command=self.notes_window.destroy, bg='#e57373', fg='white').pack(pady=10)

    #runner
    def run(self):
        menu_frame = tk.Frame(self.main, bg='#e3f2fd')
        menu_frame.pack(pady=20, fill=tk.BOTH, expand=True)


        button_style = {
            'bg': '#64b5f6',
            'fg': 'white',
            'font': ('Helvetica', 14),
            'padx': 10,
            'pady': 5,
            'activebackground': '#42a5f5'
        }

        tk.Label(menu_frame, text="Welcome to Study Buddy!", bg='#e3f2fd', font=('Helvetica', 20, 'bold')).pack(pady=10)

        tk.Button(menu_frame, text="Take the Quiz", command=self.quiz, **button_style).pack(pady=20)

        tools_frame = tk.Frame(menu_frame, bg='#e3f2fd')
        tools_frame.pack(pady=10)

        image = Image.open("student_img_no_bg2.png")
        image = image.resize((300, 225), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        image_label = tk.Label(tools_frame, image=photo, bg='#e3f2fd')
        image_label.image = photo
        image_label.pack(side=tk.LEFT, padx=20)

        buttons_frame = tk.Frame(tools_frame, bg='#e3f2fd')
        buttons_frame.pack(side=tk.LEFT)

        button_rows = [
            "Flashcards",
            "Drawing Board",
            "Audio Notes",
            "Modeling Tool",
            "Notes"
        ]

        for text in button_rows:
            command = getattr(self, text.lower().replace(" ", "_"))
            tk.Button(buttons_frame, text=text, command=command, **button_style).pack(pady=5)

        tk.Button(menu_frame, text="Exit", command=self.main.quit, bg='#e57373', fg='white', font=('Helvetica', 14), padx=10, pady=5).pack(pady=10)

        self.main.mainloop()

if __name__ == "__main__":
    app = StudyBuddy()