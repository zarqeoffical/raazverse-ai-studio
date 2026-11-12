# RAAZVERSE AI STUDIO

A free-first GitHub Actions starter that automatically creates a Hindi YouTube Short from the topic/script scenes in `content/video.json`.

## What happens automatically
1. Reads the supplied Hindi topic, narration and scene text.
2. Generates Hindi speech using the Edge TTS online service (internet required; availability/limits can change).
3. Creates original vertical motion-graphic scene cards locally with Pillow (no user photos required).
4. Combines visuals, narration and captions into a 1080x1920 MP4 with FFmpeg.
5. Produces a thumbnail and downloadable files as a GitHub Actions artifact.

## Run it
1. Open the **Actions** tab.
2. Select **Create RAAZVERSE Short**.
3. Tap **Run workflow**.
4. When the run succeeds, open it and download the `raazverse-short-video` artifact.
5. Review the finished video, factual accuracy, pronunciation and rights before uploading.

## Change the next video
Edit `content/video.json`. Keep the JSON structure:
- `title`: short video title
- `voice`: `hi-IN-MadhurNeural` (male) or `hi-IN-SwaraNeural` (female)
- `narration`: complete Hindi narration
- `scenes`: 4–7 objects with `heading`, `text`, and `visual`

The graphics are original motion-graphic cards, not generated photographic footage. This version does not autonomously research/verify new topics, and it does not upload to YouTube. Those need separate, permissioned services and review.

## Free-tier and quality notes
GitHub Actions and online TTS have usage/availability limits. Do not assume unlimited daily generation. Always review every Short before publishing. Use original content and avoid repetitive mass-produced videos with little viewer value.
