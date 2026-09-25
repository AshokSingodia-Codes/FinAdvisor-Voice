import { useState, useEffect, useRef } from 'react';
import { Mic, Square } from 'lucide-react';

interface VoiceInputButtonProps {
  onInterimResult: (text: string) => void;
  onFinalResult: (text: string) => void;
  disabled?: boolean;
}

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export function VoiceInputButton({ onInterimResult, onFinalResult, disabled }: VoiceInputButtonProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = navigator.language || 'en-US';

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      if (final) {
        onFinalResult(final);
      }
      onInterimResult(interim);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
      onInterimResult(''); // clear interim on error
      if (event.error === 'not-allowed') {
        setErrorMsg('Microphone access denied');
        setTimeout(() => setErrorMsg(null), 3000);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      onInterimResult('');
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onInterimResult, onFinalResult]);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      onInterimResult('');
    } else {
      setErrorMsg(null);
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (err) {
        console.error('Failed to start recognition', err);
      }
    }
  };

  if (!isSupported) {
    return (
      <button
        type="button"
        disabled
        title="Voice input not supported in this browser"
        className="p-2 rounded-lg text-textDim/40 bg-transparent cursor-not-allowed"
      >
        <Mic size={16} />
      </button>
    );
  }

  return (
    <div className="relative flex items-center justify-center">
      {errorMsg && (
        <div className="absolute -top-10 right-0 bg-red-500/10 text-red-400 text-[11px] px-2.5 py-1 rounded-md border border-red-500/20 whitespace-nowrap shadow-sm backdrop-blur-md">
          {errorMsg}
        </div>
      )}

      {isListening && (
        <>
          <span className="absolute w-[140%] h-[140%] rounded-full bg-red-500/20 animate-ping"></span>
          <span className="absolute w-[180%] h-[180%] rounded-full border border-red-500/40 animate-[ping_1.5s_ease-out_infinite]"></span>
        </>
      )}

      <button
        type="button"
        onClick={toggleListening}
        disabled={disabled}
        title={isListening ? "Stop listening" : "Start voice input"}
        className={`relative z-10 p-2 rounded-lg transition-all shadow-xs cursor-pointer flex items-center justify-center ${isListening
            ? 'bg-red-500/90 text-white hover:bg-red-600 shadow-[0_0_12px_rgba(239,68,68,0.5)]'
            : 'bg-slate-100 text-[#0f274a] hover:bg-blue-50 hover:text-blue-700 border border-slate-200 disabled:opacity-40 disabled:hover:bg-slate-100 disabled:hover:text-[#0f274a]'
          }`}
      >
        {isListening ? <Square size={14} className="fill-current" /> : <Mic size={16} />}
      </button>
    </div>
  );
}
