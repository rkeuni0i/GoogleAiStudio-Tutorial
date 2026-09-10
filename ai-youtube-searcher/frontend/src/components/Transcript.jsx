import React from 'react';

/**
 * 타임스탬프 기반 자막 목록 컴포넌트
 * @param {Array} transcript - [{ start_time: "00:05", seconds: 5, text: "..." }]
 * @param {Function} onSeek - 특정 타임스탬프(초)로 이동하여 재생하는 콜백
 */
export default function Transcript({ transcript, onSeek }) {
  if (!transcript || transcript.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-neutral-500 text-sm">
        <svg className="w-10 h-10 mb-2 stroke-current opacity-40" viewBox="0 0 24 24" fill="none" strokeWidth="1.5">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <p>추출된 자막이 없습니다.</p>
        <p className="text-xs text-neutral-600 mt-1">영상을 먼저 검색하여 분석해 주세요.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden p-3 sm:p-4">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#272727] text-xs text-neutral-400">
        <span>타임스탬프를 클릭하면 해당 위치로 이동합니다</span>
        <span className="font-mono text-neutral-500">총 {transcript.length}개 구간</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
        {transcript.map((item, index) => (
          <div
            key={index}
            onClick={() => onSeek && onSeek(item.seconds)}
            className="group flex items-start gap-3 p-2.5 rounded-lg hover:bg-neutral-800 transition-colors cursor-pointer border border-transparent hover:border-neutral-700"
          >
            <button
              type="button"
              className="shrink-0 px-2 py-0.5 bg-neutral-800 group-hover:bg-red-600 text-red-500 group-hover:text-white rounded text-xs font-mono font-medium transition-colors"
            >
              {item.start_time}
            </button>
            <p className="text-sm text-neutral-200 leading-snug group-hover:text-white select-text">
              {item.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
