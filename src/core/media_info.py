import subprocess
import json
import os

class MediaInfoExtractor:
    @staticmethod
    def get_info(file_path: str) -> dict:
        """
        Extracts metadata from a file using ffprobe.
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": f"ffprobe failed: {result.stderr}"}

            data = json.loads(result.stdout)
            
            # Process and simplify data
            info = {
                "file": os.path.basename(file_path),
                "path": file_path,
                "size_bytes": os.path.getsize(file_path),
                "format": MediaInfoExtractor._get_clean_format(data.get("format", {}), file_path),
                "duration": data.get("format", {}).get("duration", "N/A"),
                "streams": []
            }
            
            # Friendly size
            size = info["size_bytes"]
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    info["size_str"] = f"{size:.2f} {unit}"
                    break
                size /= 1024

            for stream in data.get("streams", []):
                s_info = {
                    "index": stream.get("index"),
                    "type": stream.get("codec_type"),
                    "codec": stream.get("codec_name"),
                }
                
                if s_info["type"] == "video":
                    s_info["width"] = stream.get("width")
                    s_info["height"] = stream.get("height")
                    s_info["fps"] = stream.get("r_frame_rate")
                elif s_info["type"] == "audio":
                    s_info["channels"] = stream.get("channels")
                    s_info["sample_rate"] = stream.get("sample_rate")
                
                info["streams"].append(s_info)

            return info

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _get_clean_format(format_data, file_path):
        raw_format = format_data.get("format_name", "Unknown")
        long_name = format_data.get("format_long_name", "")
        
        # If it's a list (e.g. mov,mp4,m4a...), try to match extension
        if "," in raw_format:
            ext = os.path.splitext(file_path)[1].lower().replace(".", "")
            candidates = raw_format.split(",")
            if ext in candidates:
                return ext.upper()
            return candidates[0].upper() # Fallback to first
            
        return raw_format.upper()
