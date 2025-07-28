# 🎬 Video Processing Tutorial

This tutorial shows you how to upload and process videos in the RAG Web UI system, making video content searchable and available for AI chat.

## 🎯 What You'll Learn

- How to upload YouTube videos and local video files
- How video transcription works with faster-whisper
- How to chat with AI about video content
- Troubleshooting common issues

## 🚀 Quick Start

### Step 1: Access the Video Upload Interface

1. Open your browser and go to `http://localhost`
2. Navigate to the **Knowledge Base** section
3. Click on **Upload Documents** or **Add Video**

### Step 2: Upload a Video

#### Option A: YouTube URL
```
1. Select "YouTube URL" option
2. Paste the YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
3. Click "Upload"
4. Wait for processing (2-5 minutes depending on video length)
```

#### Option B: Local Video File
```
1. Select "Local File" option
2. Choose your video file (MP4, AVI, MOV, etc.)
3. Click "Upload"
4. Wait for processing
```

### Step 3: Monitor Processing

The system will:
1. ✅ **Download/Upload** the video
2. ✅ **Extract Audio** from the video
3. ✅ **Transcribe** using faster-whisper (4x faster than standard Whisper)
4. ✅ **Create Text Chunks** for better searchability
5. ✅ **Generate Embeddings** for AI retrieval
6. ✅ **Add to Knowledge Base** for AI chat

### Step 4: Chat About Your Video

Once processing is complete:
1. Go to the **Chat** section
2. Create a new chat session
3. Ask questions about your video:
   - "What is this video about?"
   - "Summarize the main points"
   - "Tell me about [specific topic] mentioned in the video"

## 📋 Supported Formats

### Video Files
- MP4 (.mp4) - Recommended
- AVI (.avi)
- MOV (.mov)
- WMV (.wmv)
- WebM (.webm)
- MKV (.mkv)
- FLV (.flv)

### Video Sources
- **YouTube URLs** - Any public YouTube video
- **Local Files** - Videos stored on your computer
- **Direct URLs** - Any publicly accessible video URL

## 🔧 System Requirements

### For Optimal Performance
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8GB+ (16GB recommended for large videos)
- **Storage**: Sufficient space for video files and transcripts
- **GPU**: Optional but recommended for faster transcription

### Docker Requirements
- Docker and Docker Compose installed
- At least 4GB RAM allocated to Docker
- Sufficient disk space for containers and data

## ⚡ Performance Features

### Faster-Whisper Benefits
- **4x faster** transcription compared to OpenAI Whisper
- **50% less memory** usage with optimized models
- **GPU acceleration** when CUDA is available
- **Better accuracy** with improved models

### Processing Optimizations
- Automatic audio extraction and optimization
- Intelligent chunking for better AI retrieval
- Parallel processing where possible
- Efficient storage and indexing

## 🧪 Testing Your Setup

### Test Video Processing
1. Use this sample YouTube URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. Upload and wait for processing
3. Check that the transcript appears in your documents
4. Test AI chat with questions about the video

### Verify AI Chat Integration
```
Test Questions:
- "What is this video about?"
- "Summarize the content"
- "What are the main topics discussed?"
```

## 🔍 Troubleshooting

### Common Issues

#### Video Upload Fails
- Check internet connection for YouTube URLs
- Verify video file format is supported
- Ensure sufficient disk space

#### Transcription Takes Too Long
- Large videos (>1 hour) may take 10-15 minutes
- Check system resources (CPU/RAM usage)
- Consider using shorter video clips for testing

#### AI Chat Can't Access Video Content
- Verify video processing completed successfully
- Check that transcript appears in document list
- Restart the system if needed

#### Docker Issues
- Ensure all containers are running: `docker-compose ps`
- Check logs: `docker-compose logs backend`
- Restart services: `docker-compose restart`

### Getting Help

If you encounter issues:
1. Check the troubleshooting section
2. Review system logs
3. Verify all dependencies are installed
4. Test with a simple, short video first

## 📚 Next Steps

After mastering video processing:
- Explore advanced chat features
- Upload multiple videos to build a video knowledge base
- Combine video content with documents for comprehensive AI assistance
- Set up automated video processing workflows

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Videos upload without errors
- ✅ Transcripts appear in your document list
- ✅ AI chat can answer questions about video content
- ✅ Search functionality finds video content
- ✅ Processing completes in reasonable time

Happy video processing! 🎬✨
