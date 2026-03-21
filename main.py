#!/usr/bin/env python3
"""
PDF to ePub Converter - Windows Application
Converts PDF files to ePub format while preserving formatting and hyperlinks
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from converter import PDFToEpubConverter


class PDFToEpubGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to ePub Converter v1.0")
        self.root.geometry("600x400")
        self.root.configure(bg='#f0f0f0')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('winnative')
        
        self.converter = PDFToEpubConverter()
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF to ePub Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="PDF File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_file_var = tk.StringVar()
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_file_var, width=50)
        self.input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        
        self.browse_btn = ttk.Button(main_frame, text="Browse...", 
                                   command=self.browse_input_file)
        self.browse_btn.grid(row=1, column=2, pady=5, padx=(5, 0))
        
        # Output file selection
        ttk.Label(main_frame, text="Output ePub:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar()
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_file_var, width=50)
        self.output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        
        self.browse_output_btn = ttk.Button(main_frame, text="Browse...", 
                                          command=self.browse_output_file)
        self.browse_output_btn.grid(row=2, column=2, pady=5, padx=(5, 0))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Conversion Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        options_frame.columnconfigure(0, weight=1)
        
        # Preserve hyperlinks checkbox
        self.preserve_links_var = tk.BooleanVar(value=True)
        self.preserve_links_cb = ttk.Checkbutton(options_frame, 
                                                text="Preserve hyperlinks and table of contents",
                                                variable=self.preserve_links_var)
        self.preserve_links_cb.grid(row=0, column=0, sticky=tk.W)
        
        # Preserve formatting checkbox
        self.preserve_format_var = tk.BooleanVar(value=True)
        self.preserve_format_cb = ttk.Checkbutton(options_frame, 
                                                 text="Preserve text formatting (bold, italic, etc.)",
                                                 variable=self.preserve_format_var)
        self.preserve_format_cb.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Include images checkbox
        self.include_images_var = tk.BooleanVar(value=True)
        self.include_images_cb = ttk.Checkbutton(options_frame, 
                                               text="Include images from PDF",
                                               variable=self.include_images_var)
        self.include_images_cb.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready to convert")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.convert_btn = ttk.Button(button_frame, text="Convert to ePub", 
                                    command=self.start_conversion, style='Accent.TButton')
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_fields)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.exit_btn = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        self.exit_btn.pack(side=tk.LEFT)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
            # Auto-suggest output filename
            if not self.output_file_var.get():
                output_path = Path(filename).with_suffix('.epub')
                self.output_file_var.set(str(output_path))
                
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save ePub file as",
            defaultextension=".epub",
            filetypes=[("ePub files", "*.epub"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
            
    def clear_fields(self):
        self.input_file_var.set("")
        self.output_file_var.set("")
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Ready to convert")
        self.progress.stop()
        
    def log_message(self, message):
        """Add message to log text area"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Update status label"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def start_conversion(self):
        input_file = self.input_file_var.get().strip()
        output_file = self.output_file_var.get().strip()
        
        # Validation
        if not input_file:
            messagebox.showerror("Error", "Please select a PDF file to convert")
            return
            
        if not output_file:
            messagebox.showerror("Error", "Please specify an output ePub filename")
            return
            
        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"Input file not found: {input_file}")
            return
            
        # Disable convert button during conversion
        self.convert_btn.configure(state='disabled')
        self.progress.start()
        self.log_text.delete(1.0, tk.END)
        
        # Start conversion in separate thread
        conversion_thread = threading.Thread(
            target=self.run_conversion,
            args=(input_file, output_file),
            daemon=True
        )
        conversion_thread.start()
        
    def run_conversion(self, input_file, output_file):
        """Run the actual conversion in background thread"""
        try:
            self.update_status("Starting conversion...")
            self.log_message(f"Converting: {os.path.basename(input_file)}")
            self.log_message(f"Output: {os.path.basename(output_file)}")
            self.log_message("")
            
            # Set conversion options
            options = {
                'preserve_hyperlinks': self.preserve_links_var.get(),
                'preserve_formatting': self.preserve_format_var.get(),
                'include_images': self.include_images_var.get()
            }
            
            # Run conversion
            success = self.converter.convert(
                input_file, 
                output_file, 
                options,
                progress_callback=self.update_status,
                log_callback=self.log_message
            )
            
            if success:
                self.update_status("Conversion completed successfully!")
                self.log_message("✓ Conversion completed successfully!")
                self.log_message(f"✓ ePub saved: {output_file}")
                
                # Ask if user wants to open the output file
                if messagebox.askyesno("Success", 
                                     f"Conversion completed!\n\nWould you like to open the output file location?"):
                    import subprocess
                    subprocess.run(['explorer', '/select,', output_file], shell=True)
            else:
                self.update_status("Conversion failed")
                self.log_message("✗ Conversion failed")
                messagebox.showerror("Error", "Conversion failed. Check the log for details.")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.log_message(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")
            
        finally:
            # Re-enable convert button and stop progress
            self.root.after(0, lambda: [
                self.convert_btn.configure(state='normal'),
                self.progress.stop()
            ])


def main():
    root = tk.Tk()
    app = PDFToEpubGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()