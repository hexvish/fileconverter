import subprocess
import os

class ImageEngine:
    @staticmethod
    def convert(input_path: str, output_path: str, preset: dict, process_holder: list = None) -> bool:
        """
        Executes ImageMagick convert command.
        process_holder: Optional list acting as a mutable pointer to store the Popen object.
        """
        cmd = ["convert", input_path]

        action = preset.get("action")
        
        if action == "resize":
            width = preset.get("width")
            height = preset.get("height")
            if width:
                cmd.extend(["-resize", f"{width}x"])
            elif height:
                cmd.extend(["-resize", f"x{height}"])
        
        # Add output path at the end
        cmd.append(output_path)
        
        try:
            # Check if output directory exists, create if not
            out_dir = os.path.dirname(output_path)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            # Run command with Popen
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
            
            if process_holder is not None:
                process_holder[0] = process
                
            _, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"ImageMagick Error: {stderr}")
                return False
                
            return True

        except Exception as e:
            print(f"Exception during conversion: {e}")
            return False
