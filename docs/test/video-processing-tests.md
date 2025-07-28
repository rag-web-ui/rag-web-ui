# 🧪 Video Processing Test Suite

This document contains test cases and validation procedures for the video processing functionality.

## 🎯 Test Overview

### Test Categories
1. **Upload Tests** - Video upload functionality
2. **Processing Tests** - Transcription and indexing
3. **Integration Tests** - AI chat integration
4. **Performance Tests** - Speed and resource usage
5. **Error Handling Tests** - Failure scenarios

## 📋 Pre-Test Setup

### Environment Check
```bash
# Verify Docker services are running
docker-compose ps

# Check available disk space
df -h

# Verify system resources
free -h
```

### Test Data
- **Short Video**: 30-60 seconds for quick tests
- **Medium Video**: 5-10 minutes for standard tests  
- **Long Video**: 30+ minutes for stress tests
- **YouTube URLs**: Public videos for URL testing

## 🧪 Test Cases

### Test 1: YouTube URL Upload
**Objective**: Verify YouTube video download and processing

**Test Data**:
```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Expected Duration: ~3 minutes
Expected Size: ~10MB
```

**Steps**:
1. Navigate to video upload interface
2. Select "YouTube URL" option
3. Enter test URL
4. Click "Upload"
5. Monitor processing status

**Expected Results**:
- ✅ Video downloads successfully
- ✅ Audio extraction completes
- ✅ Transcription generates text
- ✅ Document appears in knowledge base
- ✅ Processing completes within 5 minutes

**Validation**:
```bash
# Check if video file exists in MinIO
curl -s http://localhost:9000/ragwebui/ | grep -i "rick"

# Verify transcript in database
docker-compose exec db mysql -u ragwebui -pragwebui ragwebui -e "SELECT file_name FROM documents WHERE file_name LIKE '%transcript%';"
```

### Test 2: Local File Upload
**Objective**: Verify local video file processing

**Test Data**:
- File format: MP4
- Duration: 1-2 minutes
- Size: 5-20MB

**Steps**:
1. Prepare test video file
2. Navigate to upload interface
3. Select "Local File" option
4. Choose test file
5. Upload and monitor

**Expected Results**:
- ✅ File uploads without errors
- ✅ Processing pipeline executes
- ✅ Transcript generated
- ✅ Content indexed for search

### Test 3: AI Chat Integration
**Objective**: Verify AI can access video content

**Prerequisites**: Complete Test 1 or Test 2

**Steps**:
1. Navigate to chat interface
2. Create new chat session
3. Ask about video content
4. Verify AI responses

**Test Queries**:
```
1. "What is this video about?"
2. "Summarize the main points"
3. "Tell me about [specific topic from video]"
4. "What did the speaker say about [topic]?"
```

**Expected Results**:
- ✅ AI provides relevant responses
- ✅ Responses reference video content
- ✅ No "I don't have information" errors
- ✅ Context includes video transcript

### Test 4: Performance Benchmarks
**Objective**: Measure processing performance

**Metrics to Track**:
- Upload time
- Transcription time
- Total processing time
- Memory usage
- CPU usage
- Disk usage

**Test Videos**:
```
Short (1 min):   Expected < 2 minutes processing
Medium (5 min):  Expected < 8 minutes processing  
Long (30 min):   Expected < 45 minutes processing
```

**Performance Commands**:
```bash
# Monitor system resources during processing
top -p $(docker-compose exec backend pgrep -f "python")

# Check processing logs
docker-compose logs backend | grep -i "transcription\|processing"

# Monitor disk usage
watch -n 5 'df -h | grep -E "(Size|ragwebui)"'
```

### Test 5: Error Handling
**Objective**: Verify system handles errors gracefully

**Error Scenarios**:

#### Invalid YouTube URL
```
Test URL: https://www.youtube.com/watch?v=INVALID_ID
Expected: Clear error message, no system crash
```

#### Unsupported File Format
```
Test File: document.txt (renamed to video.mp4)
Expected: Format validation error
```

#### Network Interruption
```
Test: Disconnect network during YouTube download
Expected: Timeout handling, retry mechanism
```

#### Insufficient Disk Space
```
Test: Fill disk to 95% capacity
Expected: Graceful failure with clear error message
```

## 📊 Test Results Template

### Test Execution Log
```
Date: ___________
Tester: ___________
Environment: ___________

Test 1 - YouTube Upload:
- Status: [ ] Pass [ ] Fail
- Duration: _____ minutes
- Notes: _________________

Test 2 - Local Upload:
- Status: [ ] Pass [ ] Fail  
- Duration: _____ minutes
- Notes: _________________

Test 3 - AI Integration:
- Status: [ ] Pass [ ] Fail
- Response Quality: [ ] Good [ ] Fair [ ] Poor
- Notes: _________________

Test 4 - Performance:
- Short Video: _____ minutes
- Medium Video: _____ minutes
- Memory Peak: _____ MB
- Notes: _________________

Test 5 - Error Handling:
- Invalid URL: [ ] Pass [ ] Fail
- Bad Format: [ ] Pass [ ] Fail
- Network Issues: [ ] Pass [ ] Fail
- Notes: _________________
```

## 🔧 Debugging Commands

### Check Processing Status
```bash
# View backend logs
docker-compose logs backend --tail=50

# Check video processing tasks
docker-compose exec db mysql -u ragwebui -pragwebui ragwebui -e "SELECT * FROM processing_tasks ORDER BY created_at DESC LIMIT 5;"

# Monitor ChromaDB collections
curl -s http://localhost:8001/api/v1/collections
```

### Verify Vector Store
```bash
# Check if video content is indexed
docker-compose exec backend python -c "
from app.services.vector_store.factory import VectorStoreFactory
from app.services.embedding.embedding_factory import EmbeddingsFactory
embeddings = EmbeddingsFactory.create()
vector_store = VectorStoreFactory.create('chroma', 'kb_1', embeddings)
docs = vector_store.similarity_search('video transcript', k=3)
print(f'Found {len(docs)} video-related documents')
for doc in docs:
    print(f'- {doc.metadata.get(\"file_name\", \"Unknown\")}')
"
```

## ✅ Success Criteria

### Minimum Requirements
- [ ] YouTube videos process successfully
- [ ] Local files upload and process
- [ ] AI chat can access video content
- [ ] Processing completes within reasonable time
- [ ] No system crashes or data corruption

### Performance Targets
- [ ] 1-minute video processes in < 3 minutes
- [ ] Memory usage stays under 2GB during processing
- [ ] System remains responsive during processing
- [ ] Error messages are clear and actionable

## 🚨 Known Issues

### Current Limitations
1. Very long videos (>2 hours) may timeout
2. Some YouTube videos may be geo-restricted
3. Processing is CPU-intensive for large files
4. Network interruptions can cause partial failures

### Workarounds
1. Split long videos into shorter segments
2. Use VPN for geo-restricted content
3. Process videos during low-usage periods
4. Implement retry mechanisms for network issues

## 📝 Test Maintenance

### Regular Testing Schedule
- **Daily**: Quick smoke tests with short videos
- **Weekly**: Full test suite execution
- **Monthly**: Performance benchmarking
- **Release**: Complete regression testing

### Test Data Management
- Keep test videos under 100MB total
- Use consistent test URLs that won't be deleted
- Document any test data dependencies
- Clean up test artifacts regularly

Happy testing! 🧪✨
