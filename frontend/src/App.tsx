import { useState, useRef, useEffect } from 'react';
import {
  Send,
  TrendingUp,
  DollarSign,
  Activity,
  Plus,
  MessageSquare,
  Trash2,
  Edit3,
  Check,
  X,
  Sparkles,
  Bot,
  User as UserIcon,
  Shield,
  Clock,
  LogOut,
  LogIn,
  UserPlus,
  Paperclip,
  FileText,
  AlertTriangle,
  Upload,
  Copy,
  Volume2,
  VolumeX
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuth } from './context/AuthContext';
import { AuthModal } from './components/AuthModal';
import { LoginPage } from './components/LoginPage';
import { VoiceInputButton } from './components/VoiceInputButton';
import { API_BASE } from './config';

interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  steps?: string[];
  isError?: boolean;
}

interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

interface ActiveDocument {
  id: string;
  filename: string;
  chunk_count: number;
  file_size_bytes: number;
}

function formatRelativeTime(dateStr: string): string {
  if (!dateStr) return '';
  try {
    const cleanStr = dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T');
    const normalized = cleanStr.endsWith('Z') ? cleanStr : cleanStr + 'Z';
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return '';
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - d.getTime()) / 1000);

    if (diffSec < 60) return 'Just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    if (diffSec < 172800) return 'Yesterday';
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
}

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
  const [input, setInput] = useState('');
  const [interimVoice, setInterimVoice] = useState('');
  const [loading, setLoading] = useState(false);

  // Document upload state
  const [activeDoc, setActiveDoc] = useState<ActiveDocument | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Rate limit toast
  const [rateLimitSeconds, setRateLimitSeconds] = useState<number | null>(null);
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editTitleInput, setEditTitleInput] = useState('');

  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [speakingIndex, setSpeakingIndex] = useState<number | null>(null);

  const handleCopyMessage = (content: string, index: number) => {
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
  };

  const handleToggleTTS = (content: string, index: number) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }

    window.speechSynthesis.cancel();
    // Strip markdown, code blocks, and table bars for natural voice reading
    const cleanText = content
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/\|.*?\|/g, ' ')
      .replace(/[#*_`~>-]/g, '')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onend = () => setSpeakingIndex(null);
    utterance.onerror = () => setSpeakingIndex(null);

    setSpeakingIndex(index);
    window.speechSynthesis.speak(utterance);
  };

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Stop speech synthesis when conversation changes
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setSpeakingIndex(null);
  }, [activeConvId]);

  // Count down the rate-limit toast automatically
  useEffect(() => {
    if (rateLimitSeconds === null || rateLimitSeconds <= 0) return;
    const timer = setTimeout(() => setRateLimitSeconds(s => (s !== null ? s - 1 : null)), 1000);
    return () => clearTimeout(timer);
  }, [rateLimitSeconds]);

  // Detach document automatically when the user switches to a different conversation
  useEffect(() => {
    setActiveDoc(null);
  }, [activeConvId]);

  // Load conversations list
  const fetchConversations = async () => {
    if (!isAuthenticated) {
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
  };

  // Load single conversation messages
  const loadConversation = async (convId: string) => {
    if (!isAuthenticated) return;
    try {
      const res = await authFetch(`${API_BASE}/api/conversations/${convId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveConvId(data.id);
        setActiveTitle(data.title || 'New Chat');
        setMessages(data.messages || []);
      } else {
        // Fallback for new empty chat
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
  };

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
  }, [isAuthenticated]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleNewChat = () => {
    const newId = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
    setActiveConvId(newId);
    setActiveTitle('New Chat');
    setMessages([]);
    setActiveDoc(null); // detach document when starting a new chat
  };

  const handleSelectConversation = async (convId: string) => {
    if (convId === activeConvId) return;
    await loadConversation(convId);
  };

  const handleDeleteConversation = async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    try {
      const res = await authFetch(`${API_BASE}/api/conversations/${convId}`, { method: 'DELETE' });
      if (res.ok) {
        const updated = conversations.filter(c => c.id !== convId);
        setConversations(updated);
        if (activeConvId === convId) {
          if (updated.length > 0) {
            await loadConversation(updated[0].id);
          } else {
            handleNewChat();
          }
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const startRename = (e: React.MouseEvent, conv: ConversationItem) => {
    e.stopPropagation();
    setEditingConvId(conv.id);
    setEditTitleInput(conv.title);
  };

  const handleSaveRename = async (e: React.MouseEvent | React.KeyboardEvent, convId: string) => {
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
        if (activeConvId === convId) {
          setActiveTitle(trimmed);
        }
      }
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    } finally {
      setEditingConvId(null);
    }
  };

  const handleSend = async (textToSend?: string) => {
    if (!isAuthenticated) {
      openAuthModal('signin');
      return;
    }

    const userMsg = (textToSend ?? input).trim();
    if (!userMsg || loading) return;

    setInput('');
    const newMessages: ChatMessage[] = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await authFetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          conversation_id: activeConvId,
          chat_history: messages,
          document_id: activeDoc?.id ?? null,
        })
      });

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

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();

      setMessages([...newMessages, { role: 'assistant', content: data.answer }]);

      if (data.title) {
        setActiveTitle(data.title);
      }

      // Refresh sidebar conversations to show updated title and order
      await fetchConversations();
    } catch (error) {
      console.error('Error fetching chat response:', error);
      setMessages([
        ...newMessages,
        { role: 'assistant', content: 'Sorry, I encountered an error while trying to process your request. Please try again.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !isAuthenticated) return;

    setUploadLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('conversation_id', activeConvId);

      const res = await authFetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (res.status === 413) {
        alert('File too large. Maximum size is 10 MB.');
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
      // Reset file input so same file can be re-uploaded
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDetachDoc = async () => {
    if (!activeDoc || !isAuthenticated) return;
    try {
      await authFetch(
        `${API_BASE}/api/documents/${activeDoc.id}?conversation_id=${encodeURIComponent(activeConvId)}`,
        { method: 'DELETE' }
      );
    } catch (err) {
      console.error('Delete doc error:', err);
    } finally {
      setActiveDoc(null);
    }
  };

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

      {/* Sidebar */}
      <aside className="w-72 bg-[#f8fafc] border-r border-slate-200/90 flex flex-col shrink-0">
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
            {isAuthenticated && (
              <span className="text-[10px] bg-blue-100/70 text-blue-900 border border-blue-200 px-1.5 py-0.5 rounded-full font-mono font-semibold">
                {conversations.length}
              </span>
            )}
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
            conversations.map((conv) => {
              const isActive = conv.id === activeConvId;
              const isEditing = editingConvId === conv.id;

              return (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150 border ${isActive
                      ? 'bg-blue-50/90 border-blue-200 text-blue-950 font-semibold shadow-xs'
                      : 'bg-transparent border-transparent hover:bg-slate-200/50 hover:border-slate-200 text-slate-600 hover:text-slate-900'
                    }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                    <MessageSquare size={15} className={`shrink-0 ${isActive ? 'text-blue-800' : 'text-slate-400'}`} />

                    {isEditing ? (
                      <div className="flex items-center gap-1 flex-1" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="text"
                          value={editTitleInput}
                          onChange={(e) => setEditTitleInput(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveRename(e, conv.id);
                            if (e.key === 'Escape') setEditingConvId(null);
                          }}
                          autoFocus
                          className="w-full bg-white border border-blue-500 rounded px-2 py-0.5 text-xs text-slate-900 focus:outline-none"
                        />
                        <button
                          onClick={(e) => handleSaveRename(e, conv.id)}
                          className="p-1 text-blue-800 hover:text-blue-900 rounded"
                          title="Save"
                        >
                          <Check size={13} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingConvId(null);
                          }}
                          className="p-1 text-slate-400 hover:text-slate-600 rounded"
                          title="Cancel"
                        >
                          <X size={13} />
                        </button>
                      </div>
                    ) : (
                      <div className="min-w-0 flex-1">
                        <div className="text-xs font-medium truncate leading-tight">
                          {conv.title || 'New Chat'}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate mt-0.5">
                          {formatRelativeTime(conv.updated_at)}
                        </div>
                      </div>
                    )}
                  </div>

                  {!isEditing && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => startRename(e, conv)}
                        className="p-1 text-slate-400 hover:text-blue-800 rounded hover:bg-slate-200 transition-colors"
                        title="Rename Chat"
                      >
                        <Edit3 size={13} />
                      </button>
                      <button
                        onClick={(e) => handleDeleteConversation(e, conv.id)}
                        className="p-1 text-slate-400 hover:text-red-600 rounded hover:bg-red-50 transition-colors"
                        title="Delete Chat"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  )}
                </div>
              );
            })
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
        <header className="h-14 border-b border-slate-200/90 flex items-center justify-between px-6 bg-white sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span>{activeTitle}</span>
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="flex items-center gap-1.5 text-xs text-slate-700 bg-slate-100 border border-slate-200 px-3 py-1 rounded-full font-medium">
              <Shield size={13} className="text-blue-800" />
              <span>Isolated Memory</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Indian Market & RAG Active</span>
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
              <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center mb-6 shadow-sm">
                <Sparkles size={30} className="text-blue-800" />
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
                <div key={i} className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-[#0f274a] text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
                      <Bot size={18} />
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-5 py-4 text-[14.5px] leading-relaxed select-text ${msg.role === 'user'
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
                            h1: ({ children }) => <h1 className="text-lg font-bold text-slate-900 mt-3 mb-2 pb-1 border-b border-slate-200">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-base font-bold text-blue-900 mt-3 mb-1.5">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-sm font-semibold text-blue-800 mt-2 mb-1">{children}</h3>,
                            p: ({ children }) => <p className="mb-2 leading-relaxed text-slate-800">{children}</p>,
                            ul: ({ children }) => <ul className="list-disc pl-5 mb-2.5 space-y-1 text-slate-800">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal pl-5 mb-2.5 space-y-1 text-slate-800">{children}</ol>,
                            li: ({ children }) => <li className="text-slate-800">{children}</li>,
                            hr: () => <hr className="border-slate-200 my-3" />,
                            strong: ({ children }) => <strong className="font-bold text-slate-950">{children}</strong>,
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
                            thead: ({ children }) => <thead className="bg-slate-100 text-blue-950 font-bold border-b border-slate-200">{children}</thead>,
                            tbody: ({ children }) => <tbody className="divide-y divide-slate-100 bg-white">{children}</tbody>,
                            tr: ({ children }) => <tr className="hover:bg-slate-50 transition-colors">{children}</tr>,
                            th: ({ children }) => <th className="px-3.5 py-2.5 text-[11px] uppercase tracking-wider font-bold text-blue-950">{children}</th>,
                            td: ({ children }) => <td className="px-3.5 py-2.5 text-xs text-slate-800 whitespace-normal">{children}</td>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>

                        {/* Interactive Next-Step Action Chips */}
                        {(() => {
                          const suggestions: string[] = [];
                          const regex = /\[([A-Za-z0-9\s₹$,%.\-/?!]{4,50})\]/g;
                          let match;
                          while ((match = regex.exec(msg.content)) !== null) {
                            const act = match[1].trim();
                            if (act && !suggestions.includes(act) && !act.toLowerCase().startsWith('action')) {
                              suggestions.push(act);
                            }
                          }
                          if (suggestions.length === 0) return null;
                          return (
                            <div className="mt-3 pt-2.5 border-t border-slate-200">
                              <div className="text-[11px] font-bold text-blue-900 mb-2 flex items-center gap-1">
                                <Sparkles size={12} className="text-blue-700" />
                                <span>Suggested Next Actions:</span>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {suggestions.slice(0, 3).map((actionText, actIdx) => (
                                  <button
                                    key={actIdx}
                                    onClick={() => handleSend(actionText)}
                                    disabled={loading}
                                    className="flex items-center gap-1.5 text-xs bg-blue-50 hover:bg-blue-100 text-blue-900 font-semibold border border-blue-200 hover:border-blue-400 px-3 py-1.5 rounded-xl transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50"
                                  >
                                    <span>{actionText}</span>
                                    <span className="text-[10px] opacity-70">→</span>
                                  </button>
                                ))}
                              </div>
                            </div>
                          );
                        })()}

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
                              onClick={() => handleToggleTTS(msg.content, i)}
                              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${speakingIndex === i
                                  ? 'bg-blue-100 text-blue-900 border border-blue-300 animate-pulse'
                                  : 'bg-white hover:bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200'
                                }`}
                              title={speakingIndex === i ? 'Stop Speaking' : 'Read Aloud'}
                            >
                              {speakingIndex === i ? <VolumeX size={13} className="text-blue-800" /> : <Volume2 size={13} />}
                              <span>{speakingIndex === i ? 'Stop' : 'Listen'}</span>
                            </button>

                            <button
                              onClick={() => handleCopyMessage(msg.content, i)}
                              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${copiedIndex === i
                                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                                  : 'bg-white hover:bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200'
                                }`}
                              title="Copy Answer to Clipboard"
                            >
                              {copiedIndex === i ? <Check size={13} className="text-emerald-700" /> : <Copy size={13} />}
                              <span>{copiedIndex === i ? 'Copied!' : 'Copy'}</span>
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
              ))}
              {loading && (
                <div className="flex gap-3.5 justify-start">
                  <div className="w-8 h-8 rounded-lg bg-[#0f274a] text-white flex items-center justify-center shrink-0 shadow-xs mt-1 animate-pulse">
                    <Bot size={18} />
                  </div>
                  <div className="max-w-md rounded-2xl px-4 py-3 bg-[#f8fafc] border border-slate-200 rounded-tl-sm text-slate-700 text-xs flex items-center gap-3 shadow-xs">
                    <span className="font-bold text-blue-900">Analyzing financial context...</span>
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

        {/* Input Bar */}
        <div className="border-t border-slate-200/90 bg-white pt-3 pb-3 px-4 sm:px-6 z-10">

          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md,.csv,text/plain,text/markdown,application/pdf"
            className="hidden"
            onChange={handleUpload}
          />

          {/* Rate-limit toast */}
          {rateLimitSeconds !== null && rateLimitSeconds > 0 && (
            <div className="max-w-4xl mx-auto mb-2 flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-900 rounded-xl px-4 py-2 text-xs font-medium animate-pulse">
              <AlertTriangle size={14} className="shrink-0 text-amber-700" />
              <span>Rate limit reached. You can send another message in <strong>{rateLimitSeconds}s</strong>.</span>
              <button onClick={() => setRateLimitSeconds(null)} className="ml-auto text-amber-700 hover:text-amber-900 cursor-pointer">
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
                  onClick={handleDetachDoc}
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
                  <strong className="font-semibold text-amber-950">Personal document mode active.</strong>{' '}
                  Responses are based on your uploaded document. This is general guidance — not formal RIA advisory.
                </span>
              </div>
            </div>
          )}

          <div className="max-w-4xl mx-auto relative flex items-center bg-white border border-slate-300 rounded-xl focus-within:border-[#0f274a] focus-within:ring-2 focus-within:ring-[#0f274a]/15 shadow-xs transition-all overflow-visible">
            <input
              type="text"
              value={interimVoice ? input + (input && !input.endsWith(' ') ? ' ' : '') + interimVoice : input}
              onChange={(e) => {
                setInput(e.target.value);
                setInterimVoice('');
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={loading}
              placeholder={isAuthenticated ? "Ask for financial advice, stock updates, budgeting, or return calculations..." : "Please sign in to start asking questions..."}
              className="flex-1 bg-transparent pl-5 pr-2 py-3 text-slate-900 text-sm focus:outline-none placeholder:text-slate-400 disabled:opacity-50"
            />

            {interimVoice && (
              <span className="absolute left-5 -top-6 text-[10px] text-blue-900 font-semibold bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-md shadow-xs">
                Listening...
              </span>
            )}

            <div className="flex items-center gap-1.5 pr-2 shrink-0 relative">
              {/* Upload document button */}
              {isAuthenticated && (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading || uploadLoading}
                  title={uploadLoading ? "Uploading..." : activeDoc ? `Active: ${activeDoc.filename} — click to replace` : "Attach a financial document (PDF / TXT / MD, max 10 MB)"}
                  className={`p-2 rounded-lg transition-all shadow-xs cursor-pointer z-10 relative ${activeDoc
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
                onInterimResult={(text) => setInterimVoice(text)}
                onFinalResult={(text) => {
                  setInput(prev => prev + (prev && !prev.endsWith(' ') ? ' ' : '') + text);
                  setInterimVoice('');
                }}
              />
              <button
                onClick={() => handleSend()}
                disabled={loading || (!input.trim() && !interimVoice.trim())}
                className="p-2 rounded-lg bg-[#0f274a] hover:bg-[#163a6f] text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm cursor-pointer z-10 relative"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
          <div className="text-center mt-2 text-[11px] text-slate-500">
            FinAdvisor-X is an AI financial assistant. Always verify critical decisions with a licensed advisor.
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
