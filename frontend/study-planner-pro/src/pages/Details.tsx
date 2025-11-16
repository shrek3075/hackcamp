import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, CalendarIcon, Loader2, LogOut } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import * as pdfjsLib from 'pdfjs-dist';
import { User, Session } from '@supabase/supabase-js';

const Details = () => {
  const navigate = useNavigate();
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [testDate, setTestDate] = useState<Date>();
  const [studyHours, setStudyHours] = useState("");
  const [busyDays, setBusyDays] = useState<string[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
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

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out successfully");
    navigate("/auth");
  };

  const subjects = [
    "Mathematics",
    "Chemistry",
    "Physics",
    "Biology",
    "English",
    "History",
    "Geography",
    "Computer Science",
    "Economics",
    "Psychology"
  ];

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  const toggleDay = (day: string) => {
    setBusyDays(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newFiles = Array.from(files);
      setUploadedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleGeneratePlan = async () => {
    if (!subject || !testDate || !studyHours || uploadedFiles.length === 0) {
      toast.error("Please fill in all fields and upload at least one document");
      return;
    }

    if (!topic.trim()) {
      toast.error("Please enter a topic/unit name");
      return;
    }

    setIsGenerating(true);

    try {
      // Set up PDF.js worker using local package
      pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
        'pdfjs-dist/build/pdf.worker.min.mjs',
        import.meta.url
      ).toString();

      // Read file contents
      const fileContents = await Promise.all(
        uploadedFiles.map(async (file) => {
          if (file.type === 'application/pdf') {
            // Handle PDF files
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
            let fullText = '';
            
            // Extract text from each page (limit to first 50 pages to avoid token limits)
            const numPages = Math.min(pdf.numPages, 50);
            for (let i = 1; i <= numPages; i++) {
              const page = await pdf.getPage(i);
              const textContent = await page.getTextContent();
              const pageText = textContent.items.map((item: any) => item.str).join(' ');
              fullText += pageText + '\n';
            }
            
            if (pdf.numPages > 50) {
              console.log(`PDF ${file.name}: Only first 50 pages processed (total: ${pdf.numPages})`);
            }
            
            return fullText.slice(0, 100000); // Limit to 100k chars
          } else {
            // Handle text files
            return new Promise<string>((resolve) => {
              const reader = new FileReader();
              reader.onload = (e) => {
                const content = e.target?.result as string || '';
                const truncated = content.slice(0, 100000);
                if (content.length > 100000) {
                  console.log(`File ${file.name} truncated from ${content.length} to 100,000 characters`);
                }
                resolve(truncated);
              };
              reader.readAsText(file);
            });
          }
        })
      );

      const syllabusContent = fileContents.join('\n\n');

      // Prepare plan details
      const planDetails = {
        subject,
        testDate: format(testDate, "yyyy-MM-dd"),
        startDate: format(new Date(), "yyyy-MM-dd"), // Today's date
        busyDays,
        totalStudyHours: studyHours,
        syllabusContent
      };

      toast.loading("Generating your personalized study plan...");

      // Call the edge function to generate the plan
      const { data, error: functionError } = await supabase.functions.invoke('generate-study-plan', {
        body: planDetails
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
        setIsGenerating(false);
        return;
      }

      // Save both details and generated plan to localStorage for immediate use
      localStorage.setItem('studyPlanDetails', JSON.stringify({
        ...planDetails,
        timestamp: Date.now()
      }));
      localStorage.setItem('generatedStudyPlan', JSON.stringify(data.studyPlan));

      // Save to database for history
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { error: dbError } = await supabase
          .from('study_plans')
          .insert([{
            user_id: user.id,
            subject,
            topic: topic.trim(),
            test_date: format(testDate, "yyyy-MM-dd"),
            total_study_hours: parseInt(studyHours),
            busy_days: busyDays,
            syllabus_content: syllabusContent,
            plan_data: data.studyPlan
          }]);

        if (dbError) {
          console.error("Error saving to database:", dbError);
          toast.error("Plan generated but failed to save to history");
        } else {
          toast.success("Study plan generated and saved!");
        }
      }
      
      // Navigate to home page to see active plans
      navigate('/');
    } catch (error) {
      console.error("Error generating plan:", error);
      const errorMsg = error instanceof Error ? error.message : "Failed to generate study plan";
      toast.error(errorMsg);
    } finally {
      setIsGenerating(false);
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

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12 max-w-3xl">
        <div className="flex items-start justify-between mb-8">
          <div className="flex-1 space-y-6">
            {/* Subject Dropdown */}
            <Select value={subject} onValueChange={setSubject}>
              <SelectTrigger className="h-14 text-base bg-white/90 border-none rounded-2xl shadow-sm">
                <SelectValue placeholder="Select subject" />
              </SelectTrigger>
              <SelectContent className="bg-white z-50">
                {subjects.map((subj) => (
                  <SelectItem key={subj} value={subj}>
                    {subj}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Topic/Unit Input */}
            <Input
              placeholder="Enter topic/unit (e.g., Thermodynamics, Unit 3)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="h-14 text-base bg-white/90 border-none rounded-2xl shadow-sm"
            />

            {/* Test Date Picker */}
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "h-14 w-full text-base bg-white/90 border-none rounded-2xl shadow-sm justify-start text-left font-normal",
                    !testDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-5 w-5" />
                  {testDate ? format(testDate, "dd/MM/yyyy") : "Select date of test"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0 bg-white z-50" align="start">
                <Calendar
                  mode="single"
                  selected={testDate}
                  onSelect={setTestDate}
                  initialFocus
                  className={cn("p-3 pointer-events-auto")}
                  disabled={(date) => date < new Date()}
                />
              </PopoverContent>
            </Popover>

            {/* Busy Days Section */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-[#3d2817] text-center">
                What days are you busy
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {days.map((day) => (
                  <Button
                    key={day}
                    type="button"
                    onClick={() => toggleDay(day)}
                    variant={busyDays.includes(day) ? "default" : "outline"}
                    className={`h-12 text-sm ${
                      busyDays.includes(day)
                        ? "bg-[#5c4033] text-white hover:bg-[#4a3329]"
                        : "bg-white/90 text-[#5c4033] border-[#5c4033]/30 hover:bg-[#5c4033]/10"
                    }`}
                  >
                    {day}
                  </Button>
                ))}
              </div>
            </div>

            {/* Study Hours Input */}
            <Input
              type="text"
              placeholder="Total hours you want to study"
              value={studyHours}
              onChange={(e) => setStudyHours(e.target.value)}
              className="h-14 text-base bg-white/90 border-none rounded-2xl shadow-sm"
            />

            {/* Upload Documents Button */}
            <div className="space-y-3">
              <label htmlFor="file-upload">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full h-14 text-base bg-white/90 border-none rounded-2xl shadow-sm hover:bg-white/80 text-[#5c4033] cursor-pointer"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  <Upload className="mr-2 h-5 w-5" />
                  Click to upload documents
                </Button>
              </label>
              <input
                id="file-upload"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                onChange={handleFileUpload}
                className="hidden"
              />
              
              {/* Display uploaded files */}
              {uploadedFiles.length > 0 && (
                <div className="bg-white/90 rounded-2xl p-4 space-y-2">
                  <p className="text-sm font-semibold text-[#5c4033]">
                    Uploaded Files ({uploadedFiles.length}):
                  </p>
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-[#5c4033]/10 rounded-lg px-3 py-2">
                      <span className="text-sm text-[#5c4033] truncate flex-1">
                        {file.name}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="ml-2 text-red-600 hover:text-red-800"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Generate Study Plan Button */}
            <Button
              onClick={handleGeneratePlan}
              disabled={isGenerating}
              className="w-full h-16 text-xl font-semibold bg-white/90 text-[#3d2817] border-2 border-[#5c4033] rounded-2xl shadow-lg hover:bg-white/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-6 w-6 animate-spin" />
                  Generating Your Plan...
                </>
              ) : (
                "Generate Study Plan"
              )}
            </Button>
          </div>

          {/* Smart Planner Book Icon */}
          <div className="ml-8 flex-shrink-0">
            <div className="w-24 h-32 bg-[#5c4033] rounded-lg shadow-xl flex items-center justify-center">
              <div className="text-white text-center px-2">
                <p className="text-sm font-semibold leading-tight">Smart</p>
                <p className="text-sm font-semibold leading-tight">planner</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Details;
