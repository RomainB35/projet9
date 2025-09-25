from huggingface_hub import snapshot_download
snapshot_download(repo_id='bofenghuang/whisper-large-v3-french-distil-dec16', local_dir='app/models/whisper-large-v3-french-distil-dec16', allow_patterns='ctranslate2/*')
