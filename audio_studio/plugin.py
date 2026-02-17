"""
Wan2GP Audio Studio Plugin
Integrates the audio processing pipeline with Wan2GP
"""
import gradio as gr
from shared.utils.plugins import WAN2GPPlugin
from shared.utils.process_locks import acquire_GPU_ressources, release_GPU_ressources, any_GPU_process_running
import sys
from pathlib import Path

# Add audio_backend to path
AUDIO_BACKEND_PATH = Path(__file__).parent.parent / "audio_backend"
if str(AUDIO_BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(AUDIO_BACKEND_PATH))

PlugIn_Name = "Audio Studio"
PlugIn_Id = "AudioStudio"


def acquire_GPU(state):
    GPU_process_running = any_GPU_process_running(state, PlugIn_Id)
    if GPU_process_running:
        gr.Error("Another Plugin is using the GPU")
    acquire_GPU_ressources(state, PlugIn_Id, PlugIn_Name, gr=gr)


def release_GPU(state):
    release_GPU_ressources(state, PlugIn_Id)


class AudioStudioPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.backend_process = None

    def setup_ui(self):
        self.request_global("get_current_model_settings")
        self.request_component("refresh_form_trigger")
        self.request_component("state")
        self.request_component("main_tabs")

        self.add_tab(
            tab_id=PlugIn_Id,
            label=PlugIn_Name,
            component_constructor=self.create_config_ui,
        )

    def on_tab_select(self, state: dict) -> None:
        return None

    def on_tab_deselect(self, state: dict) -> None:
        pass

    def create_config_ui(self):
        # Create a placeholder that instructs users to start the audio studio server
        with gr.Column():
            gr.HTML("""
                <div style="text-align: center; padding: 40px;">
                    <h2 style="font-size: 24px; margin-bottom: 20px;">🎵 Wan2GP Audio Studio</h2>
                    <p style="color: #9ca3af; margin-bottom: 20px;">
                        Segment-based audio processing pipeline with SwiftF0, SVC, and instrumental generation
                    </p>
                    
                    <div style="background: #1f2937; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="margin-bottom: 15px;">🚀 Quick Start</h3>
                        <ol style="text-align: left; padding-left: 20px; line-height: 1.8;">
                            <li>Open terminal and navigate to project directory</li>
                            <li>Run: <code style="background: #374151; padding: 4px 8px; border-radius: 4px;">python audio_backend/main.py</code></li>
                            <li>Open browser to: <code style="background: #374151; padding: 4px 8px; border-radius: 4px;">http://localhost:3000</code></li>
                        </ol>
                    </div>
                    
                    <div style="background: #1f2937; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="margin-bottom: 15px;">📋 Features</h3>
                        <ul style="text-align: left; padding-left: 20px; line-height: 1.8;">
                            <li><strong>SwiftF0</strong> - Pitch extraction and manipulation</li>
                            <li><strong>SVC</strong> - Voice conversion (so-vits-svc, HQ-SVC, Echo)</li>
                            <li><strong>Instrumental</strong> - Background music generation (HeartMuLa, ACE-Step)</li>
                            <li><strong>Segment Processing</strong> - Optimized for RTX 3070 (8GB VRAM)</li>
                        </ul>
                    </div>
                    
                    <div style="background: #1f2937; padding: 20px; border-radius: 8px;">
                        <h3 style="margin-bottom: 15px;">📖 Documentation</h3>
                        <p style="color: #9ca3af; margin-bottom: 10px;">
                            Full documentation available in:
                        </p>
                        <ul style="text-align: left; padding-left: 20px; line-height: 1.8;">
                            <li><code style="background: #374151; padding: 4px 8px; border-radius: 4px;">audio_studio/README.md</code></li>
                            <li><code style="background: #374151; padding: 4px 8px; border-radius: 4px;">audio_studio/SETUP.md</code></li>
                        </ul>
                    </div>
                </div>
            """)

            # Quick start buttons
            gr.Markdown("### Quick Actions")

            with gr.Row():
                start_backend_btn = gr.Button("Start Backend Server", variant="primary")
                open_frontend_btn = gr.Button("Open Frontend", variant="secondary")

            # Server status
            status_output = gr.Textbox(
                label="Server Status",
                value="Backend: Not running | Frontend: Not accessible",
                interactive=False
            )

            # Server logs
            logs_output = gr.Textbox(
                label="Server Logs",
                value="Ready to start...",
                lines=10,
                interactive=False
            )

        self.on_tab_outputs = [status_output, logs_output]

        start_backend_btn.click(
            fn=self.start_backend,
            inputs=[],
            outputs=[status_output, logs_output]
        )

        open_frontend_btn.click(
            fn=self.open_frontend,
            inputs=[],
            outputs=[logs_output]
        )

    def start_backend(self):
        """Start the FastAPI backend server"""
        import subprocess
        import threading

        try:
            # Start backend in a separate thread
            def run_backend():
                import sys
                from pathlib import Path
                
                backend_script = Path(__file__).parent.parent / "audio_backend" / "main.py"
                subprocess.Popen(
                    [sys.executable, str(backend_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            thread = threading.Thread(target=run_backend, daemon=True)
            thread.start()

            return (
                "Backend: Starting... | Frontend: Not accessible",
                "Backend server starting on http://127.0.0.1:8001\n\nPlease wait a few seconds for the server to start."
            )
        except Exception as e:
            return (
                f"Backend: Failed ({str(e)}) | Frontend: Not accessible",
                f"Error starting backend: {str(e)}"
            )

    def open_frontend(self):
        """Open the frontend in a new browser tab"""
        import webbrowser

        try:
            webbrowser.open("http://localhost:3000")
            return "Opening frontend at http://localhost:3000..."
        except Exception as e:
            return f"Failed to open frontend: {str(e)}\n\nPlease manually navigate to http://localhost:3000"
