### INTERVIEW EXAMPLE APP ###
# For GitHub browsers...
# I made this app on Wed 19th March 2025, in order to show for my "Business skills" interview at Accenture.
# Just a heads up, they don't require you to make anything, this is just really a proof of concept.
# It is a simple Tkinter app that generates graphs / diagrams based off a prompt
# My Claude AI API key: 123XYZ
# I feel like I should disclose I used Claude 3.7 Sonnet to create part of this code. They encouraged this though.

### APP FLOW OUTLINE ###
# - ask the user for what diagram they would like to make
# - send a claude api request to generate mermaid diagram code of the diagram
# - use the mermaid cli to generate an image based off the mermaid code given back

### CODE ###

# Imports
import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import scrolledtext, messagebox

import anthropic
from PIL import Image, ImageTk


# Definitions, OOP, etc.
class MermaidDiagramGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Mermaid Diagram Generator")
        self.root.geometry("800x800")

        # Configure main window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Split the window into two frames
        self.main_frame = tk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        # Create the image preview area
        self.image_frame = tk.LabelFrame(self.main_frame, text="Diagram Preview")
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Dark background with transparency for the image display
        bg_color = "#222222"
        self.image_label = tk.Label(self.image_frame, text="No diagram generated yet",
                                   bg=bg_color, fg="white",  # Dark background, white text
                                   highlightthickness=0, bd=0)  # Remove border
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create the input area
        self.input_frame = tk.LabelFrame(self.main_frame, text="Diagram Description")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.columnconfigure(0, weight=1)

        self.prompt_label = tk.Label(self.input_frame, text="Describe the diagram you want to create:")
        self.prompt_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.input_text = scrolledtext.ScrolledText(self.input_frame, height=4)
        self.input_text.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.button_frame = tk.Frame(self.input_frame)
        self.button_frame.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        self.generate_button = tk.Button(self.button_frame, text="Generate Diagram", command=self.generate_diagram)
        self.generate_button.pack(side=tk.RIGHT, padx=5)

        # Claude API key
        #self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.api_key = "123XYZ"
        if not self.api_key:
            self.api_key = tk.simpledialog.askstring("API Key", "Enter your Anthropic API Key:", show="*")

        # Store the current mermaid code
        self.current_mermaid_code = ""

    def generate_diagram(self):
        prompt = self.input_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a description for the diagram you want to create.")
            return

        try:
            # Show waiting message
            self.image_label.config(text="Generating diagram, please wait...")
            self.root.update()

            # Generate mermaid code using Claude API
            mermaid_code = self.get_mermaid_from_claude(prompt)
            self.current_mermaid_code = mermaid_code

            # Generate image from mermaid code
            image_path = self.generate_mermaid_image(mermaid_code)

            # Display the image
            self.display_image(image_path)

            # Show success message
            messagebox.showinfo("Success", "Diagram generated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def get_mermaid_from_claude(self, prompt):
        # Initialize the Claude client
        client = anthropic.Anthropic(api_key=self.api_key)

        # Create a system prompt to guide Claude to generate Mermaid diagrams
        system_prompt = """
        You are an expert at creating Mermaid diagram code. The user will describe a diagram they want to create.
        Your task is to generate ONLY the Mermaid code that represents this diagram, with no additional explanation or text.
        Make sure the syntax is valid and the diagram will render correctly.
        Just respond with the mermaid code block, nothing else.
        """

        # Create the complete prompt for Claude
        complete_prompt = f"Based on this description, generate Mermaid diagram code: {prompt}"

        # Make the API call
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",  # Use appropriate model
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": complete_prompt}
                ]
            )

            # Extract mermaid code from response
            mermaid_code = response.content[0].text.strip()

            # Clean up code if it has markdown formatting
            if mermaid_code.startswith("```mermaid"):
                mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()

            return mermaid_code

        except Exception as e:
            raise Exception(f"Error calling Claude API: {str(e)}")

    def generate_mermaid_image(self, mermaid_code):
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(suffix='.mmd', delete=False, mode='w') as mmd_file:
            mmd_file.write(mermaid_code)
            mmd_file_path = mmd_file.name

        output_path = mmd_file_path.replace('.mmd', '.png')

        try:
            # Use mmdc (Mermaid CLI) to generate the image
            result = subprocess.run(
                ['mmdc', '-i', mmd_file_path, '-o', output_path],
                check=True,
                capture_output=True,
                text=True
            )

            # Clean up the temporary mermaid file
            try:
                os.unlink(mmd_file_path)
            except:
                pass

            return output_path

        except subprocess.CalledProcessError as e:
            raise Exception(f"Mermaid CLI error: {e.stderr}")
        except FileNotFoundError:
            raise Exception(
                "Mermaid CLI (mmdc) not found. Please install it using: npm install -g @mermaid-js/mermaid-cli")

    def display_image(self, image_path):
        try:
            # Load the image using PIL
            pil_image = Image.open(image_path)

            # Resize while maintaining aspect ratio
            max_width = self.image_frame.winfo_width() - 20
            max_height = self.image_frame.winfo_height() - 20

            width, height = pil_image.size
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

            # Convert PIL image to Tkinter PhotoImage
            tk_image = ImageTk.PhotoImage(pil_image)

            # Update the image label
            self.image_label.config(image=tk_image, text="")
            self.image_label.image = tk_image  # Keep a reference to avoid garbage collection

            # Clean up the temporary image file
            try:
                os.unlink(image_path)
            except:
                pass

        except Exception as e:
            raise Exception(f"Error displaying image: {str(e)}")

# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = MermaidDiagramGenerator(root)
    root.mainloop()
