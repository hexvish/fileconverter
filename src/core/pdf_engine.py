import subprocess
import os

class PdfEngine:
    @staticmethod
    def compress(input_path: str, output_path: str, preset: dict, process_holder: list = None) -> bool:
        """
        Compresses PDF using Ghostscript.
        process_holder: Optional list acting as a mutable pointer to store the Popen object.
        """
        # preset examples: { "action": "compress", "quality": "screen" }
        quality = preset.get("quality", "ebook") # defaults to ebook (medium)
        
        # dPDFSETTINGS=/screen (72 dpi), /ebook (150 dpi), /printer (300 dpi), /prepress (color preserving)
        
        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]
        
        try:
            # Check if output directory exists, create if not
            out_dir = os.path.dirname(output_path)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir)

            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)

            if process_holder is not None:
                process_holder[0] = process

            _, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"Ghostscript Error: {stderr}")
                return False
                
            return True

        except Exception as e:
            print(f"Exception during PDF compression: {e}")
            return False

    @staticmethod
    def convert(input_path: str, output_path: str, preset: dict) -> bool:
         # Placeholder if we need specific PDF-to-something logic
         # For now, Image->PDF is handled by ImageEngine
         pass
