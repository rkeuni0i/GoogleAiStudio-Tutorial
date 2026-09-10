// AI YouTube Searcher App Controller

let currentVideoData = null;
let currentTab = 'transcript'; // 'transcript' | 'qa'

document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
});

function setupEventListeners() {
  const searchForm = document.getElementById('searchForm');
  const urlInput = document.getElementById('urlInput');
  const clearUrlBtn = document.getElementById('clearUrlBtn');
  
  // URL 클리어 버튼 (유튜브 검색창 스타일 X 버튼)
  if (clearUrlBtn && urlInput) {
    urlInput.addEventListener('input', () => {
      clearUrlBtn.style.display = urlInput.value ? 'block' : 'none';
    });
    clearUrlBtn.addEventListener('click', () => {
      urlInput.value = '';
      clearUrlBtn.style.display = 'none';
      urlInput.focus();
    });
  }

  // 검색 폼 제출
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (url) {
      processVideo(url);
    }
  });

  // 볼륨 슬라이더
  const volumeSlider = document.getElementById('volumeSlider');
  const volumePercent = document.getElementById('volumePercent');
  if (volumeSlider) {
    volumeSlider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value, 10);
      setVolume(val);
      if (volumePercent) {
        volumePercent.innerText = `${val}%`;
      }
    });
  }

  // 탭 전환 버튼
  const tabTranscriptBtn = document.getElementById('tabTranscriptBtn');
  const tabQABtn = document.getElementById('tabQABtn');
  const panelTranscript = document.getElementById('panelTranscript');
  const panelQA = document.getElementById('panelQA');

  tabTranscriptBtn.addEventListener('click', () => {
    currentTab = 'transcript';
    tabTranscriptBtn.classList.add('border-b-2', 'border-red-600', 'text-white', 'font-semibold');
    tabTranscriptBtn.classList.remove('text-neutral-400');
    tabQABtn.classList.remove('border-b-2', 'border-red-600', 'text-white', 'font-semibold');
    tabQABtn.classList.add('text-neutral-400');
    
    panelTranscript.classList.remove('hidden');
    panelQA.classList.add('hidden');
  });

  tabQABtn.addEventListener('click', () => {
    currentTab = 'qa';
    tabQABtn.classList.add('border-b-2', 'border-red-600', 'text-white', 'font-semibold');
    tabQABtn.classList.remove('text-neutral-400');
    tabTranscriptBtn.classList.remove('border-b-2', 'border-red-600', 'text-white', 'font-semibold');
    tabTranscriptBtn.classList.add('text-neutral-400');
    
    panelQA.classList.remove('hidden');
    panelTranscript.classList.add('hidden');
  });

  // Q&A 폼 제출
  const qaForm = document.getElementById('qaForm');
  const questionInput = document.getElementById('questionInput');
  qaForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const question = questionInput.value.trim();
    if (question && currentVideoData) {
      sendQuestion(question);
      questionInput.value = '';
    }
  });
}

// 1. 영상 오디오 추출 및 STT 분석 요청
async function processVideo(url) {
  const loadingOverlay = document.getElementById('loadingOverlay');
  const loadingStatus = document.getElementById('loadingStatus');
  const emptyState = document.getElementById('emptyState');
  const mainContent = document.getElementById('mainContent');

  try {
    loadingOverlay.classList.remove('hidden');
    loadingStatus.innerText = 'YouTube 오디오를 추출하고 Gemini AI로 자막 및 타임라인을 분석하는 중입니다...';

    const response = await fetch('/api/process-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '영상 처리에 실패했습니다.');
    }

    currentVideoData = await response.json();

    // UI 업데이트
    emptyState.classList.add('hidden');
    mainContent.classList.remove('hidden');

    document.getElementById('videoTitle').innerText = currentVideoData.title;
    document.getElementById('videoUploader').innerText = currentVideoData.uploader;

    // 플레이어 로드
    initOrLoadVideo(currentVideoData.video_id);

    // 자막 렌더링
    renderTranscript(currentVideoData.transcript);

    // Q&A 영역 초기화
    resetChat();

  } catch (err) {
    alert(`오류: ${err.message}`);
  } finally {
    loadingOverlay.classList.add('hidden');
  }
}

// 2. 자막 타임라인 리스트 렌더링
function renderTranscript(transcript) {
  const listContainer = document.getElementById('transcriptList');
  listContainer.innerHTML = '';

  if (!transcript || transcript.length === 0) {
    listContainer.innerHTML = `
      <div class="text-center py-8 text-neutral-500 text-sm">
        추출된 자막이 없습니다.
      </div>
    `;
    return;
  }

  transcript.forEach((item) => {
    const row = document.createElement('div');
    row.className = 'group flex items-start gap-3 p-2.5 rounded-lg hover:bg-neutral-800 transition-colors cursor-pointer border border-transparent hover:border-neutral-700';
    
    row.innerHTML = `
      <button class="shrink-0 px-2 py-0.5 bg-neutral-800 group-hover:bg-red-600 text-red-500 group-hover:text-white rounded text-xs font-mono font-medium transition-colors">
        ${item.start_time}
      </button>
      <p class="text-sm text-neutral-200 leading-snug group-hover:text-white">
        ${item.text}
      </p>
    `;

    // 클릭 시 해당 타임스탬프로 이동하여 자동 재생
    row.addEventListener('click', () => {
      jumpToAndPlay(item.seconds);
    });

    listContainer.appendChild(row);
  });
}

// 3. AI Q&A 채팅 전송
async function sendQuestion(question) {
  const chatMessages = document.getElementById('chatMessages');

  // 사용자 메시지 추가
  appendMessage('user', question);

  // 로딩 버블 추가
  const loadingBubble = appendMessage('assistant', 'Gemini AI가 자막을 분석하여 관련 구간을 탐색 중입니다...', true);

  try {
    const response = await fetch('/api/qa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_id: currentVideoData.video_id,
        question: question,
        video_title: currentVideoData.title,
        transcript: currentVideoData.transcript
      })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || '답변 생성 실패');
    }

    const data = await response.json();
    loadingBubble.remove();

    // AI 응답 버블 추가
    appendMessage('assistant', data.answer, false, data.target_seconds, data.timestamp_str);

    // 자동 재생 기능: 답변에 명확한 타임스탬프(초 > 0)가 있으면 해당 시점으로 자동 이동 및 재생!
    if (data.target_seconds && data.target_seconds > 0) {
      jumpToAndPlay(data.target_seconds);
    }

  } catch (err) {
    loadingBubble.remove();
    appendMessage('assistant', `⚠️ 오류가 발생했습니다: ${err.message}`);
  }
}

function appendMessage(role, text, isLoading = false, targetSeconds = null, timestampStr = null) {
  const chatMessages = document.getElementById('chatMessages');
  const msgWrapper = document.createElement('div');
  msgWrapper.className = `flex gap-3 ${role === 'user' ? 'justify-end' : 'justify-start'}`;

  const bubble = document.createElement('div');
  bubble.className = `max-w-[85%] rounded-2xl p-3.5 text-sm leading-relaxed ${
    role === 'user'
      ? 'bg-red-600 text-white rounded-br-none'
      : 'bg-neutral-800 text-neutral-100 rounded-bl-none border border-neutral-700'
  } ${isLoading ? 'animate-pulse text-neutral-400' : ''}`;

  let contentHtml = `<div>${text}</div>`;

  // 타임스탬프 이동 버튼 포함
  if (role === 'assistant' && targetSeconds !== null && targetSeconds > 0) {
    contentHtml += `
      <div class="mt-3 pt-2.5 border-t border-neutral-700 flex items-center justify-between">
        <span class="text-xs text-neutral-400">영상 타임라인</span>
        <button onclick="jumpToAndPlay(${targetSeconds})" class="inline-flex items-center gap-1.5 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-full shadow transition-all">
          <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          <span>${timestampStr || targetSeconds + '초'} 위치 재생</span>
        </button>
      </div>
    `;
  }

  bubble.innerHTML = contentHtml;
  msgWrapper.appendChild(bubble);
  chatMessages.appendChild(msgWrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  return msgWrapper;
}

function resetChat() {
  const chatMessages = document.getElementById('chatMessages');
  chatMessages.innerHTML = `
    <div class="p-3 bg-neutral-800/60 border border-neutral-700/60 rounded-xl text-neutral-400 text-xs leading-relaxed">
      💡 <strong>AI Q&A 가이드:</strong><br>
      "이 영상에서 핵심 결론이 뭐야?", "XX를 설명하는 부분이 어디야?" 처럼 질문하시면,
      Gemini 3.8 Flash가 답변을 알려드리고 <strong>해당 시점으로 영상을 자동 이동 및 재생</strong>합니다!
    </div>
  `;
}
