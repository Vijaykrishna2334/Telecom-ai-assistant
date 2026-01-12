import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { API_ENDPOINTS } from "@/config/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  sessionId: string;
}

const ChatInterface = ({ sessionId }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your TelecomAI assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    // Create placeholder for streaming response
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    const messageContent = inputValue;
    setInputValue("");
    setIsTyping(true);

    // Streaming API call to backend
    try {
      const response = await fetch(API_ENDPOINTS.CHAT_STREAM, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: messageContent,
          session_id: sessionId,
          history: messages.map((m) => ({ role: m.role, content: m.content })),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      // Read the stream
      let buffer = "";

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          // Process any remaining buffer
          if (buffer.trim()) {
            const lines = buffer.split("\n");
            for (const line of lines) {
              if (line.trim().startsWith("data:")) {
                processLine(line);
              }
            }
          }
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // Process complete lines
        const lines = buffer.split("\n");
        // Keep the last partial line in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          processLine(line);
        }
      }

      function processLine(line: string) {
        if (!line.trim() || !line.startsWith("data:")) return;

        try {
          const jsonStr = line.slice(5).trim(); // Remove "data:" prefix
          if (!jsonStr) return;
          if (jsonStr === "[DONE]") return; // Handle standard SSE done signal if present

          const data = JSON.parse(jsonStr);

          if (data.token) {
            // Update message content with new token
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMessageId
                  ? { ...m, content: m.content + data.token }
                  : m
              )
            );
          }

          if (data.error) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMessageId
                  ? { ...m, content: m.content + "\n\nError: " + data.error }
                  : m
              )
            );
          }
        } catch (parseError) {
          // Skip malformed JSON lines
          console.warn("Failed to parse SSE data:", line);
        }
      }
    } catch (error) {
      // Update the placeholder message with error
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessageId
            ? { ...m, content: "I'm having trouble connecting to the server. Please try again later." }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            style={{ animation: `slide-in 0.3s ease-out forwards`, animationDelay: `${index * 0.05}s` }}
          >
            <div
              className={`max-w-[80%] md:max-w-[60%] p-4 rounded-2xl ${message.role === "user"
                ? "bg-primary text-primary-foreground rounded-br-md"
                : "glass rounded-bl-md"
                }`}
            >
              <div className="text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Style tables
                    table: ({ node, ...props }) => (
                      <div className="overflow-x-auto my-4 rounded-lg border border-border/50 bg-background/50">
                        <table className="w-full text-sm text-left" {...props} />
                      </div>
                    ),
                    thead: ({ node, ...props }) => (
                      <thead className="text-xs uppercase bg-secondary/50 text-secondary-foreground font-semibold" {...props} />
                    ),
                    th: ({ node, ...props }) => (
                      <th className="px-4 py-3 whitespace-nowrap border-b border-border/50" {...props} />
                    ),
                    td: ({ node, ...props }) => (
                      <td className="px-4 py-3 border-b border-border/50 last:border-0" {...props} />
                    ),
                    // Style lists
                    ul: ({ node, ...props }) => (
                      <ul className="list-disc pl-5 space-y-1 my-2" {...props} />
                    ),
                    ol: ({ node, ...props }) => (
                      <ol className="list-decimal pl-5 space-y-1 my-2" {...props} />
                    ),
                    // Style bold
                    strong: ({ node, ...props }) => (
                      <strong className="font-bold text-primary" {...props} />
                    ),
                    // Style links
                    a: ({ node, ...props }) => (
                      <a className="text-primary underline underline-offset-4 hover:text-primary/80 transition-colors" target="_blank" rel="noopener noreferrer" {...props} />
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
              <span className={`text-xs mt-2 block ${message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="glass p-4 rounded-2xl rounded-bl-md">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-typing-dot" />
                <span className="w-2 h-2 bg-primary rounded-full animate-typing-dot" style={{ animationDelay: "0.2s" }} />
                <span className="w-2 h-2 bg-primary rounded-full animate-typing-dot" style={{ animationDelay: "0.4s" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
            />
          </div>
          <Button
            variant="glow"
            size="icon"
            onClick={sendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="shrink-0"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
