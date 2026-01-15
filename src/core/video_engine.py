import subprocess
import os

class VideoEngine:
    @staticmethod
    def convert(input_path: str, output_path: str, preset: dict, p_holder: list = None, progress_cb=None) -> bool:
        """
        Executes FFmpeg command based on preset.
        p_holder: Optional list acting as a mutable pointer to store the Popen object.
        progress_cb: Optional callback(int) for progress percentage.
        """
        cmd = ["ffmpeg", "-y", "-i", input_path] 

        # We need to see progress info, so removed "-loglevel error"
        # But we still want to hide banner
        cmd.extend(["-hide_banner"])

        action = preset.get("action")
        
        if action == "resize":
            width = preset.get("width")
            height = preset.get("height")
            
            if width and height:
                # User specified both, force exact dimensions
                # Note: This may change aspect ratio, but adheres to user request of "same as I give"
                cmd.extend(["-vf", f"scale={width}:{height}"])
            elif width:
                cmd.extend(["-vf", f"scale={width}:-2"])
            elif height:
                cmd.extend(["-vf", f"scale=-2:{height}"])
        
        cmd.append(output_path)
        
        try:
            # Check if output directory exists, create if not
            out_dir = os.path.dirname(output_path)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir)

            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

            if p_holder is not None:
                p_holder[0] = process

            total_duration = None
            
            # Read stderr line by line
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue

                # Parse Duration: 00:00:00.00
                if "Duration:" in line and total_duration is None:
                    try:
                        time_str = line.split("Duration:")[1].split(",")[0].strip()
                        h, m, s = time_str.split(':')
                        total_duration = float(h) * 3600 + float(m) * 60 + float(s)
                    except:
                        pass
                
                # Parse time=00:00:00.00
                if "time=" in line and total_duration:
                    try:
                        # Example: frame=... time=00:00:10.50 bitrate=...
                        # Find 'time='
                        parts = line.split()
                        for p in parts:
                            if p.startswith("time="):
                                t_str = p.split("=")[1]
                                h, m, s = t_str.split(':')
                                current_time = float(h) * 3600 + float(m) * 60 + float(s)
                                percent = int((current_time / total_duration) * 100)
                                if progress_cb:
                                    progress_cb(percent)
                                break
                    except:
                        pass

            process.wait()
            
            if process.returncode != 0:
                # End of stream 
                return False
                
            return True

        except Exception as e:
            print(f"Exception during video conversion: {e}")
            return False
