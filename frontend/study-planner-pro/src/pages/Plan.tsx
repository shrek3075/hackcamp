import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, Clock, BookOpen, Loader2, AlertCircle, LogOut, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { format } from "date-fns";
import { User, Session } from "@supabase/supabase-js";

interface StudySession {
  topic: string;
  duration: number;
  description: string;
  priority: "high" | "medium" | "low";
  completed?: boolean;
  suggestedTime?: string;
}

interface DailyPlan {
  day: number;
  date: string;
  dayOfWeek?: string;
  totalStudyHours?: number;
  studyHours?: number;
  sessions?: StudySession[];
  topics?: string[];
  goals: string;
  freeTimeSlots?: string[];
}

interface StudyPlan {
  totalDays: number;
  totalHours?: number;
  dailyPlans: DailyPlan[];
  summary: string;
  rawPlan?: string;
}

interface PlanDetails {
  subject: string;
  testDate: string;
  busyDays: string[];
  dailyStudyHours: string;
  syllabusContent: string;
  timestamp: number;
}

type OpenPlan = { id: string; details: PlanDetails; studyPlan: StudyPlan };

const Plan = () => {
  const navigate = useNavigate();

  // MULTI-PLAN STATE
  const [openPlans, setOpenPlans] = useState<OpenPlan[]>([]);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const currentPlan = openPlans.find((p) => p.id === activePlanId) ?? openPlans[0] ?? null;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    // Set up auth state listener
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      setSession(session);
      setUser(session?.user ?? null);

      if (!session?.user) {
        setTimeout(() => {
          navigate("/auth");
        }, 0);
      }
    });

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

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  useEffect(() => {
    if (user) {
      loadActivePlans();
    } else {
      // clear plans if user logs out
      setOpenPlans([]);
      setActivePlanId(null);
    }
  }, [user]);

  // FETCH ALL ACTIVE PLANS (no limit)
  const loadActivePlans = async () => {
    setLoading(true);
    setError(null);

    try {
      const today = new Date().toISOString().split("T")[0];
      const { data: plans, error: fetchError } = await supabase
        .from("study_plans")
        .select("*")
        .eq("completed", false)
        .gte("test_date", today)
        .order("created_at", { ascending: false });

      if (fetchError) throw fetchError;

      if (plans && plans.length > 0) {
        const mapped: OpenPlan[] = plans.map((plan: any) => ({
          id: plan.id,
          studyPlan: plan.plan_data as StudyPlan,
          details: {
            subject: plan.subject,
            testDate: plan.test_date,
            busyDays: plan.busy_days || [],
            dailyStudyHours: String(plan.total_study_hours ?? ""),
            syllabusContent: plan.syllabus_content || "",
            timestamp: new Date(plan.created_at).getTime(),
          },
        }));
        setOpenPlans(mapped);
        setActivePlanId((prev) => prev ?? mapped[0].id);
      } else {
        setOpenPlans([]);
        setActivePlanId(null);
        setError("No active study plans found. Create one from the Details page.");
      }
    } catch (err) {
      console.error("Error loading plans:", err);
      setError("Failed to load study plans");
    } finally {
      setLoading(false);
    }
  };

  // GENERATE A NEW PLAN (invokes function and inserts into openPlans)
  const generatePlan = async (details: PlanDetails) => {
    setLoading(true);
    setError(null);

    try {
      const { data, error: functionError } = await supabase.functions.invoke("generate-study-plan", {
        body: details,
      });

      if (functionError) throw functionError;

      if (data?.error) {
        if (data.error.includes("Rate limits")) {
          toast.error("Too many requests. Please wait a moment and try again.");
        } else if (data.error.includes("Payment required")) {
          toast.error("AI usage limit reached. Please contact support.");
        } else {
          toast.error("Failed to generate study plan");
        }
        setError(data.error);
        return;
      }

      const newId =
        window.crypto && (window.crypto as any).randomUUID
          ? (window.crypto as any).randomUUID()
          : Math.random().toString(36).substr(2, 9);
      const newPlan: OpenPlan = {
        id: newId,
        studyPlan: data.studyPlan as StudyPlan,
        details: {
          subject: details.subject ?? "New Plan",
          testDate: details.testDate ?? new Date().toISOString().slice(0, 10),
          busyDays: details.busyDays ?? [],
          dailyStudyHours: String(data.studyPlan?.totalHours ?? details.dailyStudyHours ?? ""),
          syllabusContent: details.syllabusContent ?? "",
          timestamp: Date.now(),
        },
      };

      // add to top
      setOpenPlans((prev) => [newPlan, ...prev]);
      setActivePlanId((prev) => prev ?? newPlan.id);

      // optionally save locally for quick reloads
      localStorage.setItem("generatedStudyPlan", JSON.stringify(data.studyPlan));
      toast.success("Study plan generated successfully!");
    } catch (err: any) {
      console.error("Error generating plan:", err);
      const errorMsg = err instanceof Error ? err.message : "Failed to generate study plan";
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // RELOAD PLANS
  const handleRegenerate = async () => {
    await loadActivePlans();
  };

  // TOGGLE A SESSION (updates only the active plan and persists by id)
  const handleToggleSession = async (dayIndex: number, sessionIndex: number) => {
    if (!activePlanId || !user) return;

    const idx = openPlans.findIndex((p) => p.id === activePlanId);
    if (idx === -1) return;

    const copy = [...openPlans];
    const updatedPlan = { ...copy[idx].studyPlan };
    const sessionItem = updatedPlan.dailyPlans[dayIndex]?.sessions?.[sessionIndex];
    if (!sessionItem) return;

    const wasCompleted = sessionItem.completed;
    // toggle completion
    sessionItem.completed = !sessionItem.completed;

    // If marking as complete, save to topic_achievements (history)
    if (sessionItem.completed && !wasCompleted) {
      try {
        const { error: achievementError } = await supabase
          .from("topic_achievements")
          .insert({
            user_id: user.id,
            subject: copy[idx].details.subject,
            topic_name: sessionItem.topic,
            unit_topic: sessionItem.description,
            achieved: true,
          });

        if (achievementError) throw achievementError;
        toast.success("Session completed and added to history!");
      } catch (err) {
        console.error("Error saving achievement:", err);
        // Don't block the main flow if achievement save fails
      }
    }

    // ONLY reschedule if marking as incomplete AND it's a past day
    // Do NOT reschedule if marking as complete
    if (!sessionItem.completed && wasCompleted) {
      const sessionDate = new Date(updatedPlan.dailyPlans[dayIndex].date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (sessionDate < today) {
        const nextDayIndex = updatedPlan.dailyPlans.findIndex((day, idx2) => {
          const dayDate = new Date(day.date);
          return dayDate >= today && idx2 > dayIndex;
        });

        if (nextDayIndex !== -1) {
          // remove session from current day
          updatedPlan.dailyPlans[dayIndex].sessions =
            updatedPlan.dailyPlans[dayIndex].sessions?.filter((_, idx3) => idx3 !== sessionIndex) || [];
          updatedPlan.dailyPlans[dayIndex].totalStudyHours =
            (updatedPlan.dailyPlans[dayIndex].totalStudyHours || 0) - sessionItem.duration;

          // add to next day
          if (!updatedPlan.dailyPlans[nextDayIndex].sessions) updatedPlan.dailyPlans[nextDayIndex].sessions = [];
          updatedPlan.dailyPlans[nextDayIndex].sessions.push({ ...sessionItem, completed: false });
          updatedPlan.dailyPlans[nextDayIndex].totalStudyHours =
            (updatedPlan.dailyPlans[nextDayIndex].totalStudyHours || 0) + sessionItem.duration;

          toast.success("Task rescheduled to next available day");
        }
      }
    }

    // update local copy
    copy[idx] = { ...copy[idx], studyPlan: updatedPlan };
    setOpenPlans(copy);

    // persist change to DB by id
    try {
      const { error: updateError } = await supabase
        .from("study_plans")
        .update({ plan_data: updatedPlan as any })
        .eq("id", activePlanId);

      if (updateError) throw updateError;
    } catch (err) {
      console.error("Error updating plan:", err);
      toast.error("Failed to save changes");
    }
  };

  // Debug logging
  useEffect(() => {
    if (currentPlan?.studyPlan?.dailyPlans) {
      console.log("=== PLAN DEBUG INFO ===");
      console.log("First daily plan:", JSON.stringify(currentPlan.studyPlan.dailyPlans[0], null, 2));
      if (currentPlan.studyPlan.dailyPlans[0]?.sessions?.[0]) {
        console.log("First session:", currentPlan.studyPlan.dailyPlans[0].sessions[0]);
      }
      console.log("======================");
    }
  }, [currentPlan]);

  return (
    <div className="min-h-screen bg-[#d4b896]">
      {/* Navigation Bar */}
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">
            Home
          </Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">
            Details
          </Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">
            Plan
          </Link>
          <Link to="/mindmap" className="hover:opacity-80 transition-opacity">
            Mindmap
          </Link>
          <Link to="/progress" className="hover:opacity-80 transition-opacity">
            Progress
          </Link>
          <Link to="/ai-tutor" className="hover:opacity-80 transition-opacity">
            AI Tutor
          </Link>
          <Link to="/history" className="hover:opacity-80 transition-opacity">
            History
          </Link>
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

      <div className="container mx-auto px-4 py-12 max-w-6xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-[#3d2817] mb-2">Study Plan</h1>
            <p className="text-[#5c4033]">Your personalized day-by-day study timeline</p>
          </div>
          {currentPlan?.details && (
            <div className="flex gap-3">
              <Link to="/details">
                <Button variant="outline">Edit Details</Button>
              </Link>
              <Button onClick={handleRegenerate} disabled={loading}>
                Regenerate Plan
              </Button>
            </div>
          )}
        </div>

        {/* Plan Switcher (only show if multiple plans) */}
        {openPlans.length > 1 && (
          <div className="mb-6 flex gap-3 items-center">
            <span className="text-sm text-muted-foreground">Open Plans:</span>
            <div className="flex gap-2 flex-wrap">
              {openPlans.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setActivePlanId(p.id)}
                  className={`px-3 py-1 rounded-full border ${
                    p.id === (currentPlan?.id ?? null)
                      ? "bg-[#5c4033] text-white border-[#5c4033]"
                      : "bg-white text-[#3d2817] border-gray-200"
                  }`}
                >
                  {p.details.subject} — {format(new Date(p.details.testDate), "MMM d")}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Content states */}
        {!currentPlan?.details ? (
          <Card className="bg-white/90">
            <CardContent className="p-12 text-center">
              <AlertCircle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-[#3d2817] mb-2">No Plan Details Found</h3>
              <p className="text-[#5c4033] mb-6">
                Please go to the Details page and enter your study information to generate a plan.
              </p>
              <Link to="/details">
                <Button>Go to Details</Button>
              </Link>
            </CardContent>
          </Card>
        ) : loading ? (
          <Card className="bg-white/90">
            <CardContent className="p-12 text-center">
              <Loader2 className="w-16 h-16 text-primary animate-spin mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-[#3d2817] mb-2">Generating Your Study Plan</h3>
              <p className="text-[#5c4033]">Analyzing your syllabus and creating a personalized timeline...</p>
            </CardContent>
          </Card>
        ) : error ? (
          <Card className="bg-white/90 border-destructive">
            <CardContent className="p-12 text-center">
              <AlertCircle className="w-16 h-16 text-destructive mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-destructive mb-2">Error</h3>
              <p className="text-[#5c4033] mb-6">{error}</p>
              <Button onClick={handleRegenerate}>Try Again</Button>
            </CardContent>
          </Card>
        ) : currentPlan?.studyPlan ? (
          <div className="space-y-6">
            {/* Summary Card */}
            {currentPlan.studyPlan.summary && (
              <Card className="bg-white/90">
                <CardHeader>
                  <CardTitle className="text-[#3d2817]">Plan Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm text-muted-foreground">Subject</p>
                        <p className="font-semibold text-[#3d2817]">{currentPlan.details.subject}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm text-muted-foreground">Total Days</p>
                        <p className="font-semibold text-[#3d2817]">{currentPlan.studyPlan.totalDays} days</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <BookOpen className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm text-muted-foreground">Total Hours</p>
                        <p className="font-semibold text-[#3d2817]">
                          {currentPlan.studyPlan.totalHours ||
                            currentPlan.studyPlan.totalDays * parseFloat(currentPlan.details.dailyStudyHours)}
                          h
                        </p>
                      </div>
                    </div>
                  </div>
                  <p className="text-[#5c4033]">{currentPlan.studyPlan.summary}</p>
                </CardContent>
              </Card>
            )}

            {/* Daily Plans Timeline */}
            {currentPlan.studyPlan.dailyPlans && currentPlan.studyPlan.dailyPlans.length > 0 ? (
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-[#5c4033] via-[#8b6f47] to-[#5c4033]" />

                <div className="space-y-8">
                  {currentPlan.studyPlan.dailyPlans.map((plan, index) => {
                    const isFirstDay = index === 0;
                    const isLastDay = index === currentPlan.studyPlan.dailyPlans.length - 1;

                    return (
                      <div key={index} className="relative pl-20">
                        {/* Timeline dot with animation */}
                        <div className="absolute left-6 top-8 z-10">
                          <div
                            className={`w-6 h-6 rounded-full ring-4 ring-[#d4b896] transition-all ${
                              isFirstDay ? "bg-green-500 animate-pulse" : isLastDay ? "bg-red-500" : "bg-[#5c4033]"
                            }`}
                          >
                            {isFirstDay && (
                              <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-2 h-2 bg-white rounded-full" />
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Day card with gradient */}
                        <Card className="bg-gradient-to-br from-white/95 to-white/90 hover:shadow-2xl transition-all duration-300 border-l-4 border-[#5c4033]">
                          <CardHeader className="pb-3">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-3">
                                  <Badge variant="secondary" className="text-base px-3 py-1 bg-[#5c4033] text-white">
                                    Day {plan.day}
                                  </Badge>
                                  <span className="text-sm font-semibold text-[#3d2817]">
                                    {format(new Date(plan.date), "EEEE MMMM d, yyyy")}
                                  </span>
                                </div>
                                <CardTitle className="text-xl text-[#3d28117] mb-2">{plan.goals}</CardTitle>
                                {plan.totalStudyHours && (
                                  <p className="text-sm text-[#5c4033]/60 mt-1">
                                    Total study time: {plan.totalStudyHours}h
                                  </p>
                                )}
                              </div>
                              <div className="flex flex-col items-end gap-1">
                                {isFirstDay && (
                                  <Badge variant="outline" className="text-xs border-green-500 text-green-700">
                                    Start Here
                                  </Badge>
                                )}
                                {isLastDay && (
                                  <Badge variant="outline" className="text-xs border-red-500 text-red-700">
                                    Test Day Soon
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            {/* Free Time Slots Display */}
                            {plan.freeTimeSlots && plan.freeTimeSlots.length > 0 && (
                              <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded-lg mb-4">
                                <div className="flex items-start gap-2">
                                  <Clock className="w-4 h-4 text-blue-600 mt-0.5" />
                                  <div className="flex-1">
                                    <p className="text-sm font-semibold text-blue-900 mb-1">Available Study Times:</p>
                                    <div className="flex flex-wrap gap-2">
                                      {plan.freeTimeSlots.map((slot, idx) => (
                                        <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded font-medium">
                                          {slot}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Warning when no calendar data */}
                            {(!plan.freeTimeSlots || plan.freeTimeSlots.length === 0) &&
                             plan.sessions && !plan.sessions.some(s => s.suggestedTime) && (
                              <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border-l-4 border-orange-400 p-4 rounded-lg mb-4 shadow-sm">
                                <div className="flex items-start gap-3">
                                  <Clock className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />
                                  <div className="flex-1">
                                    <p className="text-sm font-bold text-orange-900 mb-2">⏰ Want Smart Time Scheduling?</p>
                                    <p className="text-xs text-orange-800 mb-3">
                                      This plan was created without calendar integration. To get specific study times:
                                    </p>
                                    <ol className="text-xs text-orange-800 space-y-1 ml-4 list-decimal">
                                      <li>Go to <strong>Details</strong> page</li>
                                      <li>Upload your <strong>.ics calendar file</strong> (optional)</li>
                                      <li>Set your <strong>study time window</strong> (e.g., 3:15 PM - 10:00 PM)</li>
                                      <li>Click <strong>Generate Study Plan</strong></li>
                                    </ol>
                                    <div className="mt-3 pt-3 border-t border-orange-200">
                                      <p className="text-xs text-orange-700 italic">
                                        ✨ You'll get exact time slots with 15-min buffers around your calendar events!
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Study Sessions */}
                            {plan.sessions && plan.sessions.length > 0 ? (
                              <div className="space-y-3">
                                {plan.sessions.map((session, sessionIdx) => {
                                  const priorityColors = {
                                    high: "border-l-red-500 bg-red-50",
                                    medium: "border-l-yellow-500 bg-yellow-50",
                                    low: "border-l-blue-500 bg-blue-50",
                                  };

                                  const priorityLabels = {
                                    high: "High Priority",
                                    medium: "Medium Priority",
                                    low: "Low Priority",
                                  };

                                  return (
                                    <div
                                      key={sessionIdx}
                                      className={`p-4 rounded-lg border-l-4 ${priorityColors[session.priority] || "border-l-gray-500 bg-gray-50"} ${session.completed ? "opacity-60" : ""} transition-all hover:shadow-md`}
                                    >
                                      <div className="flex items-start gap-3 mb-2">
                                        <Checkbox
                                          checked={session.completed || false}
                                          onCheckedChange={() => handleToggleSession(index, sessionIdx)}
                                          className="mt-1"
                                        />
                                        <div className="flex items-start justify-between gap-3 flex-1">
                                          <div className="flex-1">
                                            <h4
                                              className={`font-semibold text-[#3d2817] text-base mb-1 ${session.completed ? "line-through" : ""}`}
                                            >
                                              {session.topic}
                                            </h4>
                                            <p className="text-sm text-[#5c4033]/80 mb-2">{session.description}</p>
                                            <div className="flex items-center gap-2 flex-wrap">
                                              {session.suggestedTime && (
                                                <div className="flex items-center gap-1.5 bg-gradient-to-r from-green-50 to-emerald-50 text-green-900 px-3 py-1.5 rounded-lg border border-green-200 font-semibold text-sm">
                                                  <Clock className="w-4 h-4" />
                                                  <span>{session.suggestedTime}</span>
                                                </div>
                                              )}
                                              <div className="flex items-center gap-1 text-xs text-[#5c4033]/70 bg-gray-50 px-2 py-1 rounded">
                                                <span>{session.duration}h</span>
                                              </div>
                                            </div>
                                          </div>
                                          <div className="flex flex-col items-end gap-1">
                                            {session.priority && (
                                              <Badge
                                                variant="outline"
                                                className={`text-xs ${
                                                  session.priority === "high"
                                                    ? "border-red-500 text-red-700"
                                                    : session.priority === "medium"
                                                      ? "border-yellow-600 text-yellow-700"
                                                      : "border-blue-500 text-blue-700"
                                                }`}
                                              >
                                                {priorityLabels[session.priority]}
                                              </Badge>
                                            )}
                                            {session.completed && (
                                              <Badge
                                                variant="outline"
                                                className="text-xs border-green-500 text-green-700 bg-green-50"
                                              >
                                                <CheckCircle className="w-3 h-3 mr-1" />
                                                Done
                                              </Badge>
                                            )}
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            ) : plan.topics && plan.topics.length > 0 ? (
                              // Fallback for old format
                              <div>
                                <p className="text-sm font-semibold text-[#5c4033] mb-2">Topics to Cover:</p>
                                <div className="flex flex-wrap gap-2">
                                  {plan.topics.map((topic, idx) => (
                                    <Badge key={idx} variant="outline" className="bg-white">
                                      {topic}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            ) : null}
                          </CardContent>
                        </Card>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : currentPlan.studyPlan.rawPlan ? (
              <Card className="bg-white/90">
                <CardHeader>
                  <CardTitle className="text-[#3d2817]">Study Plan</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="whitespace-pre-wrap text-[#5c4033]">{currentPlan.studyPlan.rawPlan}</div>
                </CardContent>
              </Card>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default Plan;
