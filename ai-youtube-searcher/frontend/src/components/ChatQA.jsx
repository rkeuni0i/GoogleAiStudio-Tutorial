import React, { useState } from 'react';

/**
 * Gemini 3.8 Flash 기반 AI Q&A 채팅 컴포넌트
 */
export default function ChatQA({ videoId, videoTitle, transcript, onSeek }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: '💡 <strong>AI Q&A 가이드:</strong><br>"이 영상에서 핵심 내용이 뭐야?", "XX를 설명하는 부분이 어디야?" 처럼 질문하시면, Gemini가 답변과 함께 <strong>해당 시점으로 영상을 자동 이동 및 재생</strong>합니다!'
    }
  ]);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || isLoading) return;

    // 사용자 메시지 추가
    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_id: videoId,
          question: q,
          video_title: videoTitle,
          transcript: transcript
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || '답변 생성 실패');
      }

      const data = await response.json();
      
      // AI 응답 추가
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: data.answer,
          target_seconds: data.target_seconds,
          timestamp_str: data.timestamp_str
        }
      ]);

      // 타임스탬프가 있으면 자동 영상 이동 및 재생!
      if (data.target_seconds && data.target_seconds > 0 && onSeek) {
        onSeek(data.target_seconds);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `⚠️ 오류가 발생했습니다: ${err.message}`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-3.5 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-red-600 text-white rounded-br-none'
                  : 'bg-neutral-800 text-neutral-100 rounded-bl-none border border-neutral-700'
              }`}
            >
              <div dangerouslySetInnerHTML={{ __html: msg.text }} />

              {msg.target_seconds && msg.target_seconds > 0 && (
                <div className="mt-3 pt-2.5 border-t border-neutral-700 flex items-center justify-between">
                  <span className="text-xs text-neutral-400">영상 타임라인</span>
                  <button
                    onClick={() => onSeek && onSeek(msg.target_seconds)}
                    className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-full shadow transition-all"
                  >
                    <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                    <span>{msg.timestamp_str || `${msg.target_seconds}초`} 위치 재생</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-neutral-800 border border-neutral-700 rounded-2xl p-3.5 text-sm text-neutral-400 animate-pulse">
              Gemini AI가 자막을 분석하여 관련 구간을 탐색 중입니다...
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="p-3 bg-[#141414] border-t border-[#272727]">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="예: 'XX 내용 나오는 곳 찾아줘', '핵심 요약해줘'"
            required
            className="flex-1 bg-[#1e1e1e] border border-[#333333] focus:border-red-600 rounded-xl px-4 py-2.5 text-sm text-white placeholder-neutral-500 outline-none transition-colors"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="p-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl transition-colors shrink-0 disabled:opacity-50"
            title="질문 전송"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
