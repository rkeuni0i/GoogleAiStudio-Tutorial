import React, { useState, useRef } from 'react';
import Header from './components/Header';
import VideoPlayer from './components/VideoPlayer';
import Transcript from './components/Transcript';
import ChatQA from './components/ChatQA';

export default function App() {
  const [videoData, setVideoData] = useState(null);
  const [activeTab, setActiveTab] = useState('transcript'); // 'transcript' | 'qa'
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const playerRef = useRef(null);

  const handleSearch = async (url) => {
    setIsLoading(true);
    setLoadingStatus('YouTube 오디오를 추출하고 Gemini AI로 자막 및 타임라인을 분석하는 중입니다...');

    try {
      const response = await fetch('/api/process-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || '영상 처리에 실패했습니다.');
      }

      const data = await response.json();
      setVideoData(data);
    } catch (err) {
      alert(`오류: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSeek = (seconds) => {
    if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
      playerRef.current.seekTo(seconds, true);
      playerRef.current.playVideo();
    }
  };

  return (
    <div className="bg-[#0f0f0f] text-[#f1f1f1] min-h-screen flex flex-col font-sans">
      {/* Header */}
      <Header onSearch={handleSearch} isLoading={isLoading} />

      {/* Main Container */}
      <main className="flex-1 max-w-[1800px] w-full mx-auto p-4 sm:p-6">
        {!videoData ? (
          /* Empty State */
          <div className="py-24 text-center max-w-lg mx-auto">
            <div className="w-16 h-16 bg-[#1f1f1f] rounded-2xl flex items-center justify-center text-red-500 mx-auto mb-5 shadow-lg border border-[#2e2e2e]">
              <svg className="w-8 h-8 fill-current" viewBox="0 0 24 24">
                <path d="M12 2l2.4 7.2h7.6l-6 4.8 2.4 7.2-6.4-4.8-6.4 4.8 2.4-7.2-6-4.8h7.6z"/>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">유튜브 영상을 검색하고 질문해보세요</h2>
            <p className="text-sm text-neutral-400 leading-relaxed mb-6">
              상단 검색창에 YouTube 링크를 넣으면 Gemini가 오디오를 분석하여<br />
              시간대별 자막을 추출하고, 질문한 내용의 정확한 영상 위치로 이동해 드립니다.
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#181818] rounded-xl border border-[#2a2a2a] text-xs text-neutral-400">
              <svg className="w-4 h-4 text-neutral-500 fill-current" viewBox="0 0 24 24">
                <path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
              </svg>
              <span>자막 타임스탬프 클릭 시 즉시 해당 시점으로 점프 및 자동 재생</span>
            </div>
          </div>
        ) : (
          /* Main Content Grid */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left: Video Player (7 Cols) */}
            <section className="lg:col-span-7">
              <VideoPlayer
                videoId={videoData.video_id}
                title={videoData.title}
                uploader={videoData.uploader}
                playerRef={playerRef}
              />
            </section>

            {/* Right: Tabs Panel (5 Cols) */}
            <section className="lg:col-span-5 bg-[#181818] border border-[#272727] rounded-xl flex flex-col h-[650px] shadow-xl overflow-hidden">
              {/* Tab Header */}
              <div className="flex border-b border-[#272727] bg-[#141414]">
                <button
                  onClick={() => setActiveTab('transcript')}
                  className={`flex-1 py-3.5 text-center text-sm font-semibold transition-all flex items-center justify-center gap-2 ${
                    activeTab === 'transcript'
                      ? 'border-b-2 border-red-600 text-white'
                      : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                    <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/>
                  </svg>
                  <span>타임라인 자막</span>
                </button>
                <button
                  onClick={() => setActiveTab('qa')}
                  className={`flex-1 py-3.5 text-center text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                    activeTab === 'qa'
                      ? 'border-b-2 border-red-600 text-white'
                      : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                    <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/>
                  </svg>
                  <span>AI 질의응답 (Q&A)</span>
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === 'transcript' ? (
                <Transcript transcript={videoData.transcript} onSeek={handleSeek} />
              ) : (
                <ChatQA
                  videoId={videoData.video_id}
                  videoTitle={videoData.title}
                  transcript={videoData.transcript}
                  onSeek={handleSeek}
                />
              )}
            </section>
          </div>
        )}
      </main>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#181818] border border-[#2e2e2e] rounded-2xl p-6 sm:p-8 max-w-md w-full text-center space-y-4 shadow-2xl">
            <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <h3 className="text-lg font-bold text-white">영상 분석 중</h3>
            <p className="text-sm text-neutral-400 leading-relaxed">{loadingStatus}</p>
          </div>
        </div>
      )}
    </div>
  );
}
