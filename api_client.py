import subprocess
import shlex

def call_ollama(prompt: str) -> str:
    """
    Call Ollama CLI safely using subprocess.
    """
    try:
        # Properly quote the prompt for command line
        cmd = ["ollama", "run", "qwen3:8b", prompt]

        # Use shlex.quote for safety if needed
        cmd_str = " ".join([shlex.quote(c) for c in cmd])
        print("Running command:", cmd_str)

        result = subprocess.run(
            cmd_str,
            capture_output=True,
            text=True,
            shell=True,  # must be True if passing as single string
            timeout=120  # prevent infinite hang
        )

        output = result.stdout.strip()
        print("Ollama output preview:", output[:300])
        return output

    except subprocess.TimeoutExpired:
        return "Error: Ollama request timed out."
    except subprocess.CalledProcessError as e:
        print("Ollama CLI error:", e.stderr)
        return "Error: Could not generate response from Ollama."
    except UnicodeDecodeError as e:
        print("Unicode decoding error:", e)
        return "Error: Unicode decoding issue with Ollama output."
