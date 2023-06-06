from whisper_jax import FlaxWhisperPipline
import jax.numpy as jnp

# instantiate pipeline with bfloat16 and enable batching
pipeline = FlaxWhisperPipline("openai/whisper-large-v2", dtype=jnp.bfloat16, batch_size=16)

filepath = "./assets/audio/BarbaraWalters.mp3"
# transcribe and return timestamps
outputs = pipeline(filepath,  task="transcribe", return_timestamps=True)

# python -m pip install git+https://github.com/sanchit-gandhi/whisper-jax.git
# python -m pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
