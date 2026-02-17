import gradio as gr
from shared.utils.plugins import WAN2GPPlugin
from shared.utils.process_locks import acquire_GPU_ressources, release_GPU_ressources, any_GPU_process_running
import os
import subprocess
import sys
import signal
import time
import json

PlugIn_Name = "Cover Studio"
PlugIn_Id = "CoverStudio"

class CoverStudioPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.server_process = None
        self.server_port = 8765
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))

    def setup_ui(self):
        self.request_component("state")
        self.request_component("main_tabs")
        
        self.add_tab(
            tab_id=PlugIn_Id,
            label=PlugIn_Name,
            component_constructor=self.create_ui,
        )

    def start_server(self):
        if self.server_process and self.server_process.poll() is None:
            return "Server is already running"
        
        try:
            backend_dir = os.path.join(self.plugin_dir, "backend")
            server_script = os.path.join(backend_dir, "server.py")
            
            if not os.path.exists(server_script):
                return f"Error: Server script not found at {server_script}"
            
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.dirname(self.plugin_dir)))
            
            self.server_process = subprocess.Popen(
                [sys.executable, server_script],
                cwd=backend_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            time.sleep(2)
            
            if self.server_process.poll() is None:
                return f"✓ Server started successfully on port {self.server_port}"
            else:
                stdout, stderr = self.server_process.communicate()
                return f"Error: Server failed to start\nStdout: {stdout.decode()}\nStderr: {stderr.decode()}"
        except Exception as e:
            return f"Error starting server: {str(e)}"

    def stop_server(self):
        if not self.server_process or self.server_process.poll() is not None:
            return "Server is not running"
        
        try:
            if sys.platform == "win32":
                self.server_process.terminate()
            else:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
            
            time.sleep(1)
            
            if self.server_process.poll() is None:
                self.server_process.kill()
            
            return "✓ Server stopped successfully"
        except Exception as e:
            return f"Error stopping server: {str(e)}"

    def get_server_status(self):
        if self.server_process and self.server_process.poll() is None:
            return f"🟢 Running on port {self.server_port}"
        else:
            return "🔴 Stopped"

    def create_ui(self):
        with gr.Column():
            gr.Markdown("""
            # 🎤 Cover Studio
            
            Full-length AI cover generation with voice conversion, pitch extraction, and instrumental generation.
            
            ## Features
            - **Voice Conversion**: SwiftF0 + SVC (so-vits-svc/HQ-SVC/Echo)
            - **Instrumental Generation**: HeartMuLa/ACE-Step
            - **Segment-by-Segment Pipeline**: Process long audio efficiently
            - **Real-time Waveform Visualization**: Wavesurfer.js integration
            - **Modern Web Interface**: React + Tailwind CSS
            """)
            
            with gr.Row():
                status_text = gr.Textbox(
                    label="Server Status",
                    value=self.get_server_status(),
                    interactive=False
                )
                refresh_status_btn = gr.Button("🔄 Refresh Status", scale=0)
            
            with gr.Row():
                start_btn = gr.Button("▶️ Start Server", variant="primary")
                stop_btn = gr.Button("⏹️ Stop Server", variant="stop")
            
            server_output = gr.Textbox(label="Server Output", lines=3)
            
            gr.Markdown("---")
            
            gr.Markdown(f"""
            ### Access the Cover Studio Web App
            
            Once the server is running, open your browser and navigate to:
            
            **[http://localhost:{self.server_port}](http://localhost:{self.server_port})**
            
            The web interface provides:
            - Audio file upload and processing
            - Voice model selection and management
            - Real-time waveform visualization
            - Segment-by-segment processing controls
            - Download processed covers
            """)
            
            with gr.Accordion("Technical Details", open=False):
                gr.Markdown("""
                ### Pipeline Architecture
                
                **Input Processing:**
                1. Audio source separation (vocals/instrumental)
                2. Pitch extraction with SwiftF0
                3. Segment detection and splitting
                
                **Voice Conversion:**
                1. Load SVC model (so-vits-svc/HQ-SVC/Echo)
                2. Process segments with pitch guidance
                3. Apply voice characteristics
                
                **Instrumental Generation (Optional):**
                1. HeartMuLa/ACE-Step model loading
                2. Generate instrumental from MIDI/text
                3. Mix with converted vocals
                
                **Output:**
                1. Merge processed segments
                2. Apply post-processing effects
                3. Export final cover
                """)
            
            with gr.Accordion("Model Configuration", open=False):
                gr.Markdown("""
                ### Supported Models
                
                **Voice Conversion:**
                - so-vits-svc 4.0/4.1
                - HQ-SVC (High Quality SVC)
                - Echo-SVC
                
                **Pitch Extraction:**
                - SwiftF0 (Fast and accurate F0 estimation)
                
                **Instrumental Generation:**
                - HeartMuLa (Music generation)
                - ACE-Step (Advanced audio synthesis)
                
                Models should be placed in: `plugins/wan2gp-cover-studio/models/`
                """)
            
            start_btn.click(
                fn=self.start_server,
                inputs=[],
                outputs=[server_output]
            ).then(
                fn=self.get_server_status,
                inputs=[],
                outputs=[status_text]
            )
            
            stop_btn.click(
                fn=self.stop_server,
                inputs=[],
                outputs=[server_output]
            ).then(
                fn=self.get_server_status,
                inputs=[],
                outputs=[status_text]
            )
            
            refresh_status_btn.click(
                fn=self.get_server_status,
                inputs=[],
                outputs=[status_text]
            )

    def on_tab_select(self, state: dict) -> None:
        pass

    def on_tab_deselect(self, state: dict) -> None:
        pass

    def __del__(self):
        if self.server_process and self.server_process.poll() is None:
            try:
                self.stop_server()
            except:
                pass
