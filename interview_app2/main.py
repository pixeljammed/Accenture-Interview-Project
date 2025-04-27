import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import os
import threading
import tempfile


class MarkdownToPPTXConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown to PowerPoint Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.setup_ui()

    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Convert Markdown to PowerPoint", font=("Arial", 16))
        title_label.pack(pady=(0, 10))

        # Notebook for file/text input options
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tab 1: File Input
        file_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(file_tab, text="File Input")

        # Input file selection
        input_frame = ttk.Frame(file_tab)
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Input Markdown File:").pack(side=tk.LEFT)

        self.input_path_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path_var, width=40)
        input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_input_file)
        browse_button.pack(side=tk.RIGHT)

        load_button = ttk.Button(file_tab, text="Load File to Editor", command=self.load_file_to_editor)
        load_button.pack(anchor=tk.E, pady=5)

        # Tab 2: Direct Markdown Input
        editor_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(editor_tab, text="Markdown Editor")

        # Markdown editor
        editor_frame = ttk.Frame(editor_tab)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(editor_frame, text="Enter or edit Markdown content:").pack(anchor=tk.W, pady=(0, 5))

        # Scrolled text widget for markdown editing
        self.markdown_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, width=80, height=15,
                                                         font=("Courier New", 11))
        self.markdown_editor.pack(fill=tk.BOTH, expand=True)

        # Sample markdown button
        sample_button = ttk.Button(editor_frame, text="Insert Sample Markdown", command=self.insert_sample_markdown)
        sample_button.pack(anchor=tk.E, pady=5)

        # Common settings area (outside the notebook)
        # Output file selection
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="Output PowerPoint File:").pack(side=tk.LEFT)

        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        save_button = ttk.Button(output_frame, text="Browse", command=self.browse_output_file)
        save_button.pack(side=tk.RIGHT)

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        # Theme selection
        theme_frame = ttk.Frame(options_frame)
        theme_frame.pack(fill=tk.X, pady=5)

        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)

        self.theme_var = tk.StringVar(value="default")
        themes = ["default", "serif", "simple", "night", "moon"]
        theme_dropdown = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes)
        theme_dropdown.pack(side=tk.LEFT, padx=5)

        # Additional options
        self.incremental_var = tk.BooleanVar(value=False)
        incremental_check = ttk.Checkbutton(options_frame, text="Incremental bullets", variable=self.incremental_var)
        incremental_check.pack(anchor=tk.W, pady=2)

        self.slide_level_var = tk.IntVar(value=2)
        slide_level_frame = ttk.Frame(options_frame)
        slide_level_frame.pack(fill=tk.X, pady=2)
        ttk.Label(slide_level_frame, text="Slide Level:").pack(side=tk.LEFT)
        slide_level_spin = ttk.Spinbox(slide_level_frame, from_=1, to=3, width=5, textvariable=self.slide_level_var)
        slide_level_spin.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(pady=5)

        # Convert button
        convert_button = ttk.Button(main_frame, text="Convert to PowerPoint", command=self.start_conversion)
        convert_button.pack(pady=10)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.input_path_var.set(file_path)
            # Auto-suggest output path
            if not self.output_path_var.get():
                output_path = os.path.splitext(file_path)[0] + ".pptx"
                self.output_path_var.set(output_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save PowerPoint File",
            defaultextension=".pptx",
            filetypes=[("PowerPoint files", "*.pptx"), ("All files", "*.*")]
        )
        if file_path:
            self.output_path_var.set(file_path)

    def load_file_to_editor(self):
        file_path = self.input_path_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid input file first")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.markdown_editor.delete(1.0, tk.END)
                self.markdown_editor.insert(tk.END, content)

            # Switch to editor tab
            self.notebook.select(1)  # Index 1 is the editor tab
            self.status_var.set(f"Loaded file: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {str(e)}")

    def insert_sample_markdown(self):
        sample = """# Presentation Title

## First Slide

- Bullet point 1
- Bullet point 2
- Bullet point 3

## Second Slide

### Subsection

Content for subsection

## Third Slide

> Blockquote example

---

## Images and Links

![Image description](image_url)

[Link text](http://example.com)

## Table Example

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        self.markdown_editor.delete(1.0, tk.END)
        self.markdown_editor.insert(tk.END, sample)

    def start_conversion(self):
        # Get current tab
        current_tab = self.notebook.index(self.notebook.select())

        # Check if output path is specified
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file")
            return

        # Determine if we're using file input or editor content
        if current_tab == 0:  # File Input Tab
            input_path = self.input_path_var.get()
            if not input_path or not os.path.exists(input_path):
                messagebox.showerror("Error", "Please specify a valid input file")
                return
            use_temp_file = False
        else:  # Editor Tab
            # Get content from the editor
            markdown_content = self.markdown_editor.get(1.0, tk.END)
            if not markdown_content.strip():
                messagebox.showerror("Error", "Markdown content is empty")
                return

            # Create a temporary file for the markdown content
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.md', mode='w', encoding='utf-8')
            temp_file.write(markdown_content)
            temp_file.close()
            input_path = temp_file.name
            use_temp_file = True

        # Start conversion in a separate thread to keep UI responsive
        self.status_var.set("Converting...")
        self.progress_var.set(10)

        conversion_thread = threading.Thread(target=self.perform_conversion, args=(input_path, use_temp_file))
        conversion_thread.daemon = True
        conversion_thread.start()

    def perform_conversion(self, input_path, use_temp_file=False):
        try:
            output_path = self.output_path_var.get()
            theme = self.theme_var.get()
            slide_level = self.slide_level_var.get()
            incremental = self.incremental_var.get()

            # Build pandoc command
            cmd = [
                "pandoc",
                input_path,
                "-o", output_path,
                "-t", "pptx",
                "--slide-level", str(slide_level)
            ]

            # Add theme if not default
            if theme != "default":
                cmd.extend(["-V", f"theme={theme}"])

            # Add incremental option if selected
            if incremental:
                cmd.extend(["-i"])

            self.progress_var.set(30)

            # Execute pandoc command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.progress_var.set(50)
            stdout, stderr = process.communicate()

            self.progress_var.set(90)

            # Clean up temp file if used
            if use_temp_file and os.path.exists(input_path):
                try:
                    os.unlink(input_path)
                except:
                    pass

            # Check for errors
            if process.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Conversion Error", f"Error: {stderr}"))
                self.root.after(0, lambda: self.status_var.set("Conversion failed"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully converted to {output_path}"))
                self.root.after(0, lambda: self.status_var.set("Conversion completed"))

                # Ask if user wants to open the file
                if messagebox.askyesno("Open File", "Would you like to open the PowerPoint file?"):
                    self.open_file(output_path)

            self.progress_var.set(100)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))

            # Clean up temp file if used
            if use_temp_file and os.path.exists(input_path):
                try:
                    os.unlink(input_path)
                except:
                    pass

    def open_file(self, file_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS or Linux
                import sys
                subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', file_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownToPPTXConverter(root)
    root.mainloop()