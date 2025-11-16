import { useState, useEffect } from "react";
import { BookOpen, Calendar, LayoutDashboard, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Link, useNavigate } from "react-router-dom";
import DashboardView from "@/components/DashboardView";
import NotesView from "@/components/NotesView";
import TestsView from "@/components/TestsView";
import { supabase } from "@/integrations/supabase/client";
import { User, Session } from '@supabase/supabase-js';
import { toast } from "sonner";

export interface Note {
  id: string;
  subject: string;
  title: string;
  content: string;
  createdAt: Date;
}

export interface Test {
  id: string;
  subject: string;
  date: Date;
  topics: string[];
}

interface StudyPlanRecord {
  id: string;
  subject: string;
  test_date: string;
  total_study_hours: number;
  created_at: string;
  plan_data: any;
}

const Index = () => {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [tests, setTests] = useState<Test[]>([]);
  const [activePlans, setActivePlans] = useState<StudyPlanRecord[]>([]);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isBookOpen, setIsBookOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loadingPlans, setLoadingPlans] = useState(true);

  useEffect(() => {
    // Animate book opening on page load - starts closed
    const timer = setTimeout(() => {
      setIsBookOpen(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

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
      fetchActivePlans();
      fetchNotes();
    }
  }, [user]);

  const fetchNotes = async () => {
    try {
      const { data, error } = await supabase
        .from('notes')
        .select('*')
        .eq('archived', false)
        .order('created_at', { ascending: false });

      if (error) throw error;
      
      const formattedNotes: Note[] = (data || []).map(note => ({
        id: note.id,
        subject: note.subject,
        title: note.title,
        content: note.content,
        createdAt: new Date(note.created_at)
      }));
      
      setNotes(formattedNotes);
    } catch (error: any) {
      console.error("Error fetching notes:", error);
      toast.error("Failed to load notes");
    }
  };

  const fetchActivePlans = async () => {
    setLoadingPlans(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const { data, error } = await supabase
        .from('study_plans')
        .select('*')
        .eq('completed', false)
        .gte('test_date', today)
        .order('test_date', { ascending: true });

      if (error) throw error;
      setActivePlans(data || []);
    } catch (error: any) {
      console.error("Error fetching active plans:", error);
      toast.error("Failed to load study plans");
    } finally {
      setLoadingPlans(false);
    }
  };

  const handleDeletePlan = async (id: string) => {
    try {
      const { error } = await supabase
        .from('study_plans')
        .delete()
        .eq('id', id);

      if (error) throw error;
      
      setActivePlans(activePlans.filter(p => p.id !== id));
      toast.success("Study plan deleted");
    } catch (error: any) {
      console.error("Error deleting plan:", error);
      toast.error("Failed to delete plan");
    }
  };

  const handleMarkAsAchieved = async (id: string) => {
    try {
      const { error } = await supabase
        .from('study_plans')
        .update({ completed: true })
        .eq('id', id);

      if (error) throw error;
      
      setActivePlans(activePlans.filter(p => p.id !== id));
      toast.success("Congratulations! Plan marked as achieved!");
    } catch (error: any) {
      console.error("Error marking plan as achieved:", error);
      toast.error("Failed to mark plan as achieved");
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const addNote = async (note: Omit<Note, "id" | "createdAt">) => {
    try {
      const { error } = await supabase
        .from('notes')
        .insert({
          subject: note.subject,
          title: note.title,
          content: note.content,
          user_id: user?.id,
          archived: false
        });

      if (error) throw error;
      
      await fetchNotes();
      toast.success("Note added successfully");
    } catch (error: any) {
      console.error("Error adding note:", error);
      toast.error("Failed to add note");
    }
  };

  const addTest = (test: Omit<Test, "id">) => {
    const newTest: Test = {
      ...test,
      id: Math.random().toString(36).substr(2, 9),
    };
    setTests([...tests, newTest]);
  };

  const editNote = async (id: string, updatedNote: Omit<Note, "id" | "createdAt">) => {
    try {
      const { error } = await supabase
        .from('notes')
        .update({
          subject: updatedNote.subject,
          title: updatedNote.title,
          content: updatedNote.content
        })
        .eq('id', id);

      if (error) throw error;
      
      await fetchNotes();
      toast.success("Note updated successfully");
    } catch (error: any) {
      console.error("Error updating note:", error);
      toast.error("Failed to update note");
    }
  };

  const archiveNote = async (id: string) => {
    try {
      const { error } = await supabase
        .from('notes')
        .update({ archived: true })
        .eq('id', id);

      if (error) throw error;
      
      await fetchNotes();
      toast.success("Note moved to history");
    } catch (error: any) {
      console.error("Error archiving note:", error);
      toast.error("Failed to archive note");
    }
  };

  const deleteTest = (id: string) => {
    setTests(tests.filter((test) => test.id !== id));
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

      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-2xl mx-auto grid-cols-3 h-auto p-1">
            <TabsTrigger value="dashboard" className="gap-2 py-3">
              <LayoutDashboard className="w-4 h-4" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="notes" className="gap-2 py-3">
              <BookOpen className="w-4 h-4" />
              <span className="hidden sm:inline">Notes</span>
            </TabsTrigger>
            <TabsTrigger value="tests" className="gap-2 py-3">
              <Calendar className="w-4 h-4" />
              <span className="hidden sm:inline">Tests</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <DashboardView 
              notes={notes} 
              tests={tests} 
              activePlans={activePlans}
              loadingPlans={loadingPlans}
              onDeletePlan={handleDeletePlan}
              onMarkAsAchieved={handleMarkAsAchieved}
            />
          </TabsContent>

          <TabsContent value="notes" className="space-y-6">
            <NotesView notes={notes} onAddNote={addNote} onEditNote={editNote} onArchiveNote={archiveNote} />
          </TabsContent>

          <TabsContent value="tests" className="space-y-6">
            <TestsView tests={tests} onAddTest={addTest} onDeleteTest={deleteTest} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
