// YouTube IFrame Player API Controller

let player = null;
let isPlayerReady = false;

// YouTube IFrame API 스크립트 비동기 로드
function loadYouTubeIframeAPI() {
  if (window.YT && window.YT.Player) {
    onYouTubeIframeAPIReady();
    return;
  }
  const tag = document.createElement('script');
  tag.src = "https://www.youtube.com/iframe_api";
  const firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

// API 준비 콜백
window.onYouTubeIframeAPIReady = function() {
  console.log("YouTube IFrame API Ready");
  isPlayerReady = true;
};

// 특정 영상으로 플레이어 초기화 또는 변경
function initOrLoadVideo(videoId) {
  if (!player) {
    player = new YT.Player('player', {
      height: '100%',
      width: '100%',
      videoId: videoId,
      playerVars: {
        'playsinline': 1,
        'autoplay': 1,
        'rel': 0,
        'modestbranding': 1
      },
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
  } else {
    player.loadVideoById(videoId);
  }
}

function onPlayerReady(event) {
  console.log("Player is ready");
  const volumeSlider = document.getElementById('volumeSlider');
  if (volumeSlider) {
    player.setVolume(parseInt(volumeSlider.value, 10));
  }
}

function onPlayerStateChange(event) {
  // 재생 상태 변경 처리 필요 시 추가
}

// 특정 타임스탬프 위치로 이동 후 자동 재생
function jumpToAndPlay(seconds) {
  if (player && typeof player.seekTo === 'function') {
    player.seekTo(seconds, true);
    player.playVideo();
  } else {
    console.warn("Player is not ready to seek");
  }
}

// 볼륨 크기 조절 (0 ~ 100)
function setVolume(volumeLevel) {
  if (player && typeof player.setVolume === 'function') {
    player.setVolume(volumeLevel);
  }
}

// 초기화 호출
loadYouTubeIframeAPI();
