import { Note, Test } from "@/pages/Index";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar, BookOpen, Clock, Trash2, Loader2, Trophy } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { format, differenceInDays } from "date-fns";
import { Link } from "react-router-dom";

interface StudyPlanRecord {
  id: string;
  subject: string;
  test_date: string;
  total_study_hours: number;
  created_at: string;
  plan_data: any;
}

interface DashboardViewProps {
  notes: Note[];
  tests: Test[];
  activePlans: StudyPlanRecord[];
  loadingPlans: boolean;
  onDeletePlan: (id: string) => void;
  onMarkAsAchieved: (id: string) => void;
}

const DashboardView = ({ notes, tests, activePlans, loadingPlans, onDeletePlan, onMarkAsAchieved }: DashboardViewProps) => {
  const upcomingTests = tests
    .sort((a, b) => a.date.getTime() - b.date.getTime())
    .slice(0, 3);

  const recentNotes = notes
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    .slice(0, 5);

  const getDaysUntil = (date: Date | string) => {
    const targetDate = typeof date === 'string' ? new Date(date) : date;
    const days = differenceInDays(targetDate, new Date());
    if (days === 0) return "Today";
    if (days === 1) return "Tomorrow";
    if (days < 0) return "Past";
    return `${days} days`;
  };

  const getUrgencyColor = (date: Date | string) => {
    const targetDate = typeof date === 'string' ? new Date(date) : date;
    const days = differenceInDays(targetDate, new Date());
    if (days <= 3) return "text-destructive";
    if (days <= 7) return "text-orange-500";
    return "text-success";
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Welcome back!</h2>
        <p className="text-muted-foreground">Here's your complete study overview</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="shadow-md hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <BookOpen className="w-5 h-5 text-primary" />
              Active Study Plans
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary">{activePlans.length}</p>
          </CardContent>
        </Card>

        <Card className="shadow-md hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <BookOpen className="w-5 h-5 text-accent" />
              Total Notes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-accent">{notes.length}</p>
          </CardContent>
        </Card>

        <Card className="shadow-md hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Calendar className="w-5 h-5 text-success" />
              Upcoming Tests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-success">{tests.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Active Study Plans Section */}
      <Card className="shadow-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Active Study Plans</CardTitle>
              <CardDescription>Your upcoming test preparations</CardDescription>
            </div>
            <Link to="/details">
              <Button size="sm">Create New Plan</Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {loadingPlans ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : activePlans.length === 0 ? (
            <div className="text-center py-8">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">No active study plans yet</p>
              <Link to="/details">
                <Button>Create Your First Plan</Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {activePlans.map((plan) => (
                <Card key={plan.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center justify-between">
                      <span className="truncate">{plan.subject}</span>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onDeletePlan(plan.id)}
                        className="hover:bg-destructive/10 hover:text-destructive"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span>Test: {format(new Date(plan.test_date), 'MMM d, yyyy')}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-muted-foreground" />
                      <span>{plan.total_study_hours} hours total</span>
                    </div>
                    <Badge className={getUrgencyColor(plan.test_date)}>
                      {getDaysUntil(plan.test_date)}
                    </Badge>
                    {plan.plan_data?.totalDays && (
                      <p className="text-sm text-muted-foreground">
                        {plan.plan_data.totalDays} day plan
                      </p>
                    )}
                    <div className="flex gap-2 mt-3">
                      <Link to={`/plan?planId=${plan.id}`} className="flex-1">
                        <Button className="w-full">
                          View Plan
                        </Button>
                      </Link>
                      <Button 
                        onClick={() => onMarkAsAchieved(plan.id)}
                        variant="outline"
                        className="flex-1"
                      >
                        <Trophy className="w-4 h-4 mr-2" />
                        Achieved
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Upcoming Tests</CardTitle>
            <CardDescription>Your next scheduled assessments</CardDescription>
          </CardHeader>
          <CardContent>
            {upcomingTests.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">No tests scheduled yet</p>
            ) : (
              <div className="space-y-4">
                {upcomingTests.map((test) => (
                  <div
                    key={test.id}
                    className="flex items-center justify-between p-4 bg-secondary rounded-lg hover:bg-secondary/80 transition-colors"
                  >
                    <div>
                      <p className="font-semibold text-foreground">{test.subject}</p>
                      <p className="text-sm text-muted-foreground">
                        {format(test.date, "MMM dd, yyyy")}
                      </p>
                    </div>
                    <Badge className={getUrgencyColor(test.date)}>
                      {getDaysUntil(test.date)}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Recent Notes</CardTitle>
            <CardDescription>Your latest study materials</CardDescription>
          </CardHeader>
          <CardContent>
            {recentNotes.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">No notes created yet</p>
            ) : (
              <div className="space-y-3">
                {recentNotes.map((note) => (
                  <div
                    key={note.id}
                    className="p-4 bg-secondary rounded-lg hover:bg-secondary/80 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-foreground">{note.title}</p>
                        <p className="text-sm text-muted-foreground">{note.subject}</p>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {format(note.createdAt, "MMM dd")}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardView;
