import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LogOut, Send, Bot, User, Loader2, BookOpen } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { User as SupabaseUser, Session } from '@supabase/supabase-js';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import ReactMarkdown from 'react-markdown';

type Message = { role: "user" | "assistant"; content: string };

interface StudyPlan {
  id: string;
  subject: string;
  topic: string;
  test_date: string;
  plan_data: any;
}


const AITutor = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<SupabaseUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI Tutor powered by OpenAI. Select a study plan above to get personalized help based on your current learning goals. Ask me anything about your studies!"
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [studyPlans, setStudyPlans] = useState<StudyPlan[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<string>("");
  const CHAT_URL = "http://localhost:3001/ai-tutor";

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);

        if (!session?.user) {
          setTimeout(() => {
            navigate("/auth");
          }, 0);
        }
      }
    );

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (!session?.user) {
        navigate("/auth");
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  useEffect(() => {
    if (user) {
      fetchStudyPlans();
    }
  }, [user]);

  const fetchStudyPlans = async () => {
    try {
      const { data, error } = await supabase
        .from('study_plans')
        .select('*')
        .eq('completed', false)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setStudyPlans(data || []);
    } catch (error: any) {
      console.error("Error fetching study plans:", error);
      toast.error("Failed to load study plans");
    }
  };


  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const sendMessage = async (userMessage: string) => {
    const userMsg: Message = { role: "user", content: userMessage };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Get selected plan data
      const selectedPlan = studyPlans.find(plan => plan.id === selectedPlanId);

      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...messages, userMsg],
          notes: [],
          planData: selectedPlan
        }),
      });

      if (!resp.ok) {
        const errorData = await resp.json();
        if (resp.status === 429) {
          toast.error("Rate limit exceeded. Please wait a moment and try again.");
        } else if (resp.status === 402) {
          toast.error("AI usage limit reached. Please contact support.");
        } else {
          toast.error(errorData.error || "Failed to get response");
        }
        setIsLoading(false);
        return;
      }

      const data = await resp.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.response
      };

      setMessages(prev => [...prev, assistantMsg]);
      setIsLoading(false);
    } catch (error) {
      console.error("Chat error:", error);
      toast.error("Failed to send message. Please try again.");
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const messageText = input.trim();
    setInput("");
    await sendMessage(messageText);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-[#d4b896]">
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
          <Link to="/mindmap" className="hover:opacity-80 transition-opacity">Mindmap</Link>
          <Link to="/progress" className="hover:opacity-80 transition-opacity">Progress</Link>
          <Link to="/ai-tutor" className="hover:opacity-80 transition-opacity font-semibold">AI Tutor</Link>
          <Link to="/history" className="hover:opacity-80 transition-opacity">History</Link>
        </div>
        <Button 
          onClick={handleLogout}
          variant="ghost"
          className="hover:opacity-80 transition-opacity text-white hover:bg-[#4a3329]"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Log Out
        </Button>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-[#3d2817] mb-2">AI Tutor (OpenAI)</h1>
          <p className="text-[#5c4033]">Select a study plan to get personalized, contextual help with your studies!</p>
        </div>

        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1 max-w-md">
            <Label className="text-sm font-semibold whitespace-nowrap">Study Plan:</Label>
            <Select value={selectedPlanId} onValueChange={setSelectedPlanId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a study plan" />
              </SelectTrigger>
              <SelectContent>
                {studyPlans.map(plan => (
                  <SelectItem key={plan.id} value={plan.id}>
                    {plan.subject} - {plan.topic}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedPlanId && (
              <Button
                variant="ghost"
                size="sm"
                className="text-xs"
                onClick={() => setSelectedPlanId("")}
              >
                Clear
              </Button>
            )}
          </div>
        </div>

        <Card className="h-[calc(100vh-280px)] flex flex-col overflow-hidden">
              <CardHeader className="border-b flex-shrink-0">
                <CardTitle className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-primary" />
                  Chat with AI Tutor
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col p-0 overflow-hidden min-h-0">
                <ScrollArea className="flex-1 p-4" ref={scrollRef}>
                  <div className="space-y-4">
                    {messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        {msg.role === "assistant" && (
                          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                            <Bot className="w-5 h-5 text-white" />
                          </div>
                        )}
                        <div
                          className={`max-w-[80%] rounded-lg p-4 ${
                            msg.role === "user"
                              ? "bg-[#5c4033] text-white"
                              : "bg-secondary text-foreground"
                          }`}
                        >
                          {msg.role === "assistant" ? (
                            <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-bold prose-headings:mt-4 prose-headings:mb-2 prose-h3:text-lg prose-p:my-2 prose-ul:my-2 prose-li:my-1 prose-strong:font-semibold">
                              <ReactMarkdown>{msg.content}</ReactMarkdown>
                            </div>
                          ) : (
                            <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                          )}
                        </div>
                        {msg.role === "user" && (
                          <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
                            <User className="w-5 h-5 text-white" />
                          </div>
                        )}
                      </div>
                    ))}
                    {isLoading && messages[messages.length - 1]?.role === "user" && (
                      <div className="flex gap-3 justify-start">
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                          <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div className="bg-secondary rounded-lg p-3">
                          <Loader2 className="w-5 h-5 animate-spin text-primary" />
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>

                <div className="border-t p-4 flex-shrink-0">
                  <div className="flex gap-2">
                    <Input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask your question here..."
                      disabled={isLoading}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSend}
                      disabled={isLoading || !input.trim()}
                      className="bg-[#5c4033] hover:bg-[#4a3329]"
                    >
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
      </div>
    </div>
  );
};

export default AITutor;
