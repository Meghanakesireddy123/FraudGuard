import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X, FileDown, SlidersHorizontal, Headphones, ChevronRight, Send, Bot } from "lucide-react";
import { Input } from "@/components/ui/input";

const faqs = [
  {
    id: 1,
    question: "Export Data",
    answer: "You can export your transaction data from the Analytics page. Click on the 'Export' button to download a CSV file with all your transaction history.",
    icon: FileDown,
  },
  {
    id: 2,
    question: "Adjust Thresholds",
    answer: "Go to Settings > Fraud Detection to customize your risk thresholds. You can set custom limits for amount triggers and time-based rules.",
    icon: SlidersHorizontal,
  },
  {
    id: 3,
    question: "Contact Support",
    answer: "Our support team is available 24/7. Email us at support@fraudguard.io or call +91 1800-FRAUD-00 for immediate assistance.",
    icon: Headphones,
  },
  {
    id: 4,
    question: "Chat with AI",
    answer: "interactive", // Special flag for interactive chat
    icon: Bot,
  },
];

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFaq, setSelectedFaq] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: inputMessage,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // Call Gemini AI via backend
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      const botMessage: Message = {
        id: messages.length + 2,
        text: data.response || "I apologize, but I couldn't generate a response. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error calling AI:', error);
      const errorMessage: Message = {
        id: messages.length + 2,
        text: "I'm having trouble connecting to the AI service. Please try again in a moment.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetChat = () => {
    setSelectedFaq(null);
    setMessages([]);
    setInputMessage("");
  };

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center transition-all hover:scale-105 hover:shadow-xl z-50 ${isOpen ? "scale-0 opacity-0" : "scale-100 opacity-100"
          }`}
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      <div
        className={`fixed bottom-6 right-6 w-96 bg-card rounded-2xl shadow-2xl border border-border z-50 transition-all duration-300 ${isOpen ? "scale-100 opacity-100" : "scale-0 opacity-0 pointer-events-none"
          }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">FraudGuard Assistant</h3>
              <p className="text-xs text-muted-foreground">Always here to help</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              setIsOpen(false);
              resetChat();
            }}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="max-h-96 overflow-y-auto">
          {selectedFaq === null ? (
            <div className="p-4 space-y-3">
              <p className="text-sm text-muted-foreground mb-4">
                How can I help you today? Select a topic below:
              </p>
              {faqs.map((faq) => (
                <button
                  key={faq.id}
                  onClick={() => {
                    setSelectedFaq(faq.id);
                    if (faq.answer === "interactive") {
                      // Initialize chat with welcome message
                      setMessages([
                        {
                          id: 1,
                          text: "Hello! 👋 I'm your FraudGuard AI assistant. I can answer questions about fraud detection, help you use features, or guide you through the system. What would you like to know?",
                          sender: "bot",
                          timestamp: new Date(),
                        },
                      ]);
                    }
                  }}
                  className="w-full flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-accent transition-colors text-left"
                >
                  <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                    <faq.icon className="w-5 h-5 text-foreground" />
                  </div>
                  <span className="flex-1 font-medium text-foreground">{faq.question}</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </button>
              ))}
            </div>
          ) : (
            <div className="animate-fade-in">
              <div className="p-4">
                <button
                  onClick={resetChat}
                  className="text-sm text-primary hover:underline mb-4 flex items-center gap-1"
                >
                  ← Back to topics
                </button>

                {faqs.find((f) => f.id === selectedFaq)?.answer === "interactive" ? (
                  // Interactive AI Chat
                  <div className="space-y-3">
                    {/* Messages */}
                    <div className="space-y-3 min-h-[200px] max-h-[250px] overflow-y-auto pr-2">
                      {messages.map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-lg p-3 ${msg.sender === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted text-foreground"
                              }`}
                          >
                            {msg.sender === "bot" && (
                              <div className="flex items-center gap-2 mb-1">
                                <Bot className="w-3 h-3" />
                                <span className="text-xs font-semibold">AI Assistant</span>
                              </div>
                            )}
                            <p className="text-sm leading-relaxed">{msg.text}</p>
                            <p className="text-xs opacity-70 mt-1">
                              {msg.timestamp.toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </p>
                          </div>
                        </div>
                      ))}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="flex gap-2 pt-3 border-t">
                      <Input
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your question..."
                        className="flex-1"
                      />
                      <Button
                        onClick={sendMessage}
                        size="icon"
                        disabled={!inputMessage.trim() || isLoading}
                        className="shrink-0"
                      >
                        {isLoading ? (
                          <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                ) : (
                  // Static FAQ Answer
                  <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                    <h4 className="font-semibold text-foreground mb-2">
                      {faqs.find((f) => f.id === selectedFaq)?.question}
                    </h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {faqs.find((f) => f.id === selectedFaq)?.answer}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <p className="text-xs text-center text-muted-foreground">
            Need more help?{" "}
            <a href="#" className="text-primary hover:underline">
              Contact our team
            </a>
          </p>
        </div>
      </div>
    </>
  );
}
