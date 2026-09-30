import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User as UserIcon, Sparkles, Volume2, VolumeX, Check, Copy } from 'lucide-react';

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  steps?: string[];
  isError?: boolean;
}

interface ChatMessageItemProps {
  msg: ChatMessage;
  index: number;
  isSpeaking: boolean;
  isCopied: boolean;
  onToggleTTS: (content: string, index: number) => void;
  onCopy: (content: string, index: number) => void;
  onSendAction: (actionText: string) => void;
  loading: boolean;
}

export const ChatMessageItem = React.memo(function ChatMessageItem({
  msg,
  index,
  isSpeaking,
  isCopied,
  onToggleTTS,
  onCopy,
  onSendAction,
  loading
}: ChatMessageItemProps) {
  // Extract interactive next-step action chips once per message content change
  const suggestions = useMemo(() => {
    if (msg.role !== 'assistant' || !msg.content) return [];
    const items: string[] = [];
    const regex = /\[([A-Za-z0-9\s₹$,%.\-/?!]{4,50})\]/g;
    let match;
    while ((match = regex.exec(msg.content)) !== null) {
      const act = match[1].trim();
      if (act && !items.includes(act) && !act.toLowerCase().startsWith('action')) {
        items.push(act);
      }
    }
    return items.slice(0, 3);
  }, [msg.content, msg.role]);

  return (
    <div className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      {msg.role === 'assistant' && (
        <div className="w-8 h-8 rounded-lg bg-[#0f274a] text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
          <Bot size={18} />
        </div>
      )}

      <div
        className={`rounded-2xl px-5 py-4 text-[14.5px] leading-relaxed select-text ${
          msg.role === 'user'
            ? 'max-w-[80%] bg-[#0f274a] text-white rounded-tr-sm shadow-md font-normal'
            : 'w-full max-w-full bg-[#f8fafc] border border-slate-200/90 text-slate-900 rounded-tl-sm shadow-xs'
        }`}
      >
        {msg.role === 'user' ? (
          <div className="whitespace-pre-wrap">{msg.content}</div>
        ) : (
          <div className="prose max-w-none text-slate-900 leading-relaxed space-y-2.5">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => (
                  <h1 className="text-lg font-bold text-slate-900 mt-3 mb-2 pb-1 border-b border-slate-200">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-base font-bold text-blue-900 mt-3 mb-1.5">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm font-semibold text-blue-800 mt-2 mb-1">{children}</h3>
                ),
                p: ({ children }) => <p className="mb-2 leading-relaxed text-slate-800">{children}</p>,
                ul: ({ children }) => (
                  <ul className="list-disc pl-5 mb-2.5 space-y-1 text-slate-800">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-5 mb-2.5 space-y-1 text-slate-800">{children}</ol>
                ),
                li: ({ children }) => <li className="text-slate-800">{children}</li>,
                hr: () => <hr className="border-slate-200 my-3" />,
                strong: ({ children }) => (
                  <strong className="font-bold text-slate-950">{children}</strong>
                ),
                code: ({ children }) => (
                  <code className="bg-blue-50 text-blue-900 border border-blue-200 px-1.5 py-0.5 rounded text-xs font-mono font-semibold">
                    {children}
                  </code>
                ),
                table: ({ children }) => (
                  <div className="my-3 overflow-x-auto rounded-xl border border-slate-200 shadow-xs">
                    <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-slate-100 text-blue-950 font-bold border-b border-slate-200">
                    {children}
                  </thead>
                ),
                tbody: ({ children }) => (
                  <tbody className="divide-y divide-slate-100 bg-white">{children}</tbody>
                ),
                tr: ({ children }) => <tr className="hover:bg-slate-50 transition-colors">{children}</tr>,
                th: ({ children }) => (
                  <th className="px-3.5 py-2.5 text-[11px] uppercase tracking-wider font-bold text-blue-950">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-3.5 py-2.5 text-xs text-slate-800 whitespace-normal">
                    {children}
                  </td>
                ),
              }}
            >
              {msg.content}
            </ReactMarkdown>

            {/* Interactive Next-Step Action Chips */}
            {suggestions.length > 0 && (
              <div className="mt-3 pt-2.5 border-t border-slate-200">
                <div className="text-[11px] font-bold text-blue-900 mb-2 flex items-center gap-1">
                  <Sparkles size={12} className="text-blue-700" />
                  <span>Suggested Next Actions:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((actionText, actIdx) => (
                    <button
                      key={actIdx}
                      onClick={() => onSendAction(actionText)}
                      disabled={loading}
                      className="flex items-center gap-1.5 text-xs bg-blue-50 hover:bg-blue-100 text-blue-900 font-semibold border border-blue-200 hover:border-blue-400 px-3 py-1.5 rounded-xl transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50"
                    >
                      <span>{actionText}</span>
                      <span className="text-[10px] opacity-70">→</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Assistant Message Actions (Copy & Voice TTS) */}
            <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-200 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-500 font-semibold flex items-center gap-1">
                  <Sparkles size={12} className="text-blue-700" />
                  FinAdvisor-X Analysis
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => onToggleTTS(msg.content, index)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    isSpeaking
                      ? 'bg-blue-100 text-blue-900 border border-blue-300 animate-pulse'
                      : 'bg-white hover:bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200'
                  }`}
                  title={isSpeaking ? 'Stop Speaking' : 'Read Aloud'}
                >
                  {isSpeaking ? <VolumeX size={13} className="text-blue-800" /> : <Volume2 size={13} />}
                  <span>{isSpeaking ? 'Stop' : 'Listen'}</span>
                </button>

                <button
                  onClick={() => onCopy(msg.content, index)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    isCopied
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-white hover:bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200'
                  }`}
                  title="Copy Answer to Clipboard"
                >
                  {isCopied ? <Check size={13} className="text-emerald-700" /> : <Copy size={13} />}
                  <span>{isCopied ? 'Copied!' : 'Copy'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {msg.role === 'user' && (
        <div className="w-8 h-8 rounded-full bg-[#0f274a] text-white flex items-center justify-center shrink-0 text-xs font-bold shadow-xs mt-1">
          <UserIcon size={14} />
        </div>
      )}
    </div>
  );
});
