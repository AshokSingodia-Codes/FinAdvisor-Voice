import React from 'react';
import { MessageSquare, Edit3, Trash2, Check, X } from 'lucide-react';

export interface ConversationItem {
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

interface ConversationSidebarItemProps {
  conv: ConversationItem;
  isActive: boolean;
  isEditing: boolean;
  editTitleInput: string;
  onSelect: (convId: string) => void;
  onStartRename: (e: React.MouseEvent, conv: ConversationItem) => void;
  onSaveRename: (e: React.MouseEvent | React.KeyboardEvent, convId: string) => void;
  onCancelRename: (e: React.MouseEvent) => void;
  onEditInputChange: (val: string) => void;
  onDelete: (e: React.MouseEvent, convId: string) => void;
}

export const ConversationSidebarItem = React.memo(function ConversationSidebarItem({
  conv,
  isActive,
  isEditing,
  editTitleInput,
  onSelect,
  onStartRename,
  onSaveRename,
  onCancelRename,
  onEditInputChange,
  onDelete
}: ConversationSidebarItemProps) {
  return (
    <div
      onClick={() => !isEditing && onSelect(conv.id)}
      className={`group flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all border ${
        isActive
          ? 'bg-blue-50/70 border-blue-200/80 text-blue-950 font-semibold shadow-xs'
          : 'border-transparent hover:bg-slate-100/70 text-slate-700 hover:text-slate-900'
      }`}
    >
      <div className="flex items-center gap-2.5 min-w-0 flex-1">
        <MessageSquare
          size={15}
          className={`shrink-0 ${isActive ? 'text-blue-800' : 'text-slate-400 group-hover:text-slate-600'}`}
        />

        {isEditing ? (
          <div className="flex items-center gap-1 flex-1 min-w-0" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              value={editTitleInput}
              onChange={(e) => onEditInputChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') onSaveRename(e, conv.id);
                if (e.key === 'Escape') onCancelRename(e as any);
              }}
              autoFocus
              className="w-full bg-white border border-blue-500 rounded px-2 py-0.5 text-xs text-slate-900 focus:outline-none"
            />
            <button
              onClick={(e) => onSaveRename(e, conv.id)}
              className="p-1 text-blue-800 hover:text-blue-900 rounded"
              title="Save"
            >
              <Check size={13} />
            </button>
            <button
              onClick={onCancelRename}
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
            onClick={(e) => onStartRename(e, conv)}
            className="p-1 text-slate-400 hover:text-blue-800 rounded hover:bg-slate-200 transition-colors"
            title="Rename Chat"
          >
            <Edit3 size={13} />
          </button>
          <button
            onClick={(e) => onDelete(e, conv.id)}
            className="p-1 text-slate-400 hover:text-red-600 rounded hover:bg-red-50 transition-colors"
            title="Delete Chat"
          >
            <Trash2 size={13} />
          </button>
        </div>
      )}
    </div>
  );
});
