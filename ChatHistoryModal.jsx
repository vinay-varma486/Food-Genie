import React, { useState, useEffect } from 'react';
import { MessageSquare, Trash2, X, Plus, Clock, ArrowRight, Loader2 } from 'lucide-react';
import { apiClient } from './api';
import { useAuth } from './AuthContext';

export const ChatHistoryModal = ({ isOpen, onClose, onSelectSession, onNewChat, activeSessionId }) => {
  const { token, isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      loadConversations();
    } else if (isOpen) {
      setConversations([]);
    }
  }, [isOpen, token, isAuthenticated]);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getConversations(token);
      setConversations(Array.isArray(data) ? data : []);
    } catch (_) {
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (sessionId, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation?')) return;
    setDeletingId(sessionId);
    try {
      await apiClient.deleteConversation(sessionId, token);
      setConversations((prev) => prev.filter((c) => c.session_id !== sessionId));
      if (activeSessionId === sessionId) onNewChat();
    } finally {
      setDeletingId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-royal-deep/50 backdrop-blur-sm">
      <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-card border border-lavender-border overflow-hidden flex flex-col max-h-[82vh]">
        <div className="bg-royal p-5 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-royal-deep flex items-center justify-center text-lime-electric">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-display font-bold text-base">Chat History</h3>
              <p className="text-xs text-lavender-mist/80">Reopen past Genie conversations</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => { onNewChat(); onClose(); }}
              className="px-3 py-1.5 rounded-full bg-lime-electric text-royal-deep font-bold text-xs flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Chat</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-full hover:bg-white/10 text-white"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="p-5 overflow-y-auto space-y-2.5 flex-1 bg-lavender-light">
          {!isAuthenticated ? (
            <div className="py-10 text-center text-xs text-royal/70">
              Sign in to save and revisit conversations across sessions.
            </div>
          ) : loading ? (
            <div className="py-10 flex flex-col items-center justify-center text-royal/70 gap-2">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-xs font-semibold">Loading conversations...</span>
            </div>
          ) : conversations.length === 0 ? (
            <div className="py-10 text-center text-xs text-royal/70">
              No saved conversations yet. Start chatting with Genie!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.session_id === activeSessionId;
              const dateStr = new Date(conv.last_active || conv.started_at).toLocaleDateString([], {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              });
              return (
                <div
                  key={conv.session_id}
                  onClick={() => { onSelectSession(conv.session_id); onClose(); }}
                  className={`p-3.5 rounded-2xl border cursor-pointer flex items-center justify-between gap-2 ${
                    isActive
                      ? 'bg-royal text-white border-royal'
                      : 'bg-white hover:bg-lavender-mist/40 text-royal border-lavender-border'
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-bold text-xs sm:text-sm truncate">{conv.title}</p>
                    <p className="text-[11px] opacity-75 flex items-center gap-1.5 mt-0.5">
                      <Clock className="w-3 h-3" />
                      <span>{dateStr}</span>
                      <span>• {conv.message_count} messages</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <button
                      type="button"
                      onClick={(e) => handleDeleteConversation(conv.session_id, e)}
                      disabled={deletingId === conv.session_id}
                      className="p-1.5 rounded-lg hover:bg-red-500/20"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
