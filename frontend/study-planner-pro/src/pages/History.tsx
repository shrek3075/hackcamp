import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Trash2, Calendar, Clock, BookOpen, Loader2, LogOut, Trophy, RotateCcw } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { format } from "date-fns";
import { User, Session } from '@supabase/supabase-js';

interface StudyPlanRecord {
  id: string;
  subject: string;
  test_date: string;
  total_study_hours: number;
  created_at: string;
  plan_data: any;
  completed: boolean;
}

interface ArchivedNote {
  id: string;
  subject: string;
  title: string;
  content: string;
  created_at: string;
}

interface CompletedTopic {
  id: string;
  subject: string;
  topic_name: string;
  unit_topic: string;
  created_at: string;
  achieved: boolean;
}

const History = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState<StudyPlanRecord[]>([]);
  const [archivedNotes, setArchivedNotes] = useState<ArchivedNote[]>([]);
  const [completedTopics, setCompletedTopics] = useState<CompletedTopic[]>([]);
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
      fetchPastPlans();
      fetchArchivedNotes();
      fetchCompletedTopics();
    }
  }, [user]);

  const fetchArchivedNotes = async () => {
    try {
      const { data, error } = await supabase
        .from('notes')
        .select('*')
        .eq('archived', true)
        .order('updated_at', { ascending: false });

      if (error) throw error;
      setArchivedNotes(data || []);
    } catch (error: any) {
      console.error("Error fetching archived notes:", error);
      toast.error("Failed to load archived notes");
    }
  };

  const fetchCompletedTopics = async () => {
    try {
      const { data, error } = await supabase
        .from('topic_achievements')
        .select('*')
        .eq('achieved', true)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setCompletedTopics(data || []);
    } catch (error: any) {
      console.error("Error fetching completed topics:", error);
      toast.error("Failed to load completed topics");
    }
  };

  const fetchPastPlans = async () => {
    setLoading(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const { data, error } = await supabase
        .from('study_plans')
        .select('*')
        .or(`completed.eq.true,test_date.lt.${today}`)
        .order('test_date', { ascending: false });

      if (error) throw error;
      setPlans(data || []);
    } catch (error: any) {
      console.error("Error fetching plans:", error);
      toast.error("Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const { error } = await supabase
        .from('study_plans')
        .delete()
        .eq('id', id);

      if (error) throw error;
      
      setPlans(plans.filter(p => p.id !== id));
      toast.success("Study plan deleted");
    } catch (error: any) {
      console.error("Error deleting plan:", error);
      toast.error("Failed to delete plan");
    }
  };

  const handleDeleteNote = async (id: string) => {
    try {
      const { error } = await supabase
        .from('notes')
        .delete()
        .eq('id', id);

      if (error) throw error;
      
      setArchivedNotes(archivedNotes.filter(n => n.id !== id));
      toast.success("Note permanently deleted");
    } catch (error: any) {
      console.error("Error deleting note:", error);
      toast.error("Failed to delete note");
    }
  };

  const handleRestorePlan = async (id: string) => {
    try {
      const { error } = await supabase
        .from('study_plans')
        .update({ completed: false })
        .eq('id', id);

      if (error) throw error;
      
      setPlans(plans.filter(p => p.id !== id));
      toast.success("Study plan restored to active plans");
    } catch (error: any) {
      console.error("Error restoring plan:", error);
      toast.error("Failed to restore plan");
    }
  };

  const handleRestoreNote = async (id: string) => {
    try {
      const { error } = await supabase
        .from('notes')
        .update({ archived: false })
        .eq('id', id);

      if (error) throw error;
      
      setArchivedNotes(archivedNotes.filter(n => n.id !== id));
      toast.success("Note restored to active notes");
    } catch (error: any) {
      console.error("Error restoring note:", error);
      toast.error("Failed to restore note");
    }
  };

  const handleDeleteTopic = async (id: string) => {
    try {
      const { error } = await supabase
        .from('topic_achievements')
        .delete()
        .eq('id', id);

      if (error) throw error;
      
      setCompletedTopics(completedTopics.filter(t => t.id !== id));
      toast.success("Topic achievement deleted");
    } catch (error: any) {
      console.error("Error deleting topic:", error);
      toast.error("Failed to delete topic");
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  return (
    <div className="min-h-screen bg-[#d4b896]">
      {/* Navigation Bar */}
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
          <Link to="/mindmap" className="hover:opacity-80 transition-opacity">Mindmap</Link>
          <Link to="/progress" className="hover:opacity-80 transition-opacity">Progress</Link>
          <Link to="/ai-tutor" className="hover:opacity-80 transition-opacity">AI Tutor</Link>
          <Link to="/history" className="hover:opacity-80 transition-opacity font-semibold">History</Link>
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
        <h1 className="text-4xl font-bold text-[#3d2817] mb-4">History</h1>
        <p className="text-[#5c4033] mb-8">View your completed study plans and archived notes.</p>

        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
              <p className="text-muted-foreground">Loading history...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-12">
            {/* Completed Study Plans */}
            <div>
              <h2 className="text-2xl font-semibold text-[#3d2817] mb-4">Completed Study Plans</h2>
              {plans.length === 0 ? (
                <Card className="bg-card">
                  <CardContent className="p-8 text-center">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">No past study plans yet.</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {plans.map((plan) => (
                    <Card key={plan.id} className="bg-card hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <span className="truncate">{plan.subject}</span>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRestorePlan(plan.id)}
                              className="text-primary hover:text-primary hover:bg-primary/10"
                              title="Restore to active plans"
                            >
                              <RotateCcw className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(plan.id)}
                              className="text-destructive hover:text-destructive hover:bg-destructive/10"
                              title="Delete permanently"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="w-4 h-4 text-muted-foreground" />
                          <span>Test Date: {format(new Date(plan.test_date), "MMM dd, yyyy")}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-muted-foreground" />
                          <span>Total: {plan.total_study_hours} hours</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <BookOpen className="w-4 h-4 text-muted-foreground" />
                          <span>Created: {format(new Date(plan.created_at), "MMM dd, yyyy")}</span>
                        </div>
                        {plan.completed && (
                          <Badge className="bg-green-500">
                            <Trophy className="w-3 h-3 mr-1" />
                            Completed
                          </Badge>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Completed Topics/Sessions */}
            <div>
              <h2 className="text-2xl font-semibold text-[#3d2817] mb-4">Completed Study Sessions</h2>
              {completedTopics.length === 0 ? (
                <Card className="bg-card">
                  <CardContent className="p-8 text-center">
                    <Trophy className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">No completed sessions yet.</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {completedTopics.map((topic) => (
                    <Card key={topic.id} className="bg-card hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between text-base">
                          <span className="truncate">{topic.topic_name}</span>
                          <Trophy className="w-4 h-4 text-primary flex-shrink-0" />
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 mb-4">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <BookOpen className="w-4 h-4" />
                            <span>{topic.subject}</span>
                          </div>
                          {topic.unit_topic && (
                            <p className="text-sm text-muted-foreground">{topic.unit_topic}</p>
                          )}
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            <span>{format(new Date(topic.created_at), "MMM d, yyyy")}</span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteTopic(topic.id)}
                            className="flex-1"
                          >
                            <Trash2 className="w-4 h-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Archived Notes */}
            <div>
              <h2 className="text-2xl font-semibold text-[#3d2817] mb-4">Archived Notes</h2>
              {archivedNotes.length === 0 ? (
                <Card className="bg-card">
                  <CardContent className="p-8 text-center">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">No archived notes yet.</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {archivedNotes.map((note) => (
                    <Card key={note.id} className="bg-card hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <span className="truncate">{note.title}</span>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRestoreNote(note.id)}
                              className="text-primary hover:text-primary hover:bg-primary/10"
                              title="Restore to active notes"
                            >
                              <RotateCcw className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteNote(note.id)}
                              className="text-destructive hover:text-destructive hover:bg-destructive/10"
                              title="Delete permanently"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <Badge variant="outline">{note.subject}</Badge>
                        <p className="text-sm text-muted-foreground line-clamp-3">{note.content}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Calendar className="w-3 h-3" />
                          <span>Archived: {format(new Date(note.created_at), "MMM dd, yyyy")}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
