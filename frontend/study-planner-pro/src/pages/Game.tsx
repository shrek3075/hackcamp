import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Trophy, Star, Flame, ArrowLeft, Loader2, Check, X } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

interface Question {
  type: "multiple_choice" | "true_false" | "fill_blank";
  question: string;
  options?: string[];
  correctAnswer: number | boolean | string;
  explanation: string;
}

interface QuizData {
  questions: Question[];
}

const Game = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<any>(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [gameComplete, setGameComplete] = useState(false);

  useEffect(() => {
    loadQuiz();
  }, []);

  const loadQuiz = async () => {
    setLoading(true);
    try {
      // Get notes from localStorage (in a real app, fetch from database)
      const storedNotes = localStorage.getItem('notes');
      const notes = storedNotes ? JSON.parse(storedNotes) : [];

      if (notes.length === 0) {
        toast.error("No notes found. Please add some notes first!");
        navigate("/");
        return;
      }

      const { data, error } = await supabase.functions.invoke('generate-quiz', {
        body: { notes, difficulty: 'mixed' }
      });

      if (error) throw error;

      if (data?.error) {
        if (data.error.includes("Rate limits")) {
          toast.error("Too many requests. Please wait and try again.");
        } else if (data.error.includes("Payment required")) {
          toast.error("AI usage limit reached.");
        } else {
          toast.error("Failed to generate quiz");
        }
        navigate("/");
        return;
      }

      setQuizData(data);
    } catch (error) {
      console.error("Error loading quiz:", error);
      toast.error("Failed to load quiz");
      navigate("/");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (answer: any) => {
    if (showResult) return;
    
    setSelectedAnswer(answer);
    const question = quizData!.questions[currentQuestion];
    const correct = answer === question.correctAnswer;
    
    setIsCorrect(correct);
    setShowResult(true);

    if (correct) {
      setScore(score + 10);
      setStreak(streak + 1);
      toast.success("Correct! 🎉");
    } else {
      setStreak(0);
      toast.error("Not quite right");
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < quizData!.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      setGameComplete(true);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#d4b896] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-[#5c4033] mx-auto mb-4" />
          <p className="text-[#5c4033] text-lg">Generating your quiz...</p>
        </div>
      </div>
    );
  }

  if (gameComplete) {
    const totalQuestions = quizData!.questions.length;
    const percentage = Math.round((score / (totalQuestions * 10)) * 100);

    return (
      <div className="min-h-screen bg-[#d4b896]">
        <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
          <div className="flex gap-12">
            <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
            <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
            <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
            <Link to="/history" className="hover:opacity-80 transition-opacity">History</Link>
          </div>
          <Link to="/auth" className="hover:opacity-80 transition-opacity">Log Out</Link>
        </nav>

        <div className="container mx-auto px-4 py-12 max-w-2xl">
          <Card className="bg-white/90 shadow-2xl">
            <CardContent className="p-8 text-center">
              <Trophy className="w-20 h-20 text-yellow-500 mx-auto mb-4" />
              <h1 className="text-4xl font-bold text-[#3d2817] mb-2">Quiz Complete!</h1>
              <p className="text-2xl text-[#5c4033] mb-6">Your Score: {score}</p>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-center justify-between text-lg">
                  <span className="text-[#5c4033]">Accuracy</span>
                  <span className="font-bold text-[#3d2817]">{percentage}%</span>
                </div>
                <Progress value={percentage} className="h-3" />
                
                <div className="flex items-center justify-between text-lg">
                  <span className="text-[#5c4033] flex items-center gap-2">
                    <Flame className="w-5 h-5 text-orange-500" />
                    Best Streak
                  </span>
                  <span className="font-bold text-[#3d2817]">{streak}</span>
                </div>
              </div>

              <div className="flex gap-4">
                <Button
                  onClick={() => {
                    setCurrentQuestion(0);
                    setScore(0);
                    setStreak(0);
                    setGameComplete(false);
                    loadQuiz();
                  }}
                  className="flex-1 bg-[#5c4033] hover:bg-[#4a3329] text-white h-12"
                >
                  Play Again
                </Button>
                <Button
                  onClick={() => navigate("/")}
                  variant="outline"
                  className="flex-1 h-12"
                >
                  Back to Home
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!quizData) return null;

  const question = quizData.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quizData.questions.length) * 100;

  return (
    <div className="min-h-screen bg-[#d4b896]">
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
          <Link to="/history" className="hover:opacity-80 transition-opacity">History</Link>
        </div>
        <Link to="/auth" className="hover:opacity-80 transition-opacity">Log Out</Link>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="text-[#5c4033]"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Exit
          </Button>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-[#5c4033]">
              <Star className="w-6 h-6 text-yellow-500 fill-yellow-500" />
              <span className="text-xl font-bold">{score}</span>
            </div>
            <div className="flex items-center gap-2 text-[#5c4033]">
              <Flame className="w-6 h-6 text-orange-500" />
              <span className="text-xl font-bold">{streak}</span>
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-[#5c4033]">
              Question {currentQuestion + 1} of {quizData.questions.length}
            </span>
            <span className="text-sm text-[#5c4033] font-bold">{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-3" />
        </div>

        {/* Question Card */}
        <Card className="bg-white/90 shadow-xl mb-6">
          <CardContent className="p-8">
            <h2 className="text-2xl font-bold text-[#3d2817] mb-6">
              {question.question}
            </h2>

            {/* Multiple Choice */}
            {question.type === "multiple_choice" && (
              <div className="space-y-3">
                {question.options?.map((option, index) => (
                  <Button
                    key={index}
                    onClick={() => handleAnswer(index)}
                    disabled={showResult}
                    className={`w-full h-auto p-4 text-left justify-start text-base transition-all ${
                      showResult
                        ? index === question.correctAnswer
                          ? "bg-green-500 hover:bg-green-500 text-white"
                          : selectedAnswer === index
                          ? "bg-red-500 hover:bg-red-500 text-white"
                          : "bg-gray-100 text-gray-700"
                        : "bg-white hover:bg-[#5c4033]/10 text-[#5c4033] border-2 border-[#5c4033]/30"
                    }`}
                  >
                    {showResult && index === question.correctAnswer && (
                      <Check className="w-5 h-5 mr-2" />
                    )}
                    {showResult && selectedAnswer === index && index !== question.correctAnswer && (
                      <X className="w-5 h-5 mr-2" />
                    )}
                    {option}
                  </Button>
                ))}
              </div>
            )}

            {/* True/False */}
            {question.type === "true_false" && (
              <div className="grid grid-cols-2 gap-4">
                {[true, false].map((value) => (
                  <Button
                    key={value.toString()}
                    onClick={() => handleAnswer(value)}
                    disabled={showResult}
                    className={`h-20 text-xl transition-all ${
                      showResult
                        ? value === question.correctAnswer
                          ? "bg-green-500 hover:bg-green-500 text-white"
                          : selectedAnswer === value
                          ? "bg-red-500 hover:bg-red-500 text-white"
                          : "bg-gray-100 text-gray-700"
                        : "bg-white hover:bg-[#5c4033]/10 text-[#5c4033] border-2 border-[#5c4033]/30"
                    }`}
                  >
                    {value ? "True" : "False"}
                  </Button>
                ))}
              </div>
            )}

            {/* Fill in the Blank */}
            {question.type === "fill_blank" && (
              <div className="space-y-4">
                <input
                  type="text"
                  value={selectedAnswer || ""}
                  onChange={(e) => setSelectedAnswer(e.target.value)}
                  disabled={showResult}
                  placeholder="Type your answer..."
                  className="w-full p-4 text-lg border-2 border-[#5c4033]/30 rounded-lg focus:outline-none focus:border-[#5c4033]"
                />
                {!showResult && (
                  <Button
                    onClick={() => handleAnswer(selectedAnswer?.toLowerCase().trim())}
                    disabled={!selectedAnswer}
                    className="w-full bg-[#5c4033] hover:bg-[#4a3329] text-white h-12"
                  >
                    Submit Answer
                  </Button>
                )}
              </div>
            )}

            {/* Explanation */}
            {showResult && (
              <div className={`mt-6 p-4 rounded-lg ${isCorrect ? "bg-green-50" : "bg-red-50"}`}>
                <p className="text-sm font-semibold mb-2">
                  {isCorrect ? "✓ Correct!" : "✗ Incorrect"}
                </p>
                <p className="text-sm text-gray-700">{question.explanation}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Next Button */}
        {showResult && (
          <Button
            onClick={nextQuestion}
            className="w-full bg-[#5c4033] hover:bg-[#4a3329] text-white h-14 text-lg"
          >
            {currentQuestion < quizData.questions.length - 1 ? "Next Question" : "See Results"}
          </Button>
        )}
      </div>
    </div>
  );
};

export default Game;
