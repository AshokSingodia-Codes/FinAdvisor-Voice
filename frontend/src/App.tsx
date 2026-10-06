import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  TrendingUp,
  DollarSign,
  Activity,
  Plus,
  Menu,
  Bot,
  User as UserIcon,
  Shield,
  Clock,
  LogOut,
  LogIn,
  UserPlus,
  X,
  Sparkles
} from 'lucide-react';
import { useAuth } from './context/AuthContext';
import { AuthModal } from './components/AuthModal';
import { LoginPage } from './components/LoginPage';
import { ChatMessageItem } from './components/ChatMessageItem';
import type { ChatMessage } from './components/ChatMessageItem';
import { ConversationSidebarItem } from './components/ConversationSidebarItem';
import type { ConversationItem } from './components/ConversationSidebarItem';
import { ChatInputBar } from './components/ChatInputBar';
import type { ActiveDocument } from './components/ChatInputBar';
import { API_BASE } from './config';

function App() {
  const {
    user,
    isAuthenticated,
    isLoading,
    authFetch,
    logout,
    isAuthModalOpen,
    authModalInitialTab,
    openAuthModal,
    closeAuthModal
  } = useAuth();

  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConvId, setActiveConvId] = useState<string>(() => {
    return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
  });
  const [activeTitle, setActiveTitle] = useState<string>('New Chat');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Document upload state
  const [activeDoc, setActiveDoc] = useState<ActiveDocument | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  // Rate limit toast
  const [rateLimitSeconds, setRateLimitSeconds] = useState<number | null>(null);
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editTitleInput, setEditTitleInput] = useState('');

  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [speakingIndex, setSpeakingIndex] = useState<number | null>(null);

  // Refs for stable callbacks without triggering re-renders
  const messagesRef = useRef<ChatMessage[]>(messages);
  messagesRef.current = messages;

  const activeConvIdRef = useRef<string>(activeConvId);
  activeConvIdRef.current = activeConvId;

  const activeDocRef = useRef<ActiveDocument | null>(activeDoc);
  activeDocRef.current = activeDoc;

  const isAuthenticatedRef = useRef<boolean>(isAuthenticated);
  isAuthenticatedRef.current = isAuthenticated;

  const isSendingRef = useRef<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleCopyMessage = useCallback((content: string, index: number) => {
    if (!navigator.clipboard) {
      const textArea = document.createElement("textarea");
      textArea.value = content;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
    } else {
      navigator.clipboard.writeText(content);
    }
    setCopiedIndex(index);
    setTimeout(() => {
      setCopiedIndex((prev) => (prev === index ? null : prev));
    }, 2000);
  }, []);

  // Soft female voice selection helper
  const getSoftFemaleVoice = useCallback((): SpeechSynthesisVoice | null => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    const maleKeywords = [
      'david', 'mark', 'george', 'ravi', 'guy', 'ryan', 'stefan', 'richard',
      'male', ' man', ' boy', 'daniel', 'oliver', 'thomas', 'james', 'alex',
      'fred', 'junior', 'ralph', 'albert', 'bruce', 'steve', 'tom', 'paul',
      'sean', 'cosmo', 'reed', 'eric', 'andrew', 'christopher', 'brian'
    ];

    const isMaleVoice = (v: SpeechSynthesisVoice) => {
      const name = v.name.toLowerCase();
      return maleKeywords.some(kw => name.includes(kw));
    };

    const prioritizedFemaleKeywords = [
      'zira', 'aria', 'jenny', 'neerja', 'swara', 'heera', 'samantha', 'karen',
      'serena', 'victoria', 'hazel', 'susan', 'veena', 'catherine', 'eva', 'ava',
      'emma', 'olivia', 'mia', 'chloe', 'female', 'woman'
    ];

    for (const kw of prioritizedFemaleKeywords) {
      const match = voices.find(v => !isMaleVoice(v) && v.name.toLowerCase().includes(kw));
      if (match) return match;
    }

    const nonMaleVoices = voices.filter(v => !isMaleVoice(v));
    const englishNonMale = nonMaleVoices.find(v => 
      v.lang.startsWith('en') || v.lang.startsWith('hi')
    );
    if (englishNonMale) return englishNonMale;

    if (nonMaleVoices.length > 0) return nonMaleVoices[0];
    return voices[0] || null;
  }, []);

  const handleToggleTTS = useCallback((content: string, index: number) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }

    window.speechSynthesis.cancel();
    const cleanText = content
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/\|.*?\|/g, ' ')
      .replace(/[#*_`~>-]/g, '')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    const femaleVoice = getSoftFemaleVoice();
    if (femaleVoice) {
      utterance.voice = femaleVoice;
    }

    utterance.rate = 0.95;
    utterance.pitch = 1.15;
    utterance.volume = 1.0;

    utterance.onend = () => setSpeakingIndex(null);
    utterance.onerror = () => setSpeakingIndex(null);

    setSpeakingIndex(index);
    window.speechSynthesis.speak(utterance);
  }, [speakingIndex, getSoftFemaleVoice]);

  // Stop speech synthesis on conv change
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.getVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => {
          window.speechSynthesis.getVoices();
        };
      }
      window.speechSynthesis.cancel();
    }
    setSpeakingIndex(null);
  }, [activeConvId]);

  // Reset rate-limit state when user changes
  useEffect(() => {
    setRateLimitSeconds(null);
  }, [user?.id]);

  // Count down the rate-limit toast automatically
  useEffect(() => {
    if (rateLimitSeconds === null || rateLimitSeconds <= 0) return;
    const timer = setTimeout(() => setRateLimitSeconds(s => (s !== null ? s - 1 : null)), 1000);
    return () => clearTimeout(timer);
  }, [rateLimitSeconds]);

  // Detach document automatically when switching conversations
  useEffect(() => {
    setActiveDoc(null);
  }, [activeConvId]);

  // Load conversations list
  const fetchConversations = useCallback(async () => {
    if (!isAuthenticatedRef.current) {
      setConversations([]);
      return [];
    }
    try {
      const res = await authFetch(`${API_BASE}/api/conversations`);
      if (res.ok) {
        const data: ConversationItem[] = await res.json();
        setConversations(data);
        return data;
      }
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    }
    return [];
  }, [authFetch]);

  // Load single conversation messages
  const loadConversation = useCallback(async (convId: string) => {
    if (!isAuthenticatedRef.current) return;
    try {
      const res = await authFetch(`${API_BASE}/api/conversations/${convId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveConvId(data.id);
        setActiveTitle(data.title || 'New Chat');
        setMessages(data.messages || []);
      } else {
        setActiveConvId(convId);
        setActiveTitle('New Chat');
        setMessages([]);
      }
    } catch (err) {
      console.error(`Failed to load conversation ${convId}:`, err);
      setActiveConvId(convId);
      setActiveTitle('New Chat');
      setMessages([]);
    }
  }, [authFetch]);

  const handleNewChat = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    isSendingRef.current = false;
    setLoading(false);

    const newId = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
    setActiveConvId(newId);
    setActiveTitle('New Chat');
    setMessages([]);
    setActiveDoc(null);
    setIsSidebarOpen(false);
  }, []);

  // When auth changes (user signs in or out), load conversations
  useEffect(() => {
    const init = async () => {
      if (isAuthenticated) {
        const convs = await fetchConversations();
        if (convs && convs.length > 0) {
          await loadConversation(convs[0].id);
        } else {
          handleNewChat();
        }
      } else {
        setConversations([]);
        setMessages([]);
        handleNewChat();
      }
    };
    init();
  }, [isAuthenticated, fetchConversations, loadConversation, handleNewChat]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  const handleSelectConversation = useCallback(async (convId: string) => {
    setIsSidebarOpen(false);
    if (convId === activeConvIdRef.current) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    isSendingRef.current = false;
    setLoading(false);

    await loadConversation(convId);
  }, [loadConversation]);

  const handleDeleteConversation = useCallback(async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this conversation?')) return;
    try {
      const res = await authFetch(`${API_BASE}/api/conversations/${convId}`, { method: 'DELETE' });
      if (res.ok) {
        setConversations(prev => {
          const updated = prev.filter(c => c.id !== convId);
          if (activeConvIdRef.current === convId) {
            if (updated.length > 0) {
              loadConversation(updated[0].id);
            } else {
              handleNewChat();
            }
          }
          return updated;
        });
      } else {
        alert('Failed to delete conversation.');
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      alert('Error deleting conversation.');
    }
  }, [authFetch, loadConversation, handleNewChat]);

  const handleClearAllConversations = useCallback(async () => {
    if (!window.confirm('Are you sure you want to delete ALL conversations? This cannot be undone.')) return;
    try {
      const res = await authFetch(`${API_BASE}/api/conversations`, { method: 'DELETE' });
      if (res.ok) {
        setConversations([]);
        handleNewChat();
      } else {
        alert('Failed to clear conversations.');
      }
    } catch (err) {
      console.error('Failed to clear conversations:', err);
      alert('Error clearing conversations.');
    }
  }, [authFetch, handleNewChat]);

  const startRename = useCallback((e: React.MouseEvent, conv: ConversationItem) => {
    e.stopPropagation();
    setEditingConvId(conv.id);
    setEditTitleInput(conv.title);
  }, []);

  const handleCancelRename = useCallback((e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setEditingConvId(null);
  }, []);

  const handleSaveRename = useCallback(async (e: React.MouseEvent | React.KeyboardEvent, convId: string) => {
    e.stopPropagation();
    const trimmed = editTitleInput.trim();
    if (!trimmed) {
      setEditingConvId(null);
      return;
    }
    try {
      const res = await authFetch(`${API_BASE}/api/conversations/${convId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: trimmed })
      });
      if (res.ok) {
        setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: trimmed } : c));
        if (activeConvIdRef.current === convId) {
          setActiveTitle(trimmed);
        }
      }
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    } finally {
      setEditingConvId(null);
    }
  }, [editTitleInput, authFetch]);

  // Main Non-blocking Send Handler with Timeout & Cancellation
  const handleSend = useCallback(async (textToSend: string) => {
    if (!isAuthenticatedRef.current) {
      openAuthModal('signin');
      return;
    }

    const userMsg = textToSend.trim();
    if (!userMsg || isSendingRef.current) return;

    isSendingRef.current = true;
    const currentMessages = messagesRef.current;
    const newMessages: ChatMessage[] = [...currentMessages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setLoading(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

    try {
      const targetConvId = activeConvIdRef.current;
      const targetDocId = activeDocRef.current?.id ?? null;

      const response = await authFetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          conversation_id: targetConvId,
          chat_history: currentMessages,
          document_id: targetDocId,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 429) {
        const err = await response.json().catch(() => ({}));
        const retryAfter = err?.detail?.retry_after_seconds ?? 60;
        setRateLimitSeconds(retryAfter);
        setMessages([...newMessages, {
          role: 'assistant',
          content: `⚠️ Rate limit reached. Please wait ${retryAfter} seconds before sending another message.`,
          isError: true,
        }]);
        return;
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Network response was not ok');
      }

      const data = await response.json();

      setMessages([...newMessages, { role: 'assistant', content: data.answer }]);

      if (data.title) {
        setActiveTitle(data.title);
      }

      // Refresh sidebar conversations in background without blocking UI
      fetchConversations();
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        setMessages([
          ...newMessages,
          { role: 'assistant', content: '⏱️ Request timed out. The server is taking longer than usual to respond. Please try asking again.', isError: true }
        ]);
      } else {
        console.error('Error fetching chat response:', error);
        setMessages([
          ...newMessages,
          { role: 'assistant', content: 'Sorry, I encountered an error while processing your request. Please check your connection and try again.', isError: true }
        ]);
      }
    } finally {
      isSendingRef.current = false;
      abortControllerRef.current = null;
      setLoading(false);
    }
  }, [authFetch, openAuthModal, fetchConversations]);

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !isAuthenticatedRef.current) return;

    setUploadLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('conversation_id', activeConvIdRef.current);

      const res = await authFetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (res.status === 413) {
        alert('File too large. Maximum size is 5 MB.');
        return;
      }
      if (res.status === 415) {
        alert('Unsupported file type. Please upload a PDF, plain text, or markdown file.');
        return;
      }
      if (res.status === 422) {
        const err = await res.json().catch(() => ({}));
        const detailMsg = err?.detail || 'The uploaded document is not related to finance and was not added to the system.';
        alert(`⚠️ Non-Financial Document Rejected\n\n${detailMsg}`);
        return;
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alert(`Upload failed: ${err?.detail ?? res.statusText}`);
        return;
      }

      const data = await res.json();
      setActiveDoc({
        id: data.document_id,
        filename: file.name,
        chunk_count: data.chunk_count,
        file_size_bytes: data.file_size_bytes,
      });
    } catch (err) {
      console.error('Upload error:', err);
      alert('Upload failed. Please try again.');
    } finally {
      setUploadLoading(false);
      if (e.target) e.target.value = '';
    }
  }, [authFetch]);

  const handleDetachDoc = useCallback(async () => {
    const doc = activeDocRef.current;
    if (!doc || !isAuthenticatedRef.current) return;
    try {
      await authFetch(
        `${API_BASE}/api/documents/${doc.id}?conversation_id=${encodeURIComponent(activeConvIdRef.current)}`,
        { method: 'DELETE' }
      );
    } catch (err) {
      console.error('Delete doc error:', err);
    } finally {
      setActiveDoc(null);
    }
  }, [authFetch]);

  const handleClearRateLimit = useCallback(() => {
    setRateLimitSeconds(null);
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-bgMain text-textMain">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accentPrimary to-accentHover flex items-center justify-center shadow-lg animate-pulse">
            <TrendingUp size={22} className="text-[#0d0f14]" />
          </div>
          <span className="text-xs text-textDim font-medium animate-pulse">Initializing FinAdvisor-X...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="flex h-screen bg-white text-slate-900 overflow-hidden font-sans select-none">
      {/* Auth Modal Component */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={closeAuthModal}
        initialTab={authModalInitialTab}
      />

      {/* Mobile Drawer Backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 md:hidden transition-opacity duration-300"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-72 bg-[#f8fafc] border-r border-slate-200/90 flex flex-col shrink-0
        transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0 shadow-2xl md:shadow-none' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-200/80 flex items-center justify-between bg-white">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#0f274a] flex items-center justify-center text-xl font-bold shadow-sm text-white">
              <TrendingUp size={20} className="text-white" />
            </div>
            <div>
              <span className="font-bold text-base text-slate-900 tracking-tight">FinAdvisor-X</span>
              <span className="block text-[10px] text-blue-800 font-bold tracking-wider uppercase">AI Financial Analyst</span>
            </div>
          </div>
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="md:hidden p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            title="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={() => {
              if (!isAuthenticated) {
                openAuthModal('signin');
              } else {
                handleNewChat();
              }
            }}
            className="w-full flex items-center justify-center gap-2 bg-[#0f274a] hover:bg-[#163a6f] text-white transition-all duration-200 rounded-xl py-2.5 px-4 text-sm font-semibold shadow-sm cursor-pointer active:scale-[0.98]"
          >
            <Plus size={16} className="stroke-[2.5]" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Recent Chats Section Header */}
        <div className="px-3 pt-2 pb-1">
          <div className="flex items-center justify-between px-2 mb-2">
            <span className="text-[11px] font-bold text-slate-500 tracking-wider uppercase flex items-center gap-1.5">
              <Clock size={12} />
              Recent Chats
            </span>
            <div className="flex items-center gap-2">
              {isAuthenticated && conversations.length > 0 && (
                <button
                  onClick={handleClearAllConversations}
                  className="text-[10px] text-slate-400 hover:text-red-600 hover:underline transition-colors cursor-pointer font-medium"
                  title="Clear all chats"
                >
                  Clear All
                </button>
              )}
              {isAuthenticated && (
                <span className="text-[10px] bg-blue-100/70 text-blue-900 border border-blue-200 px-1.5 py-0.5 rounded-full font-mono font-semibold">
                  {conversations.length}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Chats List */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          {!isAuthenticated ? (
            <div className="text-center py-8 px-4 text-slate-500 text-xs leading-relaxed">
              <p className="mb-3">Sign in to save and sync your chat history securely.</p>
              <button
                onClick={() => openAuthModal('signin')}
                className="inline-flex items-center gap-1.5 text-xs text-blue-800 font-semibold hover:underline cursor-pointer"
              >
                <LogIn size={13} />
                <span>Sign In Now</span>
              </button>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 px-4 text-slate-400 text-xs leading-relaxed">
              No conversations yet.<br />Click <span className="text-blue-800 font-medium">+ New Chat</span> to start!
            </div>
          ) : (
            conversations.map((conv) => (
              <ConversationSidebarItem
                key={conv.id}
                conv={conv}
                isActive={conv.id === activeConvId}
                isEditing={editingConvId === conv.id}
                editTitleInput={editTitleInput}
                onSelect={handleSelectConversation}
                onStartRename={startRename}
                onSaveRename={handleSaveRename}
                onCancelRename={handleCancelRename}
                onEditInputChange={setEditTitleInput}
                onDelete={handleDeleteConversation}
              />
            ))
          )}
        </div>

        {/* User Footer Card */}
        <div className="p-3 border-t border-slate-200/90 bg-white">
          {isAuthenticated && user ? (
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex items-center gap-2.5 min-w-0 flex-1 mr-2">
                <div className="w-8 h-8 rounded-full bg-[#0f274a] flex items-center justify-center font-bold text-white text-xs shadow-xs shrink-0">
                  <UserIcon size={14} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold truncate text-slate-900" title={user.email}>
                    {user.email}
                  </div>
                  <div className="text-[10px] text-blue-800 flex items-center gap-1 font-semibold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Authenticated (JWT)
                  </div>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer shrink-0"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <button
                onClick={() => openAuthModal('signin')}
                className="w-full flex items-center justify-center gap-2 bg-[#0f274a] hover:bg-[#163a6f] text-white font-bold py-2 px-3 rounded-xl text-xs shadow-sm active:scale-[0.98] transition-all cursor-pointer"
              >
                <LogIn size={14} />
                <span>Sign In</span>
              </button>
              <button
                onClick={() => openAuthModal('register')}
                className="w-full flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold py-1.5 px-3 rounded-xl text-xs border border-slate-200 transition-all cursor-pointer"
              >
                <UserPlus size={13} />
                <span>Create New Account</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 relative bg-white">
        {/* Top Navbar */}
        <header className="h-14 border-b border-slate-200/90 flex items-center justify-between px-4 sm:px-6 bg-white sticky top-0 z-10">
          <div className="flex items-center gap-2.5 min-w-0">
            <button
              onClick={() => setIsSidebarOpen(prev => !prev)}
              className="md:hidden p-2 -ml-1 text-slate-600 hover:text-[#0f274a] hover:bg-slate-100 rounded-lg transition-colors cursor-pointer shrink-0"
              title="Toggle Menu"
            >
              <Menu size={20} />
            </button>
            <div className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2 truncate">
              <span className="truncate">{activeTitle}</span>
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-700 bg-slate-100 border border-slate-200 px-3 py-1 rounded-full font-medium">
              <Shield size={13} className="text-blue-800" />
              <span>Isolated Memory</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">Indian Market & RAG Active</span>
              <span className="sm:hidden">RAG Active</span>
            </div>
            {!isAuthenticated && (
              <button
                onClick={() => openAuthModal('signin')}
                className="ml-2 flex items-center gap-1.5 bg-[#0f274a] hover:bg-[#163a6f] text-white px-3.5 py-1 rounded-full text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <LogIn size={13} />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </header>

        {/* Chat Messages Area */}
        <div className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 scroll-smooth bg-white">
          {messages.length === 0 ? (
            <div className="min-h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto px-4 py-8">
              <div className="w-16 h-16 rounded-2xl bg-[#0f274a] text-white flex items-center justify-center mb-6 shadow-md border border-blue-900/20">
                <TrendingUp size={30} className="text-blue-200" />
              </div>
              <h1 className="text-3xl font-bold mb-3 tracking-tight text-slate-900">
                How can I assist your financial journey?
              </h1>
              <p className="text-slate-600 text-sm sm:text-base mb-8 leading-relaxed max-w-lg">
                I maintain conversational memory within this chat to help you plan budgets, analyze stocks, model SIP returns, and evaluate tax strategies.
              </p>

              {!isAuthenticated && (
                <div className="mb-8 p-5 rounded-2xl bg-[#f8fafc] border border-slate-200 shadow-sm max-w-md w-full flex flex-col items-center text-center">
                  <span className="text-xs font-bold text-blue-900 uppercase tracking-wider mb-1">
                    Authentication Required
                  </span>
                  <p className="text-xs text-slate-600 mb-3.5">
                    Sign in or create an account with email OTP verification to start asking questions.
                  </p>
                  <div className="flex gap-2.5">
                    <button
                      onClick={() => openAuthModal('signin')}
                      className="bg-[#0f274a] hover:bg-[#163a6f] text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm cursor-pointer"
                    >
                      Sign In
                    </button>
                    <button
                      onClick={() => openAuthModal('register')}
                      className="bg-white text-slate-800 px-4 py-2 rounded-xl text-xs font-semibold border border-slate-300 hover:bg-slate-100 cursor-pointer"
                    >
                      Create Account
                    </button>
                  </div>
                </div>
              )}

              <div className="grid sm:grid-cols-3 gap-3.5 w-full">
                <div
                  onClick={() => handleSend("I am an Indian student earning ₹20,000 per month. How should I start managing my money?")}
                  className="bg-white hover:bg-blue-50/40 p-4 rounded-xl border border-slate-200 hover:border-blue-700 transition-all text-left cursor-pointer group shadow-xs hover:shadow-sm"
                >
                  <DollarSign className="text-blue-800 mb-2.5 group-hover:scale-110 transition-transform" size={22} />
                  <div className="font-bold text-xs text-slate-900 group-hover:text-blue-900 transition-colors mb-1">Student Budgeting</div>
                  <div className="text-[11px] text-slate-500 leading-snug">Income allocation, emergency funds & saving</div>
                </div>
                <div
                  onClick={() => handleSend("What is the current price and market overview for Reliance Industries?")}
                  className="bg-white hover:bg-blue-50/40 p-4 rounded-xl border border-slate-200 hover:border-blue-700 transition-all text-left cursor-pointer group shadow-xs hover:shadow-sm"
                >
                  <Activity className="text-blue-800 mb-2.5 group-hover:scale-110 transition-transform" size={22} />
                  <div className="font-bold text-xs text-slate-900 group-hover:text-blue-900 transition-colors mb-1">Stock Analysis</div>
                  <div className="text-[11px] text-slate-500 leading-snug">NSE/BSE live quotes & financial ratios</div>
                </div>
                <div
                  onClick={() => handleSend("Calculate the future value of investing ₹5,000 monthly at 12% CAGR for 10 years.")}
                  className="bg-white hover:bg-blue-50/40 p-4 rounded-xl border border-slate-200 hover:border-blue-700 transition-all text-left cursor-pointer group shadow-xs hover:shadow-sm"
                >
                  <TrendingUp className="text-blue-800 mb-2.5 group-hover:scale-110 transition-transform" size={22} />
                  <div className="font-bold text-xs text-slate-900 group-hover:text-blue-900 transition-colors mb-1">SIP & Compound Growth</div>
                  <div className="text-[11px] text-slate-500 leading-snug">Deterministic financial math calculations</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6 pb-6">
              {messages.map((msg, i) => (
                <ChatMessageItem
                  key={i}
                  msg={msg}
                  index={i}
                  isSpeaking={speakingIndex === i}
                  isCopied={copiedIndex === i}
                  onToggleTTS={handleToggleTTS}
                  onCopy={handleCopyMessage}
                  onSendAction={handleSend}
                  loading={loading}
                />
              ))}
              {loading && (
                <div className="flex gap-3.5 justify-start animate-in fade-in duration-200">
                  <div className="w-8 h-8 rounded-lg bg-[#0f274a] text-white flex items-center justify-center shrink-0 shadow-xs mt-1 animate-pulse">
                    <Bot size={18} />
                  </div>
                  <div className="max-w-md rounded-2xl px-4 py-3 bg-[#f8fafc] border border-slate-200 rounded-tl-sm text-slate-700 text-xs flex items-center gap-3 shadow-xs">
                    <span className="font-bold text-blue-900 flex items-center gap-1.5">
                      <Sparkles size={13} className="text-blue-700 animate-spin" />
                      Analyzing financial context...
                    </span>
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-[#0f274a] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-[#0f274a] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-[#0f274a] rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar (Isolated Memoized Component) */}
        <ChatInputBar
          onSend={handleSend}
          loading={loading}
          uploadLoading={uploadLoading}
          activeDoc={activeDoc}
          onUploadFile={handleUpload}
          onDetachDoc={handleDetachDoc}
          isAuthenticated={isAuthenticated}
          rateLimitSeconds={rateLimitSeconds}
          onClearRateLimit={handleClearRateLimit}
        />

      </main>
    </div>
  );
}

export default App;
