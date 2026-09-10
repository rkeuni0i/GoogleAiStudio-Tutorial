import React, { useState } from 'react';

/**
 * 상단 헤더 컴포넌트
 * 기획안 요구사항: 마이크, 만들기(+), 알림 아이콘 완전 제거
 */
export default function Header({ onSearch, isLoading }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim() && !isLoading) {
      onSearch(url.trim());
    }
  };

  const handleClear = () => {
    setUrl('');
  };

  return (
    <header className="sticky top-0 z-40 bg-[#0f0f0f] border-b border-[#272727] px-4 py-2.5 flex items-center justify-between">
      {/* Left: Logo */}
      <div className="flex items-center gap-4 shrink-0">
        <button className="p-2 hover:bg-[#272727] rounded-full text-neutral-300 transition-colors">
          <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
        <div className="flex items-center gap-1.5 cursor-pointer">
          <div className="w-8 h-6 bg-[#ff0000] rounded-lg flex items-center justify-center text-white shadow-sm">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          <div className="flex items-baseline">
            <span className="text-lg font-bold tracking-tighter text-white">YouTube</span>
            <span className="ml-1 text-[11px] font-semibold text-neutral-400">AI Searcher</span>
          </div>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="flex-1 max-w-2xl mx-4">
        <form onSubmit={handleSubmit} className="flex items-center w-full">
          <div className="relative flex-1 flex items-center">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="유튜브 영상 주소(URL)를 입력하세요 (예: https://youtu.be/...)"
              required
              className="w-full bg-[#121212] border border-[#303030] focus:border-[#1c62b9] rounded-l-full py-2.5 pl-5 pr-10 text-sm text-[#f1f1f1] placeholder-neutral-500 outline-none transition-colors"
            />
            {url && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute right-3 text-neutral-400 hover:text-white p-1"
              >
                <svg className="w-4 h-4 stroke-current" viewBox="0 0 24 24" fill="none" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            )}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="bg-[#222222] hover:bg-[#272727] border border-l-0 border-[#303030] rounded-r-full px-6 py-2.5 flex items-center justify-center text-neutral-300 hover:text-white transition-colors disabled:opacity-50"
            title="검색 및 분석"
          >
            <svg className="w-5 h-5 stroke-current" viewBox="0 0 24 24" fill="none" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.3-4.3"/>
            </svg>
          </button>
        </form>
      </div>

      {/* Right: Minimal Status (마이크, 만들기, 알림 제거됨) */}
      <div className="flex items-center gap-3 shrink-0">
        <div className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 bg-[#1f1f1f] border border-[#333333] rounded-full text-xs text-neutral-300 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Gemini 3.8 Flash Ready</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-red-700 flex items-center justify-center text-xs font-bold text-white shadow">
          AI
        </div>
      </div>
    </header>
  );
}
