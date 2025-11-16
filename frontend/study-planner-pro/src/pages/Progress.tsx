import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, LogOut, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { User, Session } from '@supabase/supabase-js';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface SubjectProgress {
  subject: string;
  totalTopics: number;
  achievedTopics: number;
  percentage: number;
}

const Progress = () => {
  const navigate = useNavigate();
  const [progressData, setProgressData] = useState<SubjectProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);

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
      fetchProgress();
    }
  }, [user]);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      // Fetch all active study plans with their plan data
      const { data: plans, error: plansError } = await supabase
        .from('study_plans')
        .select('subject, topic, plan_data')
        .eq('completed', false);

      if (plansError) throw plansError;

      // Calculate progress based on study plan sessions
      const subjectMap = new Map<string, { total: number; achieved: number }>();

      plans?.forEach(plan => {
        const key = plan.topic ? `${plan.subject} - ${plan.topic}` : plan.subject;
        
        if (!subjectMap.has(key)) {
          subjectMap.set(key, { total: 0, achieved: 0 });
        }

        // Count sessions from plan_data
        const planData = plan.plan_data as any;
        if (planData?.dailyPlans) {
          planData.dailyPlans.forEach((day: any) => {
            if (day.sessions) {
              day.sessions.forEach((session: any) => {
                const current = subjectMap.get(key)!;
                current.total++;
                if (session.completed) {
                  current.achieved++;
                }
              });
            }
          });
        }
      });

      // Convert to array
      const progress: SubjectProgress[] = Array.from(subjectMap.entries()).map(([subject, data]) => ({
        subject,
        totalTopics: data.total,
        achievedTopics: data.achieved,
        percentage: data.total > 0 ? Math.round((data.achieved / data.total) * 100) : 0
      }));

      setProgressData(progress);
    } catch (error: any) {
      console.error("Error fetching progress:", error);
      toast.error("Failed to load progress data");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];

  return (
    <div className="min-h-screen bg-[#d4b896]">
      {/* Navigation Bar */}
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
          <Link to="/mindmap" className="hover:opacity-80 transition-opacity">Mindmap</Link>
          <Link to="/progress" className="hover:opacity-80 transition-opacity font-semibold">Progress</Link>
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
        <div className="flex items-center gap-3 mb-8">
          <TrendingUp className="w-10 h-10 text-[#3d2817]" />
          <div>
            <h1 className="text-4xl font-bold text-[#3d2817]">Study Progress</h1>
            <p className="text-[#5c4033]">Track your learning achievements by subject</p>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
              <p className="text-muted-foreground">Loading progress...</p>
            </div>
          </div>
        ) : progressData.length === 0 ? (
          <Card className="bg-card">
            <CardContent className="p-8 text-center">
              <TrendingUp className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">No progress data yet. Start marking topics as achieved in the Mindmap!</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {progressData.map((subjectProgress, index) => {
              const chartData = [
                { name: 'Achieved', value: subjectProgress.achievedTopics },
                { name: 'Remaining', value: subjectProgress.totalTopics - subjectProgress.achievedTopics }
              ];

              return (
                <Card key={index} className="bg-card hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{subjectProgress.subject}</span>
                      <Badge 
                        variant={subjectProgress.percentage >= 80 ? "default" : subjectProgress.percentage >= 50 ? "secondary" : "outline"}
                        className="text-lg px-3 py-1"
                      >
                        {subjectProgress.percentage}%
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">
                          {subjectProgress.achievedTopics} of {subjectProgress.totalTopics} topics achieved
                        </span>
                      </div>
                      
                      {subjectProgress.totalTopics > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>
                          <PieChart>
                            <Pie
                              data={chartData}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                              outerRadius={80}
                              fill="#8884d8"
                              dataKey="value"
                            >
                              <Cell fill="#10b981" />
                              <Cell fill="#e5e7eb" />
                            </Pie>
                            <Tooltip />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="text-center text-muted-foreground py-8">
                          No topics tracked yet
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Progress;
