import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { notes, difficulty } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    if (!notes || notes.length === 0) {
      throw new Error("No notes provided");
    }

    const notesContext = notes
      .map((note: any) => `Title: ${note.title}\nContent: ${note.content}`)
      .join('\n\n');

    const systemPrompt = `You are a quiz generator. Create engaging, educational quiz questions STRICTLY BASED ON THE PROVIDED STUDY NOTES.

CRITICAL RULES:
- You MUST generate questions based ONLY on the content from the study notes provided by the user
- DO NOT create generic questions or questions about topics not covered in the notes
- Extract specific facts, concepts, and information directly from the notes content
- Questions should reference the exact topics, terms, and details mentioned in the notes

Generate EXACTLY 5 quiz questions with the following structure:
- Mix of multiple choice (3-4 options), true/false, and fill-in-the-blank questions
- Questions should test understanding of the NOTE CONTENT, not just memorization
- Include clear, concise explanations that reference the notes
- Vary difficulty from easy to challenging

Return ONLY valid JSON in this EXACT format:
{
  "questions": [
    {
      "type": "multiple_choice",
      "question": "What is...?",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": 0,
      "explanation": "The correct answer is A because..."
    },
    {
      "type": "true_false",
      "question": "True or False: ...",
      "correctAnswer": true,
      "explanation": "This is true because..."
    },
    {
      "type": "fill_blank",
      "question": "Complete: The _____ is important.",
      "correctAnswer": "answer",
      "explanation": "The answer is 'answer' because..."
    }
  ]
}`;

    const userPrompt = `Create 5 quiz questions (${difficulty || 'mixed'} difficulty) based STRICTLY on the following study notes.

IMPORTANT: Generate questions that directly test knowledge of the specific information contained in these notes. Use facts, concepts, definitions, and details from the notes.

Study Notes:
${notesContext}

Return ONLY the JSON object, no additional text.`;

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(JSON.stringify({ error: "Rate limits exceeded, please try again later." }), {
          status: 429,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (response.status === 402) {
        return new Response(JSON.stringify({ error: "Payment required, please add funds to your workspace." }), {
          status: 402,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      const errorText = await response.text();
      console.error("AI gateway error:", response.status, errorText);
      return new Response(JSON.stringify({ error: "AI gateway error" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await response.json();
    let content = data.choices?.[0]?.message?.content || "{}";
    
    // Clean up the response - remove markdown code blocks if present
    content = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    
    console.log("AI Response:", content);
    
    const quizData = JSON.parse(content);

    return new Response(
      JSON.stringify(quizData),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error in generate-quiz:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
