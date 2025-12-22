'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useAiTutor } from '@/hooks/use-brain-ai';
import type { TutorMessage } from '@/types/brain-ai';

interface AiTutorWidgetProps {
  userId: string;
  initialContext?: {
    currentContent?: string;
    currentCourse?: string;
    currentModule?: string;
  };
  position?: 'bottom-right' | 'bottom-left';
  defaultOpen?: boolean;
  onClose?: () => void;
}

export function AiTutorWidget({
  userId,
  initialContext,
  position = 'bottom-right',
  defaultOpen = false,
  onClose,
}: AiTutorWidgetProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    messages,
    isLoading,
    error,
    isTyping,
    sendMessage,
    clearHistory,
  } = useAiTutor({
    userId,
    initialContext,
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');

    await sendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedQuestions = [
    "Can you explain this concept in simpler terms?",
    "What are the key takeaways from this module?",
    "Can practice problem?",
 you give me a    "How does this relate to real-world applications?",
  ];

  return (
    <>
      {/* Floating Toggle Button */}
      {!isOpen && (
        <div
          className={`fixed ${
            position === 'bottom-right' ? 'right-6' : 'left-6'
          } bottom-6 z-50`}
        >
          <Button
            onClick={() => setIsOpen(true)}
            className="w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-700 shadow-lg hover:shadow-xl transition-all"
          >
            <div className="relative">
              <span className="text-2xl">🤖</span>
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></span>
            </div>
          </Button>
        </div>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <Card
          className={`fixed ${
            position === 'bottom-right' ? 'right-6' : 'left-6'
          } bottom-6 w-96 h-[500px] z-50 flex flex-col shadow-2xl`}
        >
          {/* Header */}
          <CardHeader className="flex-shrink-0 border-b bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-xl">🤖</span>
                <div>
                  <h3 className="font-semibold">AI Learning Tutor</h3>
                  <p className="text-xs text-indigo-200">
                    Powered by Brain AI Framework
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearHistory}
                  className="text-white hover:bg-white/20"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setIsOpen(false);
                    onClose?.();
                  }}
                  className="text-white hover:bg-white/20"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">👋</span>
                <h4 className="font-medium text-gray-900">
                  Welcome to AI Tutor!
                </h4>
                <p className="text-sm text-gray-500 mt-1">
                  Ask me anything about your courses
                </p>

                {/* Suggested Questions */}
                <div className="mt-4 space-y-2">
                  <p className="text-xs text-gray-400 uppercase">Try asking:</p>
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(question)}
                      className="block w-full text-left text-sm p-2 bg-gray-50 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}

                {isTyping && (
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                      <span className="text-sm">🤖</span>
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                )}

                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className="flex-shrink-0 border-t p-4">
            <div className="flex space-x-2">
              <Input
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your question..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </Button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              AI may make mistakes. Verify important information.
            </p>
          </div>
        </Card>
      )}
    </>
  );
}

interface ChatMessageProps {
  message: TutorMessage;
}

function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] ${
          isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-900'
        } rounded-2xl px-4 py-2`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        <p
          className={`text-xs mt-1 ${
            isUser ? 'text-indigo-200' : 'text-gray-400'
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}

// Compact inline version for course pages
export function InlineAiTutor({
  userId,
  context,
}: {
  userId: string;
  context: string;
}) {
  const {
    messages,
    isLoading,
    sendMessage,
    clearHistory,
  } = useAiTutor({
    userId,
    initialContext: { currentContent: context },
  });

  const [isExpanded, setIsExpanded] = useState(false);

  if (!isExpanded) {
    return (
      <Button
        variant="outline"
        onClick={() => setIsExpanded(true)}
        className="w-full"
      >
        <span className="mr-2">🤖</span>
        Ask AI Tutor about this content
      </Button>
    );
  }

  return (
    <Card className="mt-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <h4 className="font-medium flex items-center">
            <span className="mr-2">🤖</span>
            AI Tutor
          </h4>
          <Button variant="ghost" size="sm" onClick={() => setIsExpanded(false)}>
            Close
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-60 overflow-y-auto">
          {messages.slice(-3).map((message) => (
            <div
              key={message.id}
              className={`p-2 rounded ${
                message.role === 'user'
                  ? 'bg-indigo-50 ml-4'
                  : 'bg-gray-50 mr-4'
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          ))}
        </div>
        <div className="mt-3 flex space-x-2">
          <Input
            placeholder="Ask a question..."
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                sendMessage(e.currentTarget.value);
                e.currentTarget.value = '';
              }
            }}
            disabled={isLoading}
          />
          <Button
            size="sm"
            onClick={() => {
              const input = document.querySelector(
                'input[placeholder="Ask a question..."]'
              ) as HTMLInputElement;
              if (input?.value) {
                sendMessage(input.value);
                input.value = '';
              }
            }}
            disabled={isLoading}
          >
            Send
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
