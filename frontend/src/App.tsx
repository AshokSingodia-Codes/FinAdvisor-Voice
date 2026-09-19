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
  UserPlus
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuth } from './context/AuthContext';
import { AuthModal } from './components/AuthModal';
import { LoginPage } from './components/LoginPage';
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
  const [loading, setLoading] = useState(false);
  
  // Inline rename state
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editTitleInput, setEditTitleInput] = useState('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
          chat_history: messages
        })
      });

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
    <div className="flex h-screen bg-bgMain text-textMain overflow-hidden font-sans select-none">
      {/* Auth Modal Component */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={closeAuthModal}
        initialTab={authModalInitialTab}
      />

      {/* Sidebar */}
      <aside className="w-72 bg-bgCard border-r border-borderDim flex flex-col shrink-0">
        {/* Brand Header */}
        <div className="p-4 border-b border-borderDim flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accentPrimary to-accentHover flex items-center justify-center text-xl font-bold shadow-md text-bgMain">
              <TrendingUp size={20} className="text-[#0d0f14]" />
            </div>
            <div>
              <span className="font-bold text-base text-textMain tracking-tight">FinAdvisor-X</span>
              <span className="block text-[10px] text-accentPrimary font-semibold tracking-wider uppercase">AI Financial Analyst</span>
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
            className="w-full flex items-center justify-center gap-2.5 bg-gradient-to-r from-accentPrimary/15 to-accentHover/15 border border-accentPrimary/40 hover:border-accentPrimary hover:bg-accentPrimary/25 text-accentPrimary hover:text-white transition-all duration-200 rounded-xl py-2.5 px-4 text-sm font-semibold shadow-sm cursor-pointer active:scale-[0.98]"
          >
            <Plus size={16} className="stroke-[2.5]" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Recent Chats Section Header */}
        <div className="px-3 pt-2 pb-1">
          <div className="flex items-center justify-between px-2 mb-2">
            <span className="text-[11px] font-bold text-textDim tracking-wider uppercase flex items-center gap-1.5">
              <Clock size={12} />
              Recent Chats
            </span>
            {isAuthenticated && (
              <span className="text-[10px] bg-borderDim/80 text-textDim px-1.5 py-0.5 rounded-full font-mono font-medium">
                {conversations.length}
              </span>
            )}
          </div>
        </div>

        {/* Chats List */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          {!isAuthenticated ? (
            <div className="text-center py-8 px-4 text-textDim text-xs leading-relaxed">
              <p className="mb-3">Sign in to save and sync your chat history securely.</p>
              <button
                onClick={() => openAuthModal('signin')}
                className="inline-flex items-center gap-1.5 text-xs text-accentPrimary font-semibold hover:underline cursor-pointer"
              >
                <LogIn size={13} />
                <span>Sign In Now</span>
              </button>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 px-4 text-textDim text-xs leading-relaxed">
              No conversations yet.<br />Click <span className="text-accentPrimary font-medium">+ New Chat</span> to start!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConvId;
              const isEditing = editingConvId === conv.id;

              return (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150 border ${
                    isActive
                      ? 'bg-borderDim/90 border-accentPrimary/40 text-textMain shadow-sm'
                      : 'bg-transparent border-transparent hover:bg-borderDim/40 hover:border-borderDim text-textDim hover:text-textMain'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                    <MessageSquare size={15} className={`shrink-0 ${isActive ? 'text-accentPrimary' : 'text-textDim'}`} />
                    
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
                          className="w-full bg-bgMain border border-accentPrimary rounded px-2 py-0.5 text-xs text-textMain focus:outline-none"
                        />
                        <button
                          onClick={(e) => handleSaveRename(e, conv.id)}
                          className="p-1 text-accentPrimary hover:text-white rounded"
                          title="Save"
                        >
                          <Check size={13} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingConvId(null);
                          }}
                          className="p-1 text-textDim hover:text-textMain rounded"
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
                        <div className="text-[10px] text-textDim/70 truncate mt-0.5">
                          {formatRelativeTime(conv.updated_at)}
                        </div>
                      </div>
                    )}
                  </div>

                  {!isEditing && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => startRename(e, conv)}
                        className="p-1 text-textDim hover:text-accentPrimary rounded hover:bg-bgMain/60 transition-colors"
                        title="Rename Chat"
                      >
                        <Edit3 size={13} />
                      </button>
                      <button
                        onClick={(e) => handleDeleteConversation(e, conv.id)}
                        className="p-1 text-textDim hover:text-red-400 rounded hover:bg-bgMain/60 transition-colors"
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
        <div className="p-3 border-t border-borderDim">
          {isAuthenticated && user ? (
            <div className="flex items-center justify-between p-2 rounded-xl bg-borderDim/30 border border-borderDim/50">
              <div className="flex items-center gap-2.5 min-w-0 flex-1 mr-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 via-purple-500 to-accentPrimary flex items-center justify-center font-bold text-white text-xs shadow-inner shrink-0">
                  <UserIcon size={14} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold truncate text-textMain" title={user.email}>
                    {user.email}
                  </div>
                  <div className="text-[10px] text-accentPrimary flex items-center gap-1 font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-accentPrimary animate-pulse"></span>
                    Authenticated (JWT)
                  </div>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 text-textDim hover:text-red-400 hover:bg-borderDim rounded-lg transition-colors cursor-pointer shrink-0"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <button
                onClick={() => openAuthModal('signin')}
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-accentPrimary to-accentHover text-bgMain font-bold py-2 px-3 rounded-xl text-xs shadow-md hover:brightness-110 active:scale-[0.98] transition-all cursor-pointer"
              >
                <LogIn size={14} />
                <span>Sign In</span>
              </button>
              <button
                onClick={() => openAuthModal('register')}
                className="w-full flex items-center justify-center gap-2 bg-borderDim hover:bg-borderDim/80 text-textMain font-medium py-1.5 px-3 rounded-xl text-xs border border-borderDim hover:border-accentPrimary/40 transition-all cursor-pointer"
              >
                <UserPlus size={13} />
                <span>Create New Account</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {/* Top Navbar */}
        <header className="h-14 border-b border-borderDim flex items-center justify-between px-6 bg-bgCard/60 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="text-sm font-bold text-textMain tracking-tight flex items-center gap-2">
              <span>{activeTitle}</span>
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="flex items-center gap-1.5 text-xs text-textDim bg-borderDim/60 border border-borderDim px-3 py-1 rounded-full font-medium">
              <Shield size={13} className="text-accentPrimary" />
              <span>Isolated Memory</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-accentPrimary bg-accentPrimary/10 border border-accentPrimary/30 px-3 py-1 rounded-full font-medium">
              <span className="w-2 h-2 rounded-full bg-accentPrimary animate-pulse"></span>
              <span>Indian Market & RAG Active</span>
            </div>
            {!isAuthenticated && (
              <button
                onClick={() => openAuthModal('signin')}
                className="ml-2 flex items-center gap-1.5 bg-accentPrimary/20 hover:bg-accentPrimary/30 text-accentPrimary border border-accentPrimary/40 px-3 py-1 rounded-full text-xs font-semibold transition-all cursor-pointer"
              >
                <LogIn size={13} />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </header>

        {/* Chat Messages Area */}
        <div className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 scroll-smooth">
          {messages.length === 0 ? (
            <div className="min-h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto px-4 py-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-accentPrimary/20 via-borderDim to-bgCard border border-accentPrimary/30 flex items-center justify-center mb-6 shadow-xl">
                <Sparkles size={32} className="text-accentPrimary" />
              </div>
              <h1 className="text-3xl font-bold mb-3 tracking-tight text-textMain">
                How can I assist your financial journey?
              </h1>
              <p className="text-textDim text-sm sm:text-base mb-8 leading-relaxed max-w-lg">
                I maintain conversational memory within this chat to help you plan budgets, analyze stocks, model SIP returns, and evaluate tax strategies.
              </p>
              
              {!isAuthenticated && (
                <div className="mb-8 p-4 rounded-2xl bg-borderDim/30 border border-accentPrimary/30 max-w-md w-full flex flex-col items-center text-center">
                  <span className="text-xs font-semibold text-accentPrimary uppercase tracking-wider mb-1">
                    Authentication Required
                  </span>
                  <p className="text-xs text-textDim mb-3">
                    Sign in or create an account with email OTP verification to start asking questions.
                  </p>
                  <div className="flex gap-2.5">
                    <button
                      onClick={() => openAuthModal('signin')}
                      className="bg-accentPrimary text-bgMain px-4 py-2 rounded-xl text-xs font-bold hover:brightness-110 shadow-sm cursor-pointer"
                    >
                      Sign In
                    </button>
                    <button
                      onClick={() => openAuthModal('register')}
                      className="bg-borderDim text-textMain px-4 py-2 rounded-xl text-xs font-semibold border border-borderDim hover:border-accentPrimary/50 cursor-pointer"
                    >
                      Create Account
                    </button>
                  </div>
                </div>
              )}

              <div className="grid sm:grid-cols-3 gap-3.5 w-full">
                <div
                  onClick={() => handleSend("I am an Indian student earning ₹20,000 per month. How should I start managing my money?")}
                  className="bg-bgCard/80 hover:bg-bgCard p-4 rounded-xl border border-borderDim hover:border-accentPrimary/60 transition-all text-left cursor-pointer group shadow-sm hover:shadow-md"
                >
                  <DollarSign className="text-accentPrimary mb-2.5 group-hover:scale-110 transition-transform" size={22} />
                  <div className="font-semibold text-xs text-textMain mb-1">Student Budgeting</div>
                  <div className="text-[11px] text-textDim leading-snug">Income allocation, emergency funds & saving</div>
                </div>
                <div
                  onClick={() => handleSend("What is the current price and market overview for Reliance Industries?")}
                  className="bg-bgCard/80 hover:bg-bgCard p-4 rounded-xl border border-borderDim hover:border-accentPrimary/60 transition-all text-left cursor-pointer group shadow-sm hover:shadow-md"
                >
                  <Activity className="text-accentPrimary mb-2.5 group-hover:scale-110 transition-transform" size={22} />
                  <div className="font-semibold text-xs text-textMain mb-1">Stock Analysis</div>
                  <div className="text-[11px] text-textDim leading-snug">NSE/BSE live quotes & financial ratios</div>
                </div>
                <div
                  onClick={() => handleSend("Calculate the future value of investing ₹5,000 monthly at 12% CAGR for 10 years.")}
                  className="bg-bgCard/80 hover:bg-bgCard p-4 rounded-xl border border-borderDim hover:border-accentPrimary/60 transition-all text-left cursor-pointer group shadow-sm hover:shadow-md"
                >
                  <TrendingUp className="text-accentPrimary mb-2.5 group-hover:scale-110 transition-transform" size={22} />
                  <div className="font-semibold text-xs text-textMain mb-1">SIP & Compound Growth</div>
                  <div className="text-[11px] text-textDim leading-snug">Deterministic financial math calculations</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6 pb-6">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-bgCard border border-borderDim flex items-center justify-center shrink-0 text-accentPrimary shadow-sm mt-1">
                      <Bot size={18} />
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-5 py-3.5 text-[14.5px] leading-relaxed shadow-sm select-text ${
                      msg.role === 'user'
                        ? 'max-w-[80%] bg-gradient-to-r from-accentPrimary/20 to-borderDim border border-accentPrimary/30 text-textMain rounded-tr-sm'
                        : 'w-full max-w-full bg-bgCard border border-borderDim text-textMain rounded-tl-sm'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    ) : (
                      <div className="prose prose-invert max-w-none text-textMain leading-relaxed space-y-2.5">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h1: ({ children }) => <h1 className="text-lg font-bold text-textMain mt-3 mb-2 pb-1 border-b border-borderDim">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-base font-bold text-accentPrimary mt-3 mb-1.5">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-sm font-semibold text-textMain mt-2 mb-1">{children}</h3>,
                            p: ({ children }) => <p className="mb-2 leading-relaxed text-textMain">{children}</p>,
                            ul: ({ children }) => <ul className="list-disc pl-5 mb-2.5 space-y-1 text-textMain">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal pl-5 mb-2.5 space-y-1 text-textMain">{children}</ol>,
                            li: ({ children }) => <li className="text-textMain">{children}</li>,
                            hr: () => <hr className="border-borderDim my-3" />,
                            strong: ({ children }) => <strong className="font-semibold text-accentPrimary">{children}</strong>,
                            code: ({ children }) => (
                              <code className="bg-borderDim text-accentPrimary px-1.5 py-0.5 rounded text-xs font-mono">
                                {children}
                              </code>
                            ),
                            table: ({ children }) => (
                              <div className="my-3 overflow-x-auto rounded-lg border border-borderDim shadow-sm">
                                <table className="min-w-full divide-y divide-borderDim text-left text-xs">
                                  {children}
                                </table>
                              </div>
                            ),
                            thead: ({ children }) => <thead className="bg-[#181d2c] text-accentPrimary font-semibold">{children}</thead>,
                            tbody: ({ children }) => <tbody className="divide-y divide-borderDim/50 bg-bgCard">{children}</tbody>,
                            tr: ({ children }) => <tr className="hover:bg-borderDim/30 transition-colors">{children}</tr>,
                            th: ({ children }) => <th className="px-3 py-2 text-[11px] uppercase tracking-wider font-bold">{children}</th>,
                            td: ({ children }) => <td className="px-3 py-2 text-xs text-textMain whitespace-normal">{children}</td>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-borderDim border border-accentPrimary/40 flex items-center justify-center shrink-0 text-accentPrimary text-xs font-bold shadow-sm mt-1">
                      <UserIcon size={14} />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-3.5 justify-start">
                  <div className="w-8 h-8 rounded-lg bg-bgCard border border-borderDim flex items-center justify-center shrink-0 text-accentPrimary shadow-sm mt-1 animate-pulse">
                    <Bot size={18} />
                  </div>
                  <div className="max-w-md rounded-2xl px-4 py-3 bg-bgCard border border-borderDim rounded-tl-sm text-textDim text-xs flex items-center gap-3 shadow-sm">
                    <span className="font-medium text-accentPrimary">Analyzing financial context...</span>
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-accentPrimary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-accentPrimary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-accentPrimary rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar (Solid Non-Overlapping Footer) */}
        <div className="border-t border-borderDim bg-bgCard/90 backdrop-blur-md pt-3 pb-3 px-4 sm:px-6 z-10">
          <div className="max-w-4xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={loading}
              placeholder={isAuthenticated ? "Ask for financial advice, stock updates, budgeting, or return calculations..." : "Please sign in to start asking questions..."}
              className="w-full bg-bgMain border border-borderDim rounded-xl pl-5 pr-14 py-3 text-textMain text-sm focus:outline-none focus:border-accentPrimary focus:ring-1 focus:ring-accentPrimary/50 shadow-inner placeholder:text-textDim/60 disabled:opacity-50 transition-all"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-borderDim hover:bg-accentPrimary text-textMain hover:text-bgMain disabled:opacity-40 disabled:hover:bg-borderDim disabled:hover:text-textMain transition-all shadow-sm cursor-pointer"
            >
              <Send size={16} />
            </button>
          </div>
          <div className="text-center mt-2 text-[11px] text-textDim/60">
            FinAdvisor-X is an AI financial assistant. Always verify critical decisions with a licensed advisor.
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
