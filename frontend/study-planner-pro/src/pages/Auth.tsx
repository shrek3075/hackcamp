import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { User, Session } from '@supabase/supabase-js';

const Auth = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [isBookOpen, setIsBookOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    // Set up auth state listener FIRST
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        
        if (session?.user) {
          setTimeout(() => {
            navigate("/");
          }, 0);
        }
      }
    );

    // THEN check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        navigate("/");
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsBookOpen(true);
    setLoading(true);

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        if (error) throw error;
        toast.success("Logged in successfully!");
      } else {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/`
          }
        });
        
        if (error) throw error;
        toast.success("Account created! You can now log in.");
        setIsLogin(true);
      }
    } catch (error: any) {
      console.error("Auth error:", error);
      toast.error(error.message || "Authentication failed");
      setIsBookOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/30 to-accent/20 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center mb-6" style={{ perspective: '1200px' }}>
            <div className="relative w-48 h-32">
              {/* Book Container */}
              <div className="absolute inset-0 flex items-center justify-center">
                
                {/* Back Cover (Left side - only visible when open) */}
                <div 
                  className="absolute w-24 h-32 bg-card border-2 border-border rounded-l-lg overflow-hidden transition-all duration-700"
                  style={{
                    right: '50%',
                    opacity: isBookOpen ? 1 : 0,
                    transform: isBookOpen ? 'translateX(0)' : 'translateX(20px)',
                    boxShadow: 'inset 0 0 20px rgba(0,0,0,0.1), -4px 4px 12px rgba(0,0,0,0.2)',
                    zIndex: 5
                  }}
                >
                  {/* Page lines on left */}
                  <div className="absolute inset-0 p-3 space-y-2">
                    {[...Array(8)].map((_, i) => (
                      <div 
                        key={`left-${i}`}
                        className="h-px bg-muted-foreground/20 rounded"
                        style={{ width: `${85 - i * 3}%` }}
                      ></div>
                    ))}
                  </div>
                </div>

                {/* Book Spine (only visible when open) */}
                <div 
                  className="absolute w-2 h-32 rounded-sm transition-opacity duration-300"
                  style={{
                    left: '50%',
                    marginLeft: '-1px',
                    background: 'linear-gradient(to right, hsl(var(--primary) / 0.8), hsl(var(--primary)))',
                    boxShadow: 'inset 0 0 8px rgba(0,0,0,0.4)',
                    opacity: isBookOpen ? 1 : 0,
                    zIndex: 10
                  }}
                ></div>

                {/* Right Page (visible when open) */}
                <div 
                  className="absolute w-24 h-32 bg-card border-2 border-border rounded-r-lg overflow-hidden transition-all duration-700"
                  style={{
                    left: '50%',
                    opacity: isBookOpen ? 1 : 0,
                    transform: isBookOpen ? 'translateX(0)' : 'translateX(-20px)',
                    boxShadow: 'inset 0 0 20px rgba(0,0,0,0.1), 4px 4px 12px rgba(0,0,0,0.2)',
                    zIndex: 5
                  }}
                >
                  {/* Page lines on right */}
                  <div className="absolute inset-0 p-3 space-y-2">
                    {[...Array(8)].map((_, i) => (
                      <div 
                        key={`right-${i}`}
                        className="h-px bg-muted-foreground/20 rounded"
                        style={{ width: `${85 - i * 3}%` }}
                      ></div>
                    ))}
                  </div>
                </div>

                {/* Front Cover (Animated - starts closed) */}
                <div 
                  className="absolute w-24 h-32 rounded-lg border-2 border-border overflow-hidden transition-all duration-700 ease-in-out"
                  style={{
                    left: '50%',
                    marginLeft: '-48px',
                    transformOrigin: 'right center',
                    transformStyle: 'preserve-3d',
                    transform: isBookOpen ? 'rotateY(-180deg)' : 'rotateY(0deg)',
                    background: 'linear-gradient(to right, hsl(var(--primary)), hsl(var(--accent)))',
                    boxShadow: isBookOpen 
                      ? '-8px 4px 16px rgba(0,0,0,0.4), inset 4px 0 8px rgba(0,0,0,0.2)'
                      : '4px 4px 12px rgba(0,0,0,0.3), inset 4px 0 8px rgba(0,0,0,0.2)',
                    zIndex: isBookOpen ? 0 : 15,
                    opacity: isBookOpen ? 0 : 1,
                    transitionDelay: '100ms'
                  }}
                >
                  {/* Cover texture */}
                  <div className="absolute inset-0 opacity-20" style={{
                    backgroundImage: 'repeating-linear-gradient(-45deg, transparent, transparent 3px, rgba(0,0,0,0.1) 3px, rgba(0,0,0,0.1) 6px)'
                  }}></div>
                  {/* Cover decoration */}
                  <div className="absolute inset-3 border border-primary-foreground/30 rounded"></div>
                  {/* Star icon */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                    <svg viewBox="0 0 24 24" fill="hsl(var(--primary-foreground))" className="w-6 h-6 opacity-70">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                  </div>
                </div>
              </div>

              {/* Book shadow */}
              <div 
                className="absolute -bottom-2 left-1/2 -translate-x-1/2 h-4 rounded-full blur-md transition-all duration-700"
                style={{
                  width: isBookOpen ? '160px' : '100px',
                  background: 'radial-gradient(ellipse, rgba(0,0,0,0.3) 0%, transparent 70%)',
                  opacity: isBookOpen ? 0.5 : 0.7
                }}
              ></div>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Smart Planner</h1>
          <p className="text-muted-foreground">
            {isLogin ? "Welcome back! Sign in to continue" : "Create an account to get started"}
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-card rounded-3xl shadow-xl p-8 space-y-6 border-2 border-border/50">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-foreground mb-2">
              {isLogin ? "Log in" : "Sign up"}
            </h2>
            <p className="text-muted-foreground">
              {isLogin ? "Enter your details to continue" : "Create your account"}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="email"
                placeholder="email@domain.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-14 text-base rounded-2xl border-2 focus:border-primary"
                required
              />
            </div>
            <div>
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-14 text-base rounded-2xl border-2 focus:border-primary"
                required
              />
            </div>
            <Button
              type="submit"
              className="w-full h-14 text-base font-bold rounded-2xl shadow-lg hover:shadow-xl transition-all"
              size="lg"
              disabled={loading}
            >
              {loading ? "Processing..." : isLogin ? "Continue" : "Sign up"}
            </Button>
          </form>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
            </span>
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-primary font-bold hover:underline"
            >
              {isLogin ? "Sign up" : "Log in"}
            </button>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Link to="/" className="text-muted-foreground hover:text-foreground text-sm">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Auth;
