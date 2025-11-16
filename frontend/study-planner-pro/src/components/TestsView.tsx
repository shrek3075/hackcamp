import { useState } from "react";
import { Test } from "@/pages/Index";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Trash2, Calendar as CalendarIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { format, differenceInDays } from "date-fns";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface TestsViewProps {
  tests: Test[];
  onAddTest: (test: Omit<Test, "id">) => void;
  onDeleteTest: (id: string) => void;
}

const TestsView = ({ tests, onAddTest, onDeleteTest }: TestsViewProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [subject, setSubject] = useState("");
  const [date, setDate] = useState("");
  const [topics, setTopics] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (subject && date) {
      onAddTest({
        subject,
        date: new Date(date),
        topics: topics.split(",").map((t) => t.trim()).filter(Boolean),
      });
      setSubject("");
      setDate("");
      setTopics("");
      setIsOpen(false);
    }
  };

  const sortedTests = [...tests].sort((a, b) => a.date.getTime() - b.date.getTime());

  const getDaysUntil = (date: Date) => {
    const days = differenceInDays(date, new Date());
    if (days === 0) return "Today";
    if (days === 1) return "Tomorrow";
    if (days < 0) return `${Math.abs(days)} days ago`;
    return `${days} days`;
  };

  const getUrgencyColor = (date: Date) => {
    const days = differenceInDays(date, new Date());
    if (days <= 3) return "bg-destructive text-destructive-foreground";
    if (days <= 7) return "bg-orange-500 text-white";
    return "bg-success text-success-foreground";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Test Schedule</h2>
          <p className="text-muted-foreground">Track your upcoming assessments</p>
        </div>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              Add Test
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Schedule New Test</DialogTitle>
              <DialogDescription>Add an upcoming test to your calendar</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="test-subject">Subject</Label>
                <Input
                  id="test-subject"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g., Chemistry Midterm"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="test-date">Test Date</Label>
                <Input
                  id="test-date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="topics">Topics (comma-separated)</Label>
                <Input
                  id="topics"
                  value={topics}
                  onChange={(e) => setTopics(e.target.value)}
                  placeholder="e.g., Organic Chemistry, Acids and Bases"
                />
              </div>
              <Button type="submit" className="w-full">
                Schedule Test
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {tests.length === 0 ? (
        <Card className="shadow-md">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <CalendarIcon className="w-16 h-16 text-muted-foreground mb-4" />
            <p className="text-xl font-semibold text-foreground mb-2">No tests scheduled</p>
            <p className="text-muted-foreground text-center mb-6">
              Add your upcoming tests to create a study timeline
            </p>
            <Button onClick={() => setIsOpen(true)} className="gap-2">
              <Plus className="w-4 h-4" />
              Schedule First Test
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {sortedTests.map((test) => (
            <Card key={test.id} className="shadow-md hover:shadow-lg transition-all">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl">{test.subject}</CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <CalendarIcon className="w-4 h-4" />
                      {format(test.date, "EEEE, MMMM dd, yyyy")}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getUrgencyColor(test.date)}>{getDaysUntil(test.date)}</Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onDeleteTest(test.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              {test.topics.length > 0 && (
                <CardContent>
                  <p className="text-sm font-semibold text-foreground mb-2">Topics to cover:</p>
                  <div className="flex flex-wrap gap-2">
                    {test.topics.map((topic, index) => (
                      <Badge key={index} variant="secondary">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestsView;
