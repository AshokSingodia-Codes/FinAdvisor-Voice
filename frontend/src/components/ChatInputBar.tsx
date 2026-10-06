import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Send, Paperclip, Upload, X, AlertTriangle, FileText } from 'lucide-react';
import { VoiceInputButton } from './VoiceInputButton';

export interface ActiveDocument {
  id: string;
  filename: string;
  chunk_count: number;
  file_size_bytes: number;
}

interface ChatInputBarProps {
  onSend: (text: string) => void;
  loading: boolean;
  uploadLoading: boolean;
  activeDoc: ActiveDocument | null;
  onUploadFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onDetachDoc: () => void;
  isAuthenticated: boolean;
  rateLimitSeconds: number | null;
  onClearRateLimit: () => void;
}

export const ChatInputBar = React.memo(function ChatInputBar({
  onSend,
  loading,
  uploadLoading,
  activeDoc,
  onUploadFile,
  onDetachDoc,
  isAuthenticated,
  rateLimitSeconds,
  onClearRateLimit,
}: ChatInputBarProps) {
  const [input, setInput] = useState('');
  const [interimVoice, setInterimVoice] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea smoothly without layout shifts
  const adjustTextareaHeight = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (interimVoice) setInterimVoice('');
    adjustTextareaHeight();
  };

  const handleVoiceInterim = useCallback((text: string) => {
    setInterimVoice(text);
  }, []);

  const handleVoiceFinal = useCallback((text: string) => {
    setInput((prev) => {
      const trimmedPrev = prev.trim();
      return trimmedPrev ? `${trimmedPrev} ${text}` : text;
    });
    setInterimVoice('');
    setTimeout(adjustTextareaHeight, 0);
  }, [adjustTextareaHeight]);

  const handleSubmit = useCallback(() => {
    const combined = (input + (interimVoice ? (input ? ' ' : '') + interimVoice : '')).trim();
    if (!combined || loading) return;

    onSend(combined);
    setInput('');
    setInterimVoice('');

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [input, interimVoice, loading, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Reset input field height on clear
  useEffect(() => {
    if (!input && textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [input]);

  const displayValue = interimVoice ? `${input}${input && !input.endsWith(' ') ? ' ' : ''}${interimVoice}` : input;
  const isSendDisabled = loading || (!input.trim() && !interimVoice.trim());

  return (
    <div className="border-t border-slate-200/90 bg-white pt-3 pb-3 px-4 sm:px-6 z-10">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.md,.csv,text/plain,text/markdown,application/pdf"
        className="hidden"
        onChange={onUploadFile}
      />

      {/* Rate-limit toast */}
      {rateLimitSeconds !== null && rateLimitSeconds > 0 && (
        <div className="max-w-4xl mx-auto mb-2 flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-900 rounded-xl px-4 py-2 text-xs font-medium animate-pulse">
          <AlertTriangle size={14} className="shrink-0 text-amber-700" />
          <span>
            Rate limit reached. You can send another message in <strong>{rateLimitSeconds}s</strong>.
          </span>
          <button onClick={onClearRateLimit} className="ml-auto text-amber-700 hover:text-amber-900 cursor-pointer">
            <X size={13} />
          </button>
        </div>
      )}

      {/* Active document chip + disclaimer banner */}
      {activeDoc && (
        <div className="max-w-4xl mx-auto mb-2 space-y-1.5">
          {/* Document chip */}
          <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-xl px-3 py-1.5 text-xs text-blue-950">
            <FileText size={13} className="text-blue-800 shrink-0" />
            <span className="text-blue-950 font-semibold truncate max-w-[260px]" title={activeDoc.filename}>
              {activeDoc.filename}
            </span>
            <span className="text-slate-500 font-mono shrink-0">
              {activeDoc.chunk_count} chunks · {(activeDoc.file_size_bytes / 1024).toFixed(0)} KB
            </span>
            <button
              onClick={onDetachDoc}
              title="Detach & delete document"
              className="ml-auto p-0.5 text-slate-400 hover:text-red-600 transition-colors rounded cursor-pointer shrink-0"
            >
              <X size={13} />
            </button>
          </div>
          {/* Disclaimer */}
          <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-3 py-1.5 text-[10px] text-amber-900 leading-relaxed">
            <AlertTriangle size={11} className="shrink-0 mt-0.5 text-amber-700" />
            <span>
              <strong className="font-semibold text-amber-950">Personal document mode active.</strong> Responses are
              based on your uploaded document. This is general guidance — not formal RIA advisory.
            </span>
          </div>
        </div>
      )}

      {/* Input container */}
      <div className="max-w-4xl mx-auto relative flex items-end bg-white border border-slate-300 rounded-xl focus-within:border-[#0f274a] focus-within:ring-2 focus-within:ring-[#0f274a]/15 shadow-xs transition-all overflow-visible p-1.5">
        <textarea
          ref={textareaRef}
          rows={1}
          value={displayValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          disabled={loading}
          placeholder={
            isAuthenticated
              ? 'Ask for financial advice, stock updates, budgeting, or return calculations...'
              : 'Please sign in to start asking questions...'
          }
          className="flex-1 bg-transparent pl-3 pr-2 py-2 text-slate-900 text-sm focus:outline-none placeholder:text-slate-400 disabled:opacity-50 resize-none min-h-[38px] max-h-36 overflow-y-auto leading-relaxed"
        />

        {interimVoice && (
          <span className="absolute left-5 -top-6 text-[10px] text-blue-900 font-semibold bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-md shadow-xs flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
            Listening continuously...
          </span>
        )}

        <div className="flex items-center gap-1.5 pr-1 pb-1 shrink-0 relative">
          {/* Upload document button */}
          {isAuthenticated && (
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || uploadLoading}
              title={
                uploadLoading
                  ? 'Uploading...'
                  : activeDoc
                  ? `Active: ${activeDoc.filename} — click to replace`
                  : 'Attach a financial document (PDF / TXT / MD, max 5 MB)'
              }
              className={`p-2 rounded-lg transition-all shadow-xs cursor-pointer z-10 relative ${
                activeDoc
                  ? 'bg-blue-100 text-blue-900 hover:bg-blue-200'
                  : 'bg-slate-100 text-[#0f274a] hover:bg-blue-50 hover:text-blue-800 border border-slate-200'
              } disabled:opacity-40 disabled:cursor-not-allowed`}
            >
              {uploadLoading ? (
                <Upload size={16} className="animate-bounce text-blue-800" />
              ) : (
                <Paperclip size={16} />
              )}
            </button>
          )}

          <VoiceInputButton
            disabled={loading}
            onInterimResult={handleVoiceInterim}
            onFinalResult={handleVoiceFinal}
          />

          <button
            onClick={handleSubmit}
            disabled={isSendDisabled}
            className="p-2 rounded-lg bg-[#0f274a] hover:bg-[#163a6f] text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm cursor-pointer z-10 relative flex items-center justify-center"
            title="Send Message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
      <div className="text-center mt-2 text-[11px] text-slate-500">
        FinAdvisor-X is an AI financial assistant. Always verify critical decisions with a licensed advisor.
      </div>
    </div>
  );
});
