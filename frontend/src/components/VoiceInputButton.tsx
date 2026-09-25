import { useState, useEffect, useRef } from 'react';
import { Mic, Square } from 'lucide-react';

interface VoiceInputButtonProps {
  onInterimResult: (text: string) => void;
  onFinalResult: (text: string) => void;
  disabled?: boolean;
}

export function VoiceInputButton({ onInterimResult, onFinalResult, disabled }: VoiceInputButtonProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef<boolean>(false);
  const restartTimerRef = useRef<any>(null);
  const callbacksRef = useRef({ onInterimResult, onFinalResult });

  useEffect(() => {
    callbacksRef.current = { onInterimResult, onFinalResult };
  });

  const createAndStartRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      return null;
    }

    // Clean up any existing instance
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;
        recognitionRef.current.abort();
      } catch (e) {
        // ignore
      }
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = navigator.language || 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const item = event.results[i];
        if (item && item[0]) {
          const text = item[0].transcript || '';
          if (item.isFinal) {
            final += text + ' ';
          } else {
            interim += text;
          }
        }
      }

      if (final.trim()) {
        callbacksRef.current.onFinalResult(final.trim());
      }
      callbacksRef.current.onInterimResult(interim);
    };

    recognition.onerror = (event: any) => {
      console.warn('SpeechRecognition notice:', event.error);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        isListeningRef.current = false;
        setIsListening(false);
        onInterimResult('');
        setErrorMsg('Microphone access denied');
        setTimeout(() => setErrorMsg(null), 4000);
      }
      // 'no-speech' or silence transitions will naturally trigger onend and auto-restart seamlessly
    };

    recognition.onend = () => {
      if (isListeningRef.current) {
        // Multi-sentence / paragraph dictation: auto-restart new session seamlessly across silence pauses
        clearTimeout(restartTimerRef.current);
        restartTimerRef.current = setTimeout(() => {
          if (isListeningRef.current) {
            createAndStartRecognition();
          }
        }, 60);
      } else {
        setIsListening(false);
        onInterimResult('');
      }
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
      return recognition;
    } catch (err) {
      console.warn('Recognition start caught error:', err);
      return null;
    }
  };

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
    }

    return () => {
      isListeningRef.current = false;
      clearTimeout(restartTimerRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {
          // ignore
        }
      }
    };
  }, []);

  const toggleListening = () => {
    clearTimeout(restartTimerRef.current);
    if (isListeningRef.current) {
      isListeningRef.current = false;
      setIsListening(false);
      onInterimResult('');
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // ignore
        }
      }
    } else {
      setErrorMsg(null);
      isListeningRef.current = true;
      setIsListening(true);
      createAndStartRecognition();
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
        title={isListening ? "Stop listening" : "Start continuous voice input"}
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
