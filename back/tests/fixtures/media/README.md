# Media Fixtures for Integration Tests

This directory contains media files used to test the AI enrichment services (Faster-Whisper, BLIP-2, metadata generation).

## Required Files

### 1. audio.ogg (Voice Message)
- **Purpose:** Test Faster-Whisper transcription service
- **Requirements:** 
  - Format: OGG Opus (WhatsApp standard)
  - Duration: 5-10 seconds
  - Content: Clear speech in Portuguese (e.g., "Olá, gostaria de agendar uma consulta")
  - Size: < 100KB

**How to create:**
```bash
# Using ffmpeg to convert any audio to OGG
ffmpeg -i input.mp3 -c:a libopus -b:a 32k -ac 1 audio.ogg

# Or record directly with SoX
sox -d -r 16000 -c 1 audio.ogg trim 0 10
```

### 2. image.jpg (Medical/Clinical Image)
- **Purpose:** Test BLIP-2 image analysis
- **Requirements:**
  - Format: JPEG
  - Content: Medical/clinical context (e.g., clinic interior, medical equipment, healthy food)
  - Size: < 500KB
  - Resolution: 640x480 or similar

**Sample sources:**
- Unsplash: https://unsplash.com/s/photos/clinic
- Free medical images: https://www.pexels.com/search/medical/

### 3. video.mp4 (Short Video)
- **Purpose:** Test video transcription + metadata generation
- **Requirements:**
  - Format: MP4 (H.264)
  - Duration: 5-10 seconds
  - Audio: Portuguese speech
  - Size: < 1MB

**How to create:**
```bash
# Convert and compress existing video
ffmpeg -i input.mov -vcodec h264 -acodec aac -vf scale=480:360 -t 10 video.mp4
```

### 4. document.pdf (Medical Document)
- **Purpose:** Test document metadata generation
- **Requirements:**
  - Format: PDF
  - Content: Medical-related text (e.g., diet plan, exercise guide, consultation info)
  - Size: < 200KB
  - Pages: 1-2

**How to create:**
- Use LibreOffice/Word to create a simple document about diet/exercise
- Export as PDF

## Usage in Tests

Tests in `test_04_messages.py` use these files via:
1. **Local server:** Files served via pytest fixture (recommended)
2. **GitHub raw:** After committing, accessible via `https://raw.githubusercontent.com/...`
3. **Public URLs:** Temporary fallback for development

## Current Status

Tests currently use public URLs for immediate validation:
- Audio: Sample OGG from public repository
- Image: Unsplash medical image
- Video: Sample MP4 from sample-videos.com
- Document: Public PDF sample

**Next step:** Replace with local fixtures once files are added to this directory.
