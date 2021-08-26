# Youtube Downloader
A CLI tool to download Youtube videos.

### Quick Start:
1. Download `youtube-downloader.py` and `config.jsonc`.
2. Edit `defaultDownloadPath` inside `config.jsonc` to where you would like to download your videos.
3. run `python youtube-downloader.py -u <video url>`, and replace `<video url>` with the Youtube video URL.

**For more help, run `python youtube-downloader.py -h`.**

### Formats supported:
* mp4
* webm

### To-Do:
Planned features:
- [x] webm support
- [ ] ability to download multiple videos at once (currently possible using a batch or shell script)