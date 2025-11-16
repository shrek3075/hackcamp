import { Note, Test } from "@/pages/Index";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar, BookOpen, Clock, Sparkles, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { format, differenceInDays, addDays } from "date-fns";
import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

interface TimelineViewProps {
  notes: Note[];
  tests: Test[];
}

interface StudySession {
  date: Date;
  subject: string;
  topics: string[];
  notesCount: number;
  daysUntilTest: number;
  recommendedHours: number;
}

const TimelineView = ({ notes, tests }: TimelineViewProps) => {
  const [recommendations, setRecommendations] = useState<Record<string, string>>({});
  const [loadingSubject, setLoadingSubject] = useState<string | null>(null);

  const generateRecommendations = async (subject: string) => {
    if (loadingSubject) return; // Prevent multiple simultaneous requests
    
    const subjectNotes = notes.filter(note => note.subject === subject);
    if (subjectNotes.length === 0) {
      toast.error("No notes found for this subject");
      return;
    }

    setLoadingSubject(subject);
    try {
      const { data, error } = await supabase.functions.invoke('generate-study-recommendations', {
        body: { notes: subjectNotes, subject }
      });

      if (error) {
        throw error;
      }

      if (data?.error) {
        if (data.error.includes("Rate limits")) {
          toast.error("Too many requests. Please wait a moment and try again.");
        } else if (data.error.includes("Payment required")) {
          toast.error("AI usage limit reached. Please contact support.");
        } else {
          toast.error("Failed to generate recommendations");
        }
        return;
      }

      setRecommendations(prev => ({
        ...prev,
        [subject]: data.recommendations
      }));
      toast.success("Study recommendations generated!");
    } catch (error) {
      console.error("Error generating recommendations:", error);
      toast.error("Failed to generate recommendations");
    } finally {
      setLoadingSubject(null);
    }
  };
  const generateTimeline = (): StudySession[] => {
    const timeline: StudySession[] = [];
    const today = new Date();

    tests
      .filter((test) => differenceInDays(test.date, today) >= 0)
      .sort((a, b) => a.date.getTime() - b.date.getTime())
      .forEach((test) => {
        const daysUntilTest = differenceInDays(test.date, today);
        const studyDays = Math.max(Math.floor(daysUntilTest * 0.8), 1);
        
        const relatedNotes = notes.filter((note) => note.subject === test.subject);
        const sessionsNeeded = Math.max(Math.ceil(relatedNotes.length / 2), studyDays);
        
        for (let i = 0; i < sessionsNeeded && i < daysUntilTest; i++) {
          const sessionDate = addDays(today, Math.floor((daysUntilTest / sessionsNeeded) * i));
          const sessionNotes = relatedNotes.slice(
            Math.floor((relatedNotes.length / sessionsNeeded) * i),
            Math.floor((relatedNotes.length / sessionsNeeded) * (i + 1))
          );

          const daysToTest = differenceInDays(test.date, sessionDate);
          
          // Calculate recommended study hours
          // Base: 30 minutes per note
          let baseHours = sessionNotes.length * 0.5;
          
          // Add topic complexity factor (30 minutes per topic)
          baseHours += test.topics.length * 0.5;
          
          // Urgency multiplier: closer to test = more intense sessions
          let urgencyMultiplier = 1;
          if (daysToTest <= 3) urgencyMultiplier = 1.5;
          else if (daysToTest <= 7) urgencyMultiplier = 1.25;
          
          const recommendedHours = Math.max(
            Math.round((baseHours * urgencyMultiplier) * 2) / 2, // Round to nearest 0.5
            0.5 // Minimum 30 minutes
          );

          timeline.push({
            date: sessionDate,
            subject: test.subject,
            topics: test.topics,
            notesCount: sessionNotes.length,
            daysUntilTest: daysToTest,
            recommendedHours,
          });
        }
      });

    return timeline.sort((a, b) => a.date.getTime() - b.date.getTime());
  };

  const timeline = generateTimeline();

  const getIntensityColor = (daysUntilTest: number) => {
    if (daysUntilTest <= 3) return "bg-destructive";
    if (daysUntilTest <= 7) return "bg-accent";
    return "bg-success";
  };

  if (tests.length === 0) {
    return (
      <Card className="shadow-md">
        <CardContent className="flex flex-col items-center justify-center py-16">
          <Clock className="w-16 h-16 text-muted-foreground mb-4" />
          <p className="text-xl font-semibold text-foreground mb-2">No study timeline yet</p>
          <p className="text-muted-foreground text-center">
            Add tests and notes to generate your personalized study schedule
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Study Timeline</h2>
        <p className="text-muted-foreground">
          Your personalized study schedule based on upcoming tests
        </p>
      </div>

      <Card className="shadow-md">
        <CardHeader>
          <CardTitle>Timeline Overview</CardTitle>
          <CardDescription>
            {timeline.length} study sessions planned across {tests.length} test(s)
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="relative">
        {/* Timeline vertical line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border" />
        
        <div className="space-y-8">
          {timeline.map((session, index) => (
            <div key={index} className="relative pl-20">
              {/* Timeline dot */}
              <div className="absolute left-6 top-6 z-10">
                <div className={`w-5 h-5 rounded-full ${getIntensityColor(session.daysUntilTest)} ring-4 ring-background`} />
              </div>
              
              {/* Content card */}
              <Card className="shadow-md hover:shadow-lg transition-all">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-primary" />
                        {session.subject}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Calendar className="w-4 h-4" />
                        {format(session.date, "EEEE, MMMM dd, yyyy")}
                      </CardDescription>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <Badge variant="outline">{session.daysUntilTest} days until test</Badge>
                      <div className="flex items-center gap-1 text-sm font-semibold text-primary">
                        <Clock className="w-4 h-4" />
                        {session.recommendedHours}h recommended
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {session.notesCount > 0 && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <BookOpen className="w-4 h-4" />
                        Review {session.notesCount} note{session.notesCount !== 1 ? "s" : ""}
                      </div>
                    )}
                    {session.topics.length > 0 && (
                      <div>
                        <p className="text-sm font-semibold text-foreground mb-2">Focus areas:</p>
                        <div className="flex flex-wrap gap-2">
                          {session.topics.map((topic, idx) => (
                            <Badge key={idx} variant="secondary">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* AI Study Recommendations */}
                    <div className="border-t pt-4 mt-4">
                      <div className="flex items-center justify-between mb-3">
                        <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-primary" />
                          AI Study Recommendations
                        </p>
                        {!recommendations[session.subject] && (
                          <Button
                            size="sm"
                            onClick={() => generateRecommendations(session.subject)}
                            disabled={loadingSubject === session.subject}
                            className="gap-2"
                          >
                            {loadingSubject === session.subject ? (
                              <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Generating...
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-4 h-4" />
                                Generate
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                      
                      {recommendations[session.subject] ? (
                        <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                          <div className="text-sm text-foreground whitespace-pre-wrap">
                            {recommendations[session.subject]}
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-muted-foreground italic">
                          Click "Generate" to get AI-powered study recommendations based on your notes
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>

      {timeline.length === 0 && (
        <Card className="shadow-md bg-muted/50">
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              No study sessions scheduled. Add notes related to your test subjects to generate a timeline.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TimelineView;
