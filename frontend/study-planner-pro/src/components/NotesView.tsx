import { useState, useEffect } from "react";
import { Note } from "@/pages/Index";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Plus, Trash2, BookOpen, Upload, X, Trophy, Sparkles, Loader2, Edit } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface NotesViewProps {
  notes: Note[];
  onAddNote: (note: Omit<Note, "id" | "createdAt">) => void;
  onEditNote: (id: string, note: Omit<Note, "id" | "createdAt">) => void;
  onArchiveNote: (id: string) => void;
}

const NotesView = ({ notes, onAddNote, onEditNote, onArchiveNote }: NotesViewProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [subject, setSubject] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [recommendations, setRecommendations] = useState<Record<string, string>>({});
  const [loadingSubject, setLoadingSubject] = useState<string | null>(null);

  // Sync notes to localStorage whenever notes change (for quiz game access)
  useEffect(() => {
    if (notes.length > 0) {
      localStorage.setItem('notes', JSON.stringify(notes));
    }
  }, [notes]);

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

  const handleOpenEdit = (note: Note) => {
    setEditingNote(note);
    setSubject(note.subject);
    setTitle(note.title);
    setContent(note.content);
    setIsOpen(true);
  };

  const handleCloseDialog = () => {
    setIsOpen(false);
    setEditingNote(null);
    setSubject("");
    setTitle("");
    setContent("");
    setUploadedFiles([]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (subject && title && content) {
      const noteData = { subject, title, content };

      if (editingNote) {
        onEditNote(editingNote.id, noteData);
      } else {
        onAddNote(noteData);
      }

      handleCloseDialog();
    }
  };

  const generateRecommendations = async (subjectName: string) => {
    setLoadingSubject(subjectName);
    try {
      const subjectNotes = notes.filter(note => note.subject === subjectName);
      
      const { data, error } = await supabase.functions.invoke('generate-study-recommendations', {
        body: { notes: subjectNotes, subject: subjectName }
      });

      if (error) throw error;

      setRecommendations(prev => ({
        ...prev,
        [subjectName]: data.recommendations
      }));
      toast.success("AI recommendations generated!");
    } catch (error) {
      console.error('Error generating recommendations:', error);
      toast.error("Failed to generate recommendations");
    } finally {
      setLoadingSubject(null);
    }
  };

  const subjects = Array.from(new Set(notes.map((note) => note.subject)));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Study Notes</h2>
          <p className="text-muted-foreground">Organize your learning materials</p>
        </div>
        <div className="flex gap-3">
          <Link to="/game">
            <Button variant="outline" className="gap-2">
              <Trophy className="w-4 h-4" />
              Play Quiz Game
            </Button>
          </Link>
          <Dialog open={isOpen} onOpenChange={handleCloseDialog}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="w-4 h-4" />
                Add Note
              </Button>
            </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingNote ? "Edit Note" : "Create New Note"}</DialogTitle>
              <DialogDescription>
                {editingNote ? "Update your study note" : "Add a new study note to your collection"}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g., Mathematics, Biology"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Quadratic Equations"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="content">Content</Label>
                <Textarea
                  id="content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Write your notes here..."
                  rows={6}
                  required
                />
              </div>
              
              {/* File Upload Section */}
              <div className="space-y-2">
                <Label>Attach Documents</Label>
                <div className="space-y-3">
                  <label htmlFor="note-file-upload">
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full cursor-pointer"
                      onClick={() => document.getElementById('note-file-upload')?.click()}
                    >
                      <Upload className="mr-2 h-4 w-4" />
                      Upload files
                    </Button>
                  </label>
                  <input
                    id="note-file-upload"
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  
                  {/* Display uploaded files */}
                  {uploadedFiles.length > 0 && (
                    <div className="space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-secondary rounded-lg px-3 py-2">
                          <span className="text-sm truncate flex-1">
                            {file.name}
                          </span>
                          <button
                            type="button"
                            onClick={() => removeFile(index)}
                            className="ml-2 text-destructive hover:text-destructive/80"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              
              <Button type="submit" className="w-full">
                {editingNote ? "Save Changes" : "Create Note"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {subjects.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {subjects.map((subject) => (
            <Badge key={subject} variant="secondary">
              {subject} ({notes.filter((n) => n.subject === subject).length})
            </Badge>
          ))}
        </div>
      )}

      {notes.length === 0 ? (
        <Card className="shadow-md">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <BookOpen className="w-16 h-16 text-muted-foreground mb-4" />
            <p className="text-xl font-semibold text-foreground mb-2">No notes yet</p>
            <p className="text-muted-foreground text-center mb-6">
              Start adding your study materials to organize your learning
            </p>
            <Button onClick={() => setIsOpen(true)} className="gap-2">
              <Plus className="w-4 h-4" />
              Create First Note
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {subjects.map((subjectName) => (
            <Card key={subjectName} className="overflow-hidden">
              <CardHeader>
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-primary" />
                    <CardTitle>{subjectName}</CardTitle>
                    <Badge variant="secondary">
                      {notes.filter((note) => note.subject === subjectName).length} notes
                    </Badge>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => generateRecommendations(subjectName)}
                    disabled={loadingSubject === subjectName}
                    className="gap-2"
                  >
                    {loadingSubject === subjectName ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Get AI Recommendations
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {recommendations[subjectName] && (
                  <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 space-y-2">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-5 h-5 text-primary" />
                      <h4 className="font-semibold text-foreground">AI Study Recommendations</h4>
                    </div>
                    <div className="text-sm text-foreground whitespace-pre-wrap">
                      {recommendations[subjectName]}
                    </div>
                  </div>
                )}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {notes
                    .filter((note) => note.subject === subjectName)
                    .map((note) => (
                      <Card key={note.id} className="shadow-md hover:shadow-lg transition-all">
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <CardTitle className="text-lg">{note.title}</CardTitle>
                            </div>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleOpenEdit(note)}
                                className="text-primary hover:text-primary hover:bg-primary/10"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => onArchiveNote(note.id)}
                                className="text-destructive hover:text-destructive hover:bg-destructive/10"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground line-clamp-4 mb-3">{note.content}</p>
                          <p className="text-xs text-muted-foreground">
                            {format(note.createdAt, "MMM dd, yyyy")}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotesView;
