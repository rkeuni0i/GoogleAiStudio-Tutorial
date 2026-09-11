// YouTube IFrame Player API Controller

let player = null;
let isPlayerReady = false;
let currentVolume = 100;
let pendingVideoId = null;

// YouTube IFrame API 스크립트 비동기 로드
function loadYouTubeIframeAPI() {
  if (window.YT && window.YT.Player) {
    onYouTubeIframeAPIReady();
    return;
  }
  if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  }
}

// API 준비 콜백
window.onYouTubeIframeAPIReady = function() {
  console.log("YouTube IFrame API Ready");
  if (pendingVideoId) {
    const vid = pendingVideoId;
    pendingVideoId = null;
    initOrLoadVideo(vid);
  }
};

// 특정 영상으로 플레이어 초기화 또는 변경
function initOrLoadVideo(videoId) {
  if (!videoId) return;

  if (!window.YT || !window.YT.Player) {
    pendingVideoId = videoId;
    return;
  }

  // 슬라이더 현재 값 동기화
  const volumeSlider = document.getElementById('volumeSlider');
  if (volumeSlider) {
    currentVolume = parseInt(volumeSlider.value, 10);
    if (isNaN(currentVolume)) currentVolume = 100;
  }

  if (!player) {
    const playerVars = {
      playsinline: 1,
      autoplay: 1,
      rel: 0,
      modestbranding: 1,
      enablejsapi: 1
    };
    if (window.location.origin && window.location.origin !== 'null' && !window.location.origin.startsWith('file:')) {
      playerVars.origin = window.location.origin;
    }

    player = new YT.Player('player', {
      height: '100%',
      width: '100%',
      videoId: videoId,
      playerVars: playerVars,
      events: {
        onReady: onPlayerReady,
        onStateChange: onPlayerStateChange
      }
    });
  } else {
    isPlayerReady = false;
    if (typeof player.loadVideoById === 'function') {
      player.loadVideoById(videoId);
    }
  }
}

function onPlayerReady(event) {
  console.log("Player is ready");
  isPlayerReady = true;
  player = event.target;

  const volumeSlider = document.getElementById('volumeSlider');
  const targetVolume = volumeSlider ? parseInt(volumeSlider.value, 10) : currentVolume;
  setVolume(isNaN(targetVolume) ? 100 : targetVolume);
}

function onPlayerStateChange(event) {
  // YT.PlayerState.PLAYING === 1: 영상 재생 시작 시 볼륨 상태 동기화
  if (event.data === 1) {
    isPlayerReady = true;
    if (player && typeof player.setVolume === 'function') {
      player.setVolume(currentVolume);
    }
  }
}

// 특정 타임스탬프 위치로 이동 후 자동 재생
function jumpToAndPlay(seconds) {
  if (player && typeof player.seekTo === 'function') {
    player.seekTo(seconds, true);
    if (typeof player.playVideo === 'function') {
      player.playVideo();
    }
    // 타임스탬프 클릭은 사용자 인터랙션이므로 음소거 해제 적용
    if (currentVolume > 0 && typeof player.unMute === 'function') {
      player.unMute();
    }
  } else {
    console.warn("Player is not ready to seek");
  }
}

// 볼륨 크기 조절 (0 ~ 100)
function setVolume(volumeLevel) {
  const level = Math.max(0, Math.min(100, parseInt(volumeLevel, 10) || 0));
  currentVolume = level;

  if (player && typeof player.setVolume === 'function') {
    try {
      player.setVolume(level);
      // 브라우저의 자동재생(Autoplay) 정책으로 인해 영상이 muted 상태로 시작된 경우,
      // 볼륨을 조절해도 mute 상태가 유지되어 소리가 들리지 않으므로 unMute()를 명시적으로 호출해야 합니다.
      if (level > 0) {
        if (typeof player.unMute === 'function') {
          player.unMute();
        }
      } else {
        if (typeof player.mute === 'function') {
          player.mute();
        }
      }
    } catch (e) {
      console.warn("setVolume failed:", e);
    }
  }
}

// 전역 객체(window) 바인딩 보장
window.initOrLoadVideo = initOrLoadVideo;
window.jumpToAndPlay = jumpToAndPlay;
window.setVolume = setVolume;

// 초기화 호출
loadYouTubeIframeAPI();
