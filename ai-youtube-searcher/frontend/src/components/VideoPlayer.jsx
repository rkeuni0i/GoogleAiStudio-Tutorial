import React, { useEffect, useRef, useState } from 'react';

/**
 * YouTube IFrame 플레이어 및 볼륨 조절 컨트롤러
 */
export default function VideoPlayer({ videoId, title, uploader, playerRef }) {
  const [volume, setVolume] = useState(100);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!videoId) return;

    const loadPlayer = () => {
      if (window.YT && window.YT.Player) {
        if (playerRef.current) {
          playerRef.current.loadVideoById(videoId);
        } else {
          playerRef.current = new window.YT.Player('yt-player-target', {
            height: '100%',
            width: '100%',
            videoId: videoId,
            playerVars: {
              playsinline: 1,
              autoplay: 1,
              rel: 0,
              modestbranding: 1
            },
            events: {
              onReady: (e) => {
                e.target.setVolume(volume);
              }
            }
          });
        }
      } else {
        // IFrame API 스크립트 로드
        if (!document.getElementById('yt-iframe-api')) {
          const tag = document.createElement('script');
          tag.id = 'yt-iframe-api';
          tag.src = 'https://www.youtube.com/iframe_api';
          document.body.appendChild(tag);
        }
        window.onYouTubeIframeAPIReady = () => {
          playerRef.current = new window.YT.Player('yt-player-target', {
            height: '100%',
            width: '100%',
            videoId: videoId,
            playerVars: {
              playsinline: 1,
              autoplay: 1,
              rel: 0,
              modestbranding: 1
            },
            events: {
              onReady: (e) => {
                e.target.setVolume(volume);
              }
            }
          });
        };
      }
    };

    loadPlayer();
  }, [videoId]);

  const handleVolumeChange = (e) => {
    const val = parseInt(e.target.value, 10);
    setVolume(val);
    if (playerRef.current && typeof playerRef.current.setVolume === 'function') {
      playerRef.current.setVolume(val);
      if (val > 0 && typeof playerRef.current.unMute === 'function') {
        playerRef.current.unMute();
      } else if (val === 0 && typeof playerRef.current.mute === 'function') {
        playerRef.current.mute();
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* 16:9 Aspect Ratio Container */}
      <div className="relative w-full pb-[56.25%] h-0 bg-black rounded-xl overflow-hidden shadow-2xl border border-[#272727]">
        <div id="yt-player-target" className="absolute top-0 left-0 w-full h-full"></div>
      </div>

      {/* Video Details & Volume Controller */}
      <div className="bg-[#181818] border border-[#272727] rounded-xl p-4 sm:p-5 space-y-4">
        <div>
          <h1 className="text-lg sm:text-xl font-bold text-white leading-snug">
            {title || '영상 제목'}
          </h1>
          <p className="text-sm text-neutral-400 mt-1 flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            <span>{uploader || '채널명'}</span>
          </p>
        </div>

        <hr className="border-[#2a2a2a]" />

        {/* Custom Volume Slider */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-red-500 fill-current" viewBox="0 0 24 24">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
            <span className="text-sm font-medium text-neutral-300">커스텀 볼륨 조절</span>
          </div>
          <div className="flex items-center gap-3 w-48 sm:w-60">
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={handleVolumeChange}
              className="w-full cursor-pointer accent-red-600"
            />
            <span className="text-xs font-mono text-neutral-400 w-10 text-right">
              {volume}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
