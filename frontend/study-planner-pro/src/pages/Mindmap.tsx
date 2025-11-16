import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Network, LogOut, CheckCircle, TrendingUp } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { User, Session } from '@supabase/supabase-js';
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Topic {
  name: string;
  subtopics: string[];
  description: string;
}

interface FlowchartData {
  subject: string;
  mainTopics: Topic[];
  summary: string;
}

interface StudyPlanRecord {
  id: string;
  subject: string;
  syllabus_content: string;
  plan_data: any;
}

const Mindmap = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const planId = searchParams.get('planId');
  
  // Multi-plan state
  const [allPlans, setAllPlans] = useState<StudyPlanRecord[]>([]);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const currentPlan = allPlans.find((p) => p.id === activePlanId) ?? allPlans[0] ?? null;
  
  const [flowchartData, setFlowchartData] = useState<FlowchartData | null>(null);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [achievements, setAchievements] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // Set up auth state listener
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

    // Check for existing session
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
      loadAllPlans();
      fetchAchievements();
    }
  }, [user]);

  // Load mindmap when active plan changes
  useEffect(() => {
    if (currentPlan) {
      generateFlowchart(currentPlan.subject, currentPlan.syllabus_content || '');
    }
  }, [activePlanId]);

  const fetchAchievements = async () => {
    try {
      const { data, error } = await supabase
        .from('topic_achievements')
        .select('*');

      if (error) throw error;

      const achievementsMap: Record<string, boolean> = {};
      data?.forEach(achievement => {
        achievementsMap[achievement.topic_name] = achievement.achieved;
      });
      setAchievements(achievementsMap);
    } catch (error: any) {
      console.error("Error fetching achievements:", error);
    }
  };

  const loadAllPlans = async () => {
    setLoading(true);
    
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const { data: plans, error: fetchError } = await supabase
        .from('study_plans')
        .select('id, subject, syllabus_content, plan_data')
        .eq('completed', false)
        .gte('test_date', today)
        .order('created_at', { ascending: false });

      if (fetchError) throw fetchError;

      if (plans && plans.length > 0) {
        setAllPlans(plans);
        
        // Set active plan: use planId from URL if available, otherwise first plan
        const targetPlanId = planId || plans[0].id;
        setActivePlanId(targetPlanId);
        
        const targetPlan = plans.find(p => p.id === targetPlanId) || plans[0];
        await generateFlowchart(targetPlan.subject, targetPlan.syllabus_content || '');
      } else {
        setAllPlans([]);
        toast.error("No active study plans found. Create one from the Details page.");
      }
    } catch (err) {
      console.error("Error loading plans:", err);
      toast.error("Failed to load study plans");
    } finally {
      setLoading(false);
    }
  };

  const generateFlowchart = async (subject: string, syllabusContent: string) => {
    setLoading(true);
    
    try {
      const { data, error: functionError } = await supabase.functions.invoke('generate-study-recommendations', {
        body: {
          subject,
          syllabusContent,
          type: 'flowchart'
        }
      });

      if (functionError) throw functionError;

      if (data?.error) {
        if (data.error.includes("Rate limits")) {
          toast.error("Too many requests. Please wait a moment and try again.");
        } else if (data.error.includes("Payment required")) {
          toast.error("AI usage limit reached. Please contact support.");
        } else {
          toast.error("Failed to generate mindmap");
        }
        return;
      }

      setFlowchartData(data.flowchart);
    } catch (err) {
      console.error("Error generating flowchart:", err);
      toast.error("Failed to generate mindmap");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const toggleAchievement = async (topicName: string, currentState: boolean) => {
    if (!flowchartData || !user) return;

    try {
      const { error } = await supabase
        .from('topic_achievements')
        .upsert({
          user_id: user.id,
          subject: flowchartData.subject,
          topic_name: topicName,
          achieved: !currentState
        }, {
          onConflict: 'user_id,subject,topic_name'
        });

      if (error) throw error;

      setAchievements(prev => ({
        ...prev,
        [topicName]: !currentState
      }));

      toast.success(!currentState ? "Topic marked as achieved!" : "Achievement removed");
    } catch (error: any) {
      console.error("Error toggling achievement:", error);
      toast.error("Failed to update achievement");
    }
  };

  return (
    <div className="min-h-screen bg-[#d4b896]">
      {/* Navigation Bar */}
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
          <Link to="/mindmap" className="hover:opacity-80 transition-opacity font-semibold">Mindmap</Link>
          <Link to="/progress" className="hover:opacity-80 transition-opacity">Progress</Link>
          <Link to="/ai-tutor" className="hover:opacity-80 transition-opacity">AI Tutor</Link>
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

      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-[#3d2817] mb-4">Topic Mindmap</h1>
        <p className="text-[#5c4033] mb-4">Visual overview of your study topics</p>

        {/* Subject Switcher (only show if multiple plans) */}
        {allPlans.length > 1 && (
          <div className="mb-6 flex gap-3 items-center">
            <span className="text-sm font-semibold text-[#3d2817]">Select Subject:</span>
            <div className="flex gap-2 flex-wrap">
              {allPlans.map((plan) => (
                <button
                  key={plan.id}
                  onClick={() => setActivePlanId(plan.id)}
                  className={`px-4 py-2 rounded-full border transition-colors ${
                    plan.id === (currentPlan?.id ?? null)
                      ? "bg-[#5c4033] text-white border-[#5c4033]"
                      : "bg-white text-[#3d2817] border-gray-300 hover:border-[#5c4033]"
                  }`}
                >
                  {plan.subject}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
              <p className="text-muted-foreground">Generating mindmap...</p>
            </div>
          </div>
        ) : !flowchartData ? (
          <Card className="bg-card">
            <CardContent className="p-8 text-center">
              <Network className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">
                No active study plan found. Generate a study plan first to see the mindmap.
              </p>
              <Link to="/details">
                <Button>Go to Details</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="w-5 h-5" />
                {flowchartData.subject} - Topic Structure
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Progress Section */}
              {(() => {
                // Calculate progress based on completed sessions in study plan (same as Progress page)
                let totalSessions = 0;
                let completedSessions = 0;

                if (currentPlan?.plan_data?.dailyPlans) {
                  currentPlan.plan_data.dailyPlans.forEach((day: any) => {
                    if (day.sessions) {
                      day.sessions.forEach((session: any) => {
                        totalSessions++;
                        if (session.completed) {
                          completedSessions++;
                        }
                      });
                    }
                  });
                }

                const totalTopics = totalSessions;
                const achievedTopics = completedSessions;
                const percentage = totalTopics > 0 ? Math.round((achievedTopics / totalTopics) * 100) : 0;

                return (
                  <div className="mb-6 p-5 bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg border-2 border-primary/20">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-primary" />
                        <h3 className="font-semibold text-lg">Progress Tracker</h3>
                      </div>
                      <Badge 
                        variant={percentage >= 80 ? "default" : percentage >= 50 ? "secondary" : "outline"}
                        className="text-lg px-4 py-1"
                      >
                        {percentage}%
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>{achievedTopics} of {totalTopics} sessions completed</span>
                        <span>{totalTopics - achievedTopics} remaining</span>
                      </div>
                      <Progress value={percentage} className="h-3" />
                      {percentage === 100 && (
                        <div className="mt-3 p-2 bg-green-500/10 border border-green-500/20 rounded text-center">
                          <span className="text-green-700 font-semibold">🎉 All sessions completed!</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}

              <div className="mb-6 p-4 bg-secondary/50 rounded-lg">
                <h3 className="font-semibold mb-2">Summary</h3>
                <p className="text-muted-foreground">{flowchartData.summary}</p>
              </div>

              <div className="space-y-6">
                {flowchartData.mainTopics.map((topic, index) => (
                  <div key={index} className="relative">
                    {/* Main Topic Node */}
                    <div className={cn(
                      "p-4 rounded-lg shadow-md mb-4 transition-colors",
                      achievements[topic.name] 
                        ? "bg-green-600 text-white" 
                        : "bg-primary text-primary-foreground"
                    )}>
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="font-bold text-lg">{topic.name}</h3>
                          <p className="text-sm mt-2 opacity-90">{topic.description}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Checkbox
                            checked={achievements[topic.name] || false}
                            onCheckedChange={() => toggleAchievement(topic.name, achievements[topic.name] || false)}
                            className={cn(
                              achievements[topic.name]
                                ? "border-white data-[state=checked]:bg-white data-[state=checked]:border-white data-[state=checked]:text-green-600"
                                : "border-primary-foreground data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500"
                            )}
                          />
                          {achievements[topic.name] && (
                            <CheckCircle className="w-5 h-5 text-white" />
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Subtopics */}
                    <div className="ml-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                      {topic.subtopics.map((subtopic, subIndex) => (
                        <div key={subIndex} className="relative">
                          {/* Connection Line */}
                          <div className="absolute -left-8 top-1/2 w-8 h-0.5 bg-border" />
                          
                          {/* Subtopic Node */}
                          <div className={cn(
                            "border-2 p-3 rounded-lg transition-colors",
                            achievements[subtopic]
                              ? "bg-green-500 border-green-600 text-white"
                              : "bg-accent/10 border-accent hover:bg-accent/20"
                          )}>
                            <div className="flex items-center justify-between gap-2">
                              <p className="text-sm font-medium flex-1">{subtopic}</p>
                              <div className="flex items-center gap-2">
                                <Checkbox
                                  checked={achievements[subtopic] || false}
                                  onCheckedChange={() => toggleAchievement(subtopic, achievements[subtopic] || false)}
                                  className={cn(
                                    achievements[subtopic]
                                      ? "border-white data-[state=checked]:bg-white data-[state=checked]:border-white data-[state=checked]:text-green-600"
                                      : "border-accent data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500"
                                  )}
                                />
                                {achievements[subtopic] && (
                                  <CheckCircle className="w-4 h-4 text-white" />
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Connector to next topic */}
                    {index < flowchartData.mainTopics.length - 1 && (
                      <div className="w-0.5 h-8 bg-border mx-auto my-4" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Mindmap;
